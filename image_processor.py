import hashlib
import io
import os
import random
import re
import string
import time
import uuid

from PIL import Image, ImageOps
from PySide6.QtCore import QObject

from app.enums.image_format import ImageFormat
from app.enums.rename_image_method import RenameImageMethod
from app.modules.load_image_path_from_folder import load_image_path_from_folder


def find_field_by_value(enum, value):
    for item in enum:
        if item.value == value:
            return item.name
    return None


def convert_mode_for_format(image, image_format, alpha_to_white=True):
    """把图片转换为目标格式支持的色彩模式，避免 RGBA/P/CMYK 等模式保存时失败。

    alpha_to_white: 转 JPEG 时，True 表示把透明区域合成到白色背景，False 表示合成到黑色背景。
    """
    format_name = image_format.upper()

    if format_name in ('JPEG', 'MPO'):
        if image.mode in ('RGB', 'L', 'CMYK'):
            return image

        # 带透明通道的图片先合成到纯色背景，避免透明区域变黑
        if image.mode in ('RGBA', 'LA', 'PA') or (image.mode == 'P' and 'transparency' in image.info):
            rgba_image = image.convert('RGBA')
            background_color = (255, 255, 255) if alpha_to_white else (0, 0, 0)
            background = Image.new('RGB', rgba_image.size, background_color)
            background.paste(rgba_image, mask=rgba_image.getchannel('A'))
            return background

        return image.convert('RGB')

    if format_name == 'WEBP' and image.mode not in ('RGB', 'RGBA'):
        has_alpha = image.mode in ('RGBA', 'LA', 'PA') or (
            image.mode == 'P' and 'transparency' in image.info)
        return image.convert('RGBA' if has_alpha else 'RGB')

    if format_name == 'PNG' and image.mode == 'CMYK':
        return image.convert('RGB')

    return image


