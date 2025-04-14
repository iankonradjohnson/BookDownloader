import os
import zipfile
import tarfile
import logging
from abc import ABC, abstractmethod
from tqdm import tqdm

from python.src.util.file_utility import FileUtility


class ArchiveExtractor(ABC):
    """
    Abstract base class for archive extraction
    """
    
    @abstractmethod
    def extract(self, archive_path, output_dir=None, move_to_trash=False):
        """
        Extract the archive to the output directory
        
        Args:
            archive_path (str): Path to the archive file
            output_dir (str, optional): Directory to extract to. If None, extracts to the same directory as the archive.
            move_to_trash (bool, optional): Whether to move the archive to trash after extraction. Default is False.
        
        Returns:
            str: Path to the extraction directory
        """
        pass


class ZipExtractor(ArchiveExtractor):
    """
    Extractor for ZIP archives
    """
    
    def extract(self, archive_path, output_dir=None, move_to_trash=False):
        """
        Extract a ZIP archive
        
        Args:
            archive_path (str): Path to the ZIP file
            output_dir (str, optional): Directory to extract to. If None, extracts to the same directory as the archive.
            move_to_trash (bool, optional): Whether to move the archive to trash after extraction.
        
        Returns:
            str: Path to the extraction directory
        """
        if not zipfile.is_zipfile(archive_path):
            logging.error(f"File is not a valid ZIP archive: {archive_path}")
            return None
            
        if output_dir is None:
            # Extract to the same directory as the archive
            output_dir = os.path.dirname(archive_path)
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Get list of files to extract with their sizes
                file_info_list = zip_ref.infolist()
                total_size = sum(info.file_size for info in file_info_list)
                
                # Create progress bar for extraction
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                         desc=f"Extracting {os.path.basename(archive_path)}") as pbar:
                     
                    # Extract files one by one with progress tracking
                    for file_info in file_info_list:
                        zip_ref.extract(file_info, output_dir)
                        pbar.update(file_info.file_size)
                        
            logging.info(f"Successfully extracted ZIP archive to {output_dir}")
            
            # Move archive to trash if requested
            if move_to_trash:
                if FileUtility.move_to_trash(archive_path):
                    logging.info(f"Moved archive to trash: {archive_path}")
                else:
                    logging.warning(f"Failed to move archive to trash: {archive_path}")
                    
            return output_dir
        except Exception as e:
            logging.error(f"Error extracting ZIP archive: {e}")
            return None


class TarExtractor(ArchiveExtractor):
    """
    Extractor for TAR archives (including .tar.gz, .tgz, .tar.bz2)
    """
    
    def extract(self, archive_path, output_dir=None, move_to_trash=False):
        """
        Extract a TAR archive
        
        Args:
            archive_path (str): Path to the TAR file
            output_dir (str, optional): Directory to extract to. If None, extracts to the same directory as the archive.
            move_to_trash (bool, optional): Whether to move the archive to trash after extraction.
        
        Returns:
            str: Path to the extraction directory
        """
        if not tarfile.is_tarfile(archive_path):
            logging.error(f"File is not a valid TAR archive: {archive_path}")
            return None
            
        if output_dir is None:
            # Extract to the same directory as the archive
            output_dir = os.path.dirname(archive_path)
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                # Get members list for progress tracking
                members = tar_ref.getmembers()
                
                # Create progress bar for extraction
                with tqdm(total=len(members), unit='file', 
                         desc=f"Extracting {os.path.basename(archive_path)}") as pbar:
                    
                    # Extract files one by one with progress tracking
                    for member in members:
                        tar_ref.extract(member, output_dir)
                        pbar.update(1)
                
            logging.info(f"Successfully extracted TAR archive to {output_dir}")
            
            # Move archive to trash if requested
            if move_to_trash:
                if FileUtility.move_to_trash(archive_path):
                    logging.info(f"Moved archive to trash: {archive_path}")
                else:
                    logging.warning(f"Failed to move archive to trash: {archive_path}")
                    
            return output_dir
        except Exception as e:
            logging.error(f"Error extracting TAR archive: {e}")
            return None


class ExtractorFactory:
    """
    Factory for creating appropriate extractors based on file extension
    """
    
    @staticmethod
    def get_extractor(file_path):
        """
        Get the appropriate extractor for a file based on its extension
        
        Args:
            file_path (str): Path to the archive file
        
        Returns:
            ArchiveExtractor: The appropriate extractor for the file type
        """
        if file_path.endswith('.zip'):
            return ZipExtractor()
        elif any(file_path.endswith(ext) for ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']):
            return TarExtractor()
        else:
            logging.error(f"Unsupported archive format: {file_path}")
            return None