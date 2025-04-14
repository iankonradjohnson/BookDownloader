import unittest
import tempfile
import os
import zipfile
import shutil

from python.src.converter.archive_extractor import ZipExtractor

class SimpleTest(unittest.TestCase):
    def test_zip_extraction(self):
        # Create temp dir and test zip
        test_dir = tempfile.mkdtemp()
        try:
            # Create test content
            test_content = b"Test content"
            
            # Create a test zip
            zip_path = os.path.join(test_dir, "test.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.writestr("test.txt", test_content)
            
            # Extract using our extractor
            extractor = ZipExtractor()
            output_dir = os.path.join(test_dir, "output")
            extractor.extract(zip_path, output_dir)
            
            # Verify extraction
            extracted_file = os.path.join(output_dir, "test.txt")
            self.assertTrue(os.path.exists(extracted_file))
            
            with open(extracted_file, 'rb') as f:
                self.assertEqual(f.read(), test_content)
                
        finally:
            # Clean up
            shutil.rmtree(test_dir)

if __name__ == '__main__':
    unittest.main()
