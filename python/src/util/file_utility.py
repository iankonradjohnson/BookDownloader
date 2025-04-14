
import os
import shutil
import logging
import platform
import subprocess
from pathlib import Path

class FileUtility:

    @staticmethod
    def create_image_name(i):
        return f"image_{str.zfill(str(i), 4)}.png"
        
    @staticmethod
    def move_to_trash(file_path):
        """
        Move a file to the system trash/recycle bin.
        
        Args:
            file_path (str): Path to the file to be moved to trash
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logging.warning(f"File not found, cannot move to trash: {file_path}")
            return False
            
        try:
            # macOS
            if platform.system() == 'Darwin':
                subprocess.run(['osascript', '-e', f'tell application "Finder" to delete POSIX file "{file_path}"'], 
                              check=True, capture_output=True)
                return True
                
            # Windows
            elif platform.system() == 'Windows':
                import winshell
                winshell.delete_file(file_path, no_confirm=True, allow_undo=True)
                return True
                
            # Linux with trash-cli
            elif platform.system() == 'Linux':
                try:
                    subprocess.run(['trash', file_path], check=True, capture_output=True)
                    return True
                except (subprocess.SubprocessError, FileNotFoundError):
                    # If trash-cli is not available, fall back to standard delete
                    pass
                    
            # Fallback - move to a trash directory
            trash_dir = os.path.join(os.path.dirname(file_path), '.trash')
            os.makedirs(trash_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(trash_dir, os.path.basename(file_path)))
            logging.info(f"Moved file to local trash directory: {file_path} -> {trash_dir}")
            return True
            
        except Exception as e:
            logging.error(f"Error moving file to trash: {e}")
            return False