import unittest
import os
from PIL import Image

from python.src.book_automation.processor.converter.image_converter import ImageConverter


class TestImageConverter(unittest.TestCase):

    def setUp(self):
        # Create a sample JPG image for testing
        self.sample_jpg = "sample.jpg"
        im = Image.new('RGB', (100, 100), color=(73, 109, 137))
        im.save(self.sample_jpg)

    def tearDown(self):
        # Cleanup any created files
        if os.path.exists(self.sample_jpg):
            os.remove(self.sample_jpg)

        sample_png = "sample.png"
        if os.path.exists(sample_png):
            os.remove(sample_png)

    def test_convert_to_png(self):
        output_path = ImageConverter.convert(self.sample_jpg)
        self.assertEqual(output_path, "sample.png")
        self.assertTrue(os.path.exists(output_path))
        self.assertFalse(os.path.exists(self.sample_jpg))

    def test_convert_invalid_file(self):
        output_path = ImageConverter.convert("nonexistent.jpg")
        self.assertEqual(output_path, "")


if __name__ == "__main__":
    unittest.main()
