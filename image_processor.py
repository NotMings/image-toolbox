import hashlib
import io
import os
import random
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


class ImageProcessor(QObject):
    input_folder = None
    output_folder = None
    kwargs = {}

    image_path = None

    def __init__(self, input_folder, output_folder, **kwargs):
        super().__init__()

        self.input_folder = input_folder
        self.output_folder = output_folder
        self.kwargs = kwargs

    def run(
            self,
            progress_callback=None,
            progress_count_callback=None,
            console_callback=None
    ):
        if console_callback is not None:
            console_callback('正在载入图片...')

        self.image_path = load_image_path_from_folder(self.input_folder, self.kwargs.get('recursive_load', False))

        if not self.image_path:
            if console_callback is not None:
                console_callback('没有找到图片')
            return

        i = 0

        total_count = len(self.image_path)
        if progress_count_callback is not None:
            progress_count_callback(total_count)

        for image_path_item in self.image_path:
            image = Image.open(image_path_item)

            # 获取原始图片的格式
            original_image_format = image.format
            original_image_name = os.path.basename(image_path_item)

            output_folder = self.output_folder

            buffer = None
            if self.kwargs.get('is_selected_convert_image_format', False) is True:
                if console_callback is not None:
                    console_callback('正在转换图片格式: ' + original_image_name)

                image_format = find_field_by_value(ImageFormat, self.kwargs.get('image_format', ImageFormat.JPEG.value))
                original_image_format = image_format

            if self.kwargs.get('is_selected_compress_image', False) is True:
                if console_callback is not None:
                    console_callback('正在压缩图片: ' + original_image_name)

                image_target_size = self.kwargs.get('image_target_size', 0.0)
                if image_target_size > 0:
                    step = 5
                    quality = 95
                    min_quality = 20  # 设置最低质量限制

                    o_size = len(image.tobytes()) / 1024  # 获取图片大小
                    if o_size <= image_target_size:
                        return image  # 如果当前图片大小小于等于目标大小，则无需压缩
                    while o_size > image_target_size and quality > min_quality:  # 添加质量下限判断
                        buffer = io.BytesIO()
                        image.save(buffer, format=original_image_format.upper(),
                                   quality=quality)  # 保存时修改quality参数，达到压缩的目的
                        quality -= step  # 每次循环，quality减小，以达到更小的文件大小
                        o_size = len(buffer.getvalue()) / 1024

                    # 如果质量已经达到最低限制，但是图像大小仍然大于目标大小，则尝试裁剪图像
                    while o_size > image_target_size and quality <= min_quality:  # 添加裁剪循环
                        width, height = image.size
                        new_width, new_height = int(width * 0.9), int(height * 0.9)  # 将图像尺寸缩小10%
                        image = ImageOps.fit(image, (new_width, new_height), Image.LANCZOS)
                        buffer = io.BytesIO()
                        image.save(buffer, format=original_image_format.upper(), quality=quality)
                        o_size = len(buffer.getvalue()) / 1024

                    image = Image.open(buffer)

            if self.kwargs.get('is_selected_rename_image', False) is True:
                if console_callback is not None:
                    console_callback('正在重命名图片: ' + original_image_name)

                rename_image_method = self.kwargs.get('rename_image_method', RenameImageMethod.UUID.value)

                if rename_image_method == RenameImageMethod.UUID.value:
                    original_image_name = str(uuid.uuid4()) + '.' + original_image_format.lower()
                elif rename_image_method == RenameImageMethod.MD5.value:
                    length = 128
                    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
                    md5_hash = hashlib.md5()
                    md5_hash.update((str(time.perf_counter_ns()) + random_string).encode('utf-8'))
                    original_image_name = md5_hash.hexdigest() + '.' + original_image_format.lower()
                elif rename_image_method == RenameImageMethod.AUTO_INCREMENT_NUMBER.value:
                    original_image_name = str(i) + '.' + original_image_format.lower()

            new_name = os.path.splitext(original_image_name)[0] + '.' + original_image_format.lower()
            new_path = os.path.join(output_folder, new_name)

            image.save(new_path, format=original_image_format.upper(), optimize=True)

            i += 1
            if progress_callback is not None:
                progress_callback(i)
