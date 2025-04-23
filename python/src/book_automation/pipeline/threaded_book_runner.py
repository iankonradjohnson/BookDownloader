import os
import concurrent.futures
import logging
from typing import List, Optional
import glob
from tqdm import tqdm

from python.src.book_automation.processor.image_processor import ImageDirectoryProcessor


class ThreadedBookRunner:
    def __init__(
        self, 
        processor: ImageDirectoryProcessor,
        input_dir: str,
        output_dir: Optional[str] = None,
        file_pattern: str = "*",
        max_workers: int = 8,
    ):
        """
        Initialize the ThreadedBookRunner.
        
        Args:
            processor: The ImageProcessor to use for processing
            input_dir: Directory containing images to process
            output_dir: Optional directory to save processed images to (if None, replace originals)
            file_pattern: Glob pattern to match files (e.g., "*.jp2")
            max_workers: Maximum number of worker threads to use
        """
        self.processor = processor
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.file_pattern = file_pattern
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def _find_files(self) -> List[str]:
        """
        Find files to process based on the input path and pattern.
        
        Returns:
            List of file paths to process
        """
        if not self.input_dir or not os.path.exists(self.input_dir):
            return []
            
        if os.path.isfile(self.input_dir):
            return [self.input_dir]
            
        # If it's a directory, use pattern to find files
        pattern = self.file_pattern
        if not pattern.startswith("*"):
            pattern = f"*{pattern}"
            
        search_pattern = os.path.join(self.input_dir, pattern)
        files = glob.glob(search_pattern)
        return sorted(files)
    
    def run(self) -> List[str]:
        """
        Process all matching files in parallel using threads.
        
        Returns:
            List of paths to the processed output files
        """
        files = self._find_files()
        if not files:
            self.logger.warning(f"No files found to process in {self.input_dir}")
            return []
            
        # Create output directory if needed
        if self.output_dir and not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            
        results = []
        self.logger.info(f"Processing {len(files)} files with {self.max_workers} workers")
        
        # Process files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all processing tasks
            future_to_file = {}
            
            for file_path in files:
                if self.output_dir:
                    if hasattr(self.processor, 'output_format'):
                        output_ext = self.processor.output_format.lower()
                    else:
                        _, output_ext = os.path.splitext(file_path)
                        output_ext = output_ext.lstrip('.')
                    
                    base_filename = os.path.splitext(os.path.basename(file_path))[0]
                    output_filename = f"{base_filename}.{output_ext}"
                    output_path = os.path.join(self.output_dir, output_filename)
                else:
                    output_path = None
                
                future = executor.submit(self.processor.process, file_path, output_path)
                future_to_file[future] = file_path
            
            # Process results as they complete with progress bar
            with tqdm(total=len(files), desc="Processing files") as progress_bar:
                for future in concurrent.futures.as_completed(future_to_file):
                    input_file = future_to_file[future]
                    try:
                        output_file = future.result()
                        if output_file:
                            results.append(output_file)
                        else:
                            self.logger.error(f"Failed to process {input_file}")
                    except Exception as e:
                        self.logger.exception(f"Error processing {input_file}: {e}")
                    
                    progress_bar.update(1)
        
        self.logger.info(f"Successfully processed {len(results)} of {len(files)} files")
        return results