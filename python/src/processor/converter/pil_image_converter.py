import os
from typing import Optional

import PIL
from PIL import Image

from python.src.processor.converter.image_converter import ImageConverter


class PilImageConverter(ImageConverter):
    def __init__(self, output_format: str = "PNG"):
        super().__init__(output_format)

    def convert(self, input_filepath: str, output_filepath: Optional[str] = None) -> str:
        try:
            if output_filepath is None:
                output_ext = self.output_format.lower()
                output_filepath = input_filepath.rsplit('.', 1)[0] + f'.{output_ext}'
                replace_original = True
            else:
                replace_original = False

                os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

            with Image.open(input_filepath) as image:
                image.save(output_filepath, format=self.output_format)

            if replace_original and os.path.exists(output_filepath):
                os.remove(input_filepath)

            return output_filepath
        except (FileNotFoundError, PIL.UnidentifiedImageError) as e:
            print(f"Error converting {input_filepath}: {e}")
            return ""