class ImageProcessor(QObject):
    input_folder = None
    output_folder = None
    kwargs = {}

    image_path = None

    # 转 JPEG 时透明图片的处理方式：ask（询问）/ white（白底）/ black（黑底）/ skip（跳过）
    ALPHA_HANDLING_VALUES = ('ask', 'white', 'black', 'skip')
    # 输出文件名重复时的处理方式：ask（询问）/ overwrite（覆盖）/ rename（自动加序号）/ custom（自定义前缀）
    DUPLICATE_HANDLING_VALUES = ('ask', 'overwrite', 'rename', 'custom')

    def __init__(self, input_folder, output_folder, **kwargs):
        super().__init__()

        self.input_folder = input_folder
        self.output_folder = output_folder
        self.kwargs = kwargs

        self.alpha_handling = self.kwargs.get('alpha_handling', 'ask')
        if self.alpha_handling not in self.ALPHA_HANDLING_VALUES:
            self.alpha_handling = 'ask'

        self.duplicate_handling = self.kwargs.get('duplicate_handling', 'ask')
        if self.duplicate_handling not in self.DUPLICATE_HANDLING_VALUES:
            self.duplicate_handling = 'ask'

        # 输出文件夹中已存在的文件名（小写，忽略文件夹），用于检测同名覆盖
        self.existing_output_names = set()
        if os.path.isdir(output_folder):
            for name in os.listdir(output_folder):
                if os.path.isfile(os.path.join(output_folder, name)):
                    self.existing_output_names.add(name.lower())

    def run(
            self,
            progress_callback=None,
            progress_count_callback=None,
            console_callback=None,
            pause_callback=None,
            question_callback=None
    ):
        def log(message):
            if console_callback is not None:
                console_callback(message)

        def check_point():
            # 暂停时在这里阻塞，恢复后继续；返回 False 表示处理已被中止
            return pause_callback() if pause_callback is not None else True

        def ask(question):
            if question_callback is None:
                return None
            return question_callback(question)

        result = {
            'total': 0,
            'success': 0,
            'failed': [],
            'skipped': 0,
            'aborted': False,
            'alpha_questions': [],
            'duplicate_questions': [],
        }

        log('正在载入图片...')
        self.image_path = load_image_path_from_folder(
            self.input_folder,
            self.kwargs.get('recursive_load', False),
            check_point=check_point,
        )

        if self.image_path is None:
            log('处理已中止')
            result['aborted'] = True
            return result

        if not self.image_path:
            log('没有找到图片')
            return result

        total_count = len(self.image_path)
        result['total'] = total_count
        if progress_count_callback is not None:
            progress_count_callback(total_count)

        alpha_policy = self.alpha_handling
        duplicate_policy = self.duplicate_handling
        duplicate_prefix = ''

        # 没有界面回调（例如脚本直接调用）时使用默认策略，避免处理卡住
        if question_callback is None:
            if alpha_policy == 'ask':
                alpha_policy = 'white'
            if duplicate_policy == 'ask':
                duplicate_policy = 'rename'

        used_output_names = set()

        for index, image_path_item in enumerate(self.image_path):
            if not check_point():
                log('处理已中止')
                result['aborted'] = True
                return result

            source_name = os.path.basename(image_path_item)
            original_image_name = source_name
            image = None
            skipped = False
            try:
                image = Image.open(image_path_item)
                image.load()

                original_image_format = image.format
                if not original_image_format:
                    raise ValueError('无法识别图片格式')

                # MPO 本质上是 JPEG 多图容器，按 JPEG 处理
                if original_image_format.upper() == 'MPO':
                    original_image_format = 'JPEG'

                # 手机照片的方向信息在重新保存时会丢失，先按 EXIF 方向摆正像素
                image = ImageOps.exif_transpose(image)

                output_format_name = original_image_format

                if self.kwargs.get('is_selected_convert_image_format', False) is True:
                    log('正在转换图片格式: ' + source_name)
                    converted_format = find_field_by_value(
                        ImageFormat, self.kwargs.get('image_format', ImageFormat.JPEG.value))
                    if converted_format is None:
                        raise ValueError('未知的目标图片格式')
                    output_format_name = converted_format

                alpha_to_white = True
                if output_format_name.upper() in ('JPEG', 'MPO') and self._has_alpha(image):
                    if alpha_policy == 'ask':
                        result['alpha_questions'].append(source_name)
                        answer = ask({'type': 'alpha', 'source_name': source_name})
                        if answer in ('white', 'black', 'skip'):
                            alpha_policy = answer
                        else:
                            log('处理已中止')
                            result['aborted'] = True
                            return result

                    if alpha_policy == 'skip':
                        result['failed'].append(source_name)
                        result['skipped'] += 1
                        log('已跳过透明图片（目标格式不支持透明通道）: ' + source_name)
                        skipped = True
                    else:
                        alpha_to_white = alpha_policy != 'black'

                if not skipped:
                    image = convert_mode_for_format(image, output_format_name, alpha_to_white)

                    if self.kwargs.get('is_selected_compress_image', False) is True:
                        log('正在压缩图片: ' + source_name)
                        target_size = self.kwargs.get('image_target_size')
                        if target_size is not None and target_size > 0:
                            compressed_image = self._compress_image(
                                image, output_format_name, float(target_size), log, check_point)
                            if compressed_image is None:
                                log('处理已中止')
                                result['aborted'] = True
                                return result
                            image = compressed_image

                    if self.kwargs.get('is_selected_rename_image', False) is True:
                        log('正在重命名图片: ' + source_name)
                        original_image_name = self._build_new_name(
                            output_format_name,
                            self.kwargs.get('rename_image_method', RenameImageMethod.UUID.value),
                            result['success'],
                        )

                    desired_name = os.path.splitext(original_image_name)[0] + '.' + output_format_name.lower()
                    final_name = desired_name

                    if self._name_taken(desired_name, used_output_names):
                        if duplicate_policy == 'ask':
                            result['duplicate_questions'].append(desired_name)
                            answer = ask({
                                'type': 'duplicate',
                                'source_name': source_name,
                                'desired_name': desired_name,
                                'suggested_name': self._suggest_unique_name(desired_name, used_output_names),
                                'in_batch': desired_name.lower() in used_output_names,
                            })
                            if answer == 'overwrite':
                                duplicate_policy = 'overwrite'
                            elif answer == 'rename':
                                duplicate_policy = 'rename'
                            elif isinstance(answer, dict) and answer.get('action') == 'custom':
                                duplicate_policy = 'custom'
                                duplicate_prefix = answer.get('prefix') or ''
                            else:
                                log('处理已中止')
                                result['aborted'] = True
                                return result

                        if duplicate_policy == 'overwrite':
                            final_name = desired_name
                            log('输出文件已覆盖: ' + final_name)
                        elif duplicate_policy == 'custom':
                            final_name = self._custom_unique_name(
                                desired_name, duplicate_prefix, used_output_names)
                            log('输出文件名重复，已重命名为: ' + final_name)
                        else:
                            final_name = self._suggest_unique_name(desired_name, used_output_names)
                            log('输出文件名重复，已重命名为: ' + final_name)

                    used_output_names.add(final_name.lower())

                    new_path = os.path.join(self.output_folder, final_name)
                    image.save(new_path, format=self._save_format(output_format_name), optimize=True)

                    result['success'] += 1
            except Exception as error:
                result['failed'].append(source_name)
                log('处理失败，已跳过: %s（%s）' % (source_name, error))
            finally:
                if image is not None:
                    try:
                        image.close()
                    except Exception:
                        pass

            if progress_callback is not None:
                progress_callback(index + 1)

        log('处理完成: 成功 %d 张，失败 %d 张' % (result['success'], len(result['failed'])))
        if result['skipped'] > 0:
            log('其中因透明通道跳过 %d 张' % result['skipped'])
        return result

    @staticmethod
    def _save_format(image_format):
        # 部分格式（如 MPO）只是容器，统一按 JPEG 保存
        return 'JPEG' if image_format.upper() == 'MPO' else image_format.upper()

    @staticmethod
    def _has_alpha(image):
        return image.mode in ('RGBA', 'LA', 'PA') or (
            image.mode == 'P' and 'transparency' in image.info)

    @staticmethod
    def _encode_image(image, image_format, quality=None):
        buffer = io.BytesIO()
        save_kwargs = {'optimize': True}
        if quality is not None:
            save_kwargs['quality'] = quality
        image.save(buffer, format=image_format, **save_kwargs)
        return buffer

    def _compress_image(self, image, image_format, target_size_kb, log, check_point):
        """把图片压缩到接近目标大小（KB），必要时逐步降低质量、裁剪尺寸。"""
        save_format = self._save_format(image_format)
        supports_quality = save_format in ('JPEG', 'WEBP')

        # 先按当前设置编码一次，用真实的编码后大小判断是否需要压缩
        buffer = self._encode_image(image, save_format, 95 if supports_quality else None)
        current_size = len(buffer.getvalue()) / 1024

        quality = 90
        while supports_quality and current_size > target_size_kb and quality > 20:
            if not check_point():
                return None
            buffer = self._encode_image(image, save_format, quality)
            current_size = len(buffer.getvalue()) / 1024
            quality -= 5

        crop_quality = quality if supports_quality else None
        while current_size > target_size_kb:
            if not check_point():
                return None

            width, height = image.size
            new_width, new_height = int(width * 0.9), int(height * 0.9)
            if new_width < 1 or new_height < 1:
                log('无法压缩到目标大小，已保留当前结果')
                break

            image = ImageOps.fit(image, (new_width, new_height), Image.Resampling.LANCZOS)
            buffer = self._encode_image(image, save_format, crop_quality)
            current_size = len(buffer.getvalue()) / 1024

        buffer.seek(0)
        return Image.open(buffer)

    @staticmethod
    def _build_new_name(image_format, rename_image_method, index):
        extension = image_format.lower()

        if rename_image_method == RenameImageMethod.UUID.value:
            return str(uuid.uuid4()) + '.' + extension

        if rename_image_method == RenameImageMethod.MD5.value:
            length = 128
            random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
            md5_hash = hashlib.md5()
            md5_hash.update((str(time.perf_counter_ns()) + random_string).encode('utf-8'))
            return md5_hash.hexdigest() + '.' + extension

        if rename_image_method == RenameImageMethod.AUTO_INCREMENT_NUMBER.value:
            return str(index) + '.' + extension

        return str(uuid.uuid4()) + '.' + extension

    def _name_taken(self, name, used_names):
        key = name.lower()
        return key in used_names or key in self.existing_output_names

    def _suggest_unique_name(self, desired_name, used_names):
        base, extension = os.path.splitext(desired_name)
        counter = 1
        candidate = '%s_%d%s' % (base, counter, extension)
        while self._name_taken(candidate, used_names):
            counter += 1
            candidate = '%s_%d%s' % (base, counter, extension)
        return candidate

    def _custom_unique_name(self, desired_name, prefix, used_names):
        _, extension = os.path.splitext(desired_name)
        safe_prefix = re.sub(r'[\\/:*?"<>|]', '_', (prefix or '').strip())
        if safe_prefix:
            prefix_base, prefix_extension = os.path.splitext(safe_prefix)
            if prefix_extension and prefix_extension.lower() == extension.lower():
                safe_prefix = prefix_base
        if not safe_prefix:
            safe_prefix = os.path.splitext(desired_name)[0] or 'image'

        counter = 1
        candidate = '%s_%d%s' % (safe_prefix, counter, extension)
        while self._name_taken(candidate, used_names):
            counter += 1
            candidate = '%s_%d%s' % (safe_prefix, counter, extension)
        return candidate
