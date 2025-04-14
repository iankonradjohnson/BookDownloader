import os
import unittest
import tempfile
import zipfile
import shutil
from unittest.mock import patch, MagicMock

from python.src.downloader.batch_archive_pdf_downloader import BatchArchiveDownloader, PROCESSED_ZIP
from python.src.util.file_utility import FileUtility


class TestBatchArchiveDownloader(unittest.TestCase):
    
    def setUp(self):
        # Create temporary directory and test files
        self.test_dir = tempfile.mkdtemp()
        self.zip_content = b"Test zip content"
        
        # Create temp file with identifiers
        self.identifiers_file = os.path.join(self.test_dir, "identifiers.txt")
        with open(self.identifiers_file, 'w') as f:
            f.write("test_book1\ntest_book2\n")
            
        # Create output directory
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create test config
        self.config = {
            "input_list": self.identifiers_file,
            "output_path": self.output_dir
        }
        
    def tearDown(self):
        # Remove test directory and files
        shutil.rmtree(self.test_dir)
        
    @patch('requests.Session')
    def test_download_with_extraction(self, mock_session):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [self.zip_content]
        
        # Setup session mock
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # Create downloader with extraction enabled but no trashing
        downloader = BatchArchiveDownloader(self.config, extract_archives=True, trash_archives=False)
        
        # Create a real zip file for the extraction test
        identifier = "test_book1"
        filename = f"{identifier}_jp2.zip"
        zip_path = os.path.join(self.output_dir, filename)
        
        # Create test zip with some content
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("test.txt", self.zip_content)
            zipf.writestr("subfolder/nested.txt", self.zip_content)
        
        # Run download - this should also extract the already created zip
        downloader.download()
        
        # Verify extraction
        extract_dir = os.path.join(self.output_dir, identifier)
        self.assertTrue(os.path.exists(extract_dir), "Extraction directory should exist")
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "test.txt")), "Extracted file should exist")
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "subfolder/nested.txt")), 
                        "Nested extracted file should exist")
        
        # Verify file content
        with open(os.path.join(extract_dir, "test.txt"), 'rb') as f:
            self.assertEqual(f.read(), self.zip_content)
            
        # Verify archive still exists (not trashed)
        self.assertTrue(os.path.exists(zip_path), "Archive should still exist (not trashed)")
            
    @patch('requests.Session')
    def test_download_without_extraction(self, mock_session):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [self.zip_content]
        
        # Setup session mock
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # Create downloader with extraction disabled
        downloader = BatchArchiveDownloader(self.config, extract_archives=False)
        
        # Create a real zip file
        identifier = "test_book1"
        filename = f"{identifier}_jp2.zip"
        zip_path = os.path.join(self.output_dir, filename)
        
        # Create test zip
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("test.txt", self.zip_content)
        
        # Run download
        downloader.download()
        
        # Verify no extraction happened
        extract_dir = os.path.join(self.output_dir, identifier)
        self.assertFalse(os.path.exists(extract_dir), "Extraction directory should not exist")
        
    @patch('requests.Session')
    @patch('python.src.util.file_utility.FileUtility.move_to_trash')
    def test_download_with_extraction_and_trashing(self, mock_move_to_trash, mock_session):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [self.zip_content]
        
        # Setup session mock
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # Setup trash mock to return True (success)
        mock_move_to_trash.return_value = True
        
        # Create downloader with extraction and trashing enabled
        downloader = BatchArchiveDownloader(self.config, extract_archives=True, trash_archives=True)
        
        # Create a real zip file for the extraction test
        identifier = "test_book1"
        filename = f"{identifier}_jp2.zip"
        zip_path = os.path.join(self.output_dir, filename)
        
        # Create test zip with some content
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr("test.txt", self.zip_content)
        
        # Run download
        downloader.download()
        
        # Verify extraction
        extract_dir = os.path.join(self.output_dir, identifier)
        self.assertTrue(os.path.exists(extract_dir), "Extraction directory should exist")
        
        # Verify the move_to_trash method was called with the correct path
        mock_move_to_trash.assert_called_once_with(zip_path)


if __name__ == '__main__':
    unittest.main()