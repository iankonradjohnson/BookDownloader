import os
import unittest
import tempfile
import zipfile
import tarfile
import shutil

from python.src.processor.archive_extractor import ExtractorFactory, ZipExtractor, TarExtractor


class TestArchiveExtractor(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_file_content = b"This is a test file content"
        
        # Create a test zip file
        self.zip_path = os.path.join(self.test_dir, "test.zip")
        with zipfile.ZipFile(self.zip_path, 'w') as zipf:
            zipf.writestr("test.txt", self.test_file_content)
            zipf.writestr("subfolder/test2.txt", self.test_file_content)
        
        # Create a test tar file
        self.tar_path = os.path.join(self.test_dir, "test.tar")
        with tarfile.open(self.tar_path, 'w') as tarf:
            info = tarfile.TarInfo("test.txt")
            info.size = len(self.test_file_content)
            tarf.addfile(info, fileobj=tempfile.BytesIO(self.test_file_content))
            
            info = tarfile.TarInfo("subfolder/test2.txt")
            info.size = len(self.test_file_content)
            tarf.addfile(info, fileobj=tempfile.BytesIO(self.test_file_content))
            
    def tearDown(self):
        # Remove the temporary directory and files
        shutil.rmtree(self.test_dir)
        
    def test_factory_returns_correct_extractor(self):
        # Test that factory returns the correct extractor type
        zip_extractor = ExtractorFactory.get_extractor(self.zip_path)
        self.assertIsInstance(zip_extractor, ZipExtractor)
        
        tar_extractor = ExtractorFactory.get_extractor(self.tar_path)
        self.assertIsInstance(tar_extractor, TarExtractor)
        
        # Test with unsupported format
        unsupported_path = os.path.join(self.test_dir, "test.unsupported")
        with open(unsupported_path, 'wb') as f:
            f.write(self.test_file_content)
            
        extractor = ExtractorFactory.get_extractor(unsupported_path)
        self.assertIsNone(extractor)
        
    def test_zip_extractor(self):
        # Test ZIP extraction
        extractor = ZipExtractor()
        extract_dir = os.path.join(self.test_dir, "zip_extract")
        
        result = extractor.extract(self.zip_path, extract_dir)
        self.assertEqual(result, extract_dir)
        
        # Check that files were extracted correctly
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "subfolder", "test2.txt")))
        
        # Check file content
        with open(os.path.join(extract_dir, "test.txt"), 'rb') as f:
            self.assertEqual(f.read(), self.test_file_content)
            
    def test_tar_extractor(self):
        # Test TAR extraction
        extractor = TarExtractor()
        extract_dir = os.path.join(self.test_dir, "tar_extract")
        
        result = extractor.extract(self.tar_path, extract_dir)
        self.assertEqual(result, extract_dir)
        
        # Check that files were extracted correctly
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "subfolder", "test2.txt")))
        
        # Check file content
        with open(os.path.join(extract_dir, "test.txt"), 'rb') as f:
            self.assertEqual(f.read(), self.test_file_content)
            
    def test_extraction_to_default_directory(self):
        # Test extraction when no output directory is specified
        extractor = ZipExtractor()
        result = extractor.extract(self.zip_path)
        
        # Should extract to the same directory as the archive
        self.assertEqual(result, os.path.dirname(self.zip_path))
        
        # Check that files were extracted correctly
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "test.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "subfolder", "test2.txt")))
        
    def test_invalid_archive(self):
        # Test extraction with invalid archive
        invalid_path = os.path.join(self.test_dir, "invalid.zip")
        with open(invalid_path, 'wb') as f:
            f.write(b"This is not a valid zip file")
            
        extractor = ZipExtractor()
        result = extractor.extract(invalid_path)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()