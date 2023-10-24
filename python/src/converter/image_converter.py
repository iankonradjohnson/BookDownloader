import os

import PIL
from PIL import Image


class ImageConverter:
    @staticmethod
    def convert(input_filepath: str, output_filepath: str = None, to_format="PNG") -> str:
        try:
            with Image.open(input_filepath) as image:
                if output_filepath is None:
                    png_path = input_filepath.rsplit('.', 1)[0] + '.png'
                image.save(png_path, format=to_format)
                os.remove(input_filepath)
                return png_path
        except (FileNotFoundError, PIL.UnidentifiedImageError) as e:
            print(e)
            return ""


