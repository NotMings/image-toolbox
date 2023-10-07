import os
from PIL import Image


def load_image_path_from_folder(folder, recursive=False):
    image_path = []

    if recursive:
        for subdir, dirs, files in os.walk(folder):
            for file in files:
                try:
                    Image.open(os.path.join(subdir, file))
                    image_path.append(os.path.join(subdir, file))
                except IOError:
                    pass  # 不是图片
    else:
        for file in os.listdir(folder):
            try:
                Image.open(os.path.join(folder, file))
                image_path.append(os.path.join(folder, file))
            except IOError:
                pass  # 不是图片

    return image_path
