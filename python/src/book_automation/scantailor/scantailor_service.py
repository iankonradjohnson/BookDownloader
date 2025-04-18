import os
import subprocess
import time
from typing import List

class ScanTailorService:
    def __init__(self, 
                 enabled: bool = True,
                 content_detection: str = "normal",
                 auto_margins: bool = True,
                 dpi: int = 600,
                 compression: str = 'lzw'):
        self.enabled = enabled
        self.content_detection = content_detection
        self.auto_margins = auto_margins
        self.dpi = dpi
        self.compression = compression
    
    def process_images(self, input_dir: str, output_dir: str) -> bool:
        if not self.enabled:
            print("ScanTailor processing is disabled")
            return False
            
        os.makedirs(output_dir, exist_ok=True)
        print(f"Processing images from {input_dir} to {output_dir}")
        
        start_time = time.time()
        
        cmd = self._build_scantailor_command(input_dir, output_dir)
        cmd_str = ' '.join(cmd)
        
        print(f"Starting ScanTailor with command: {cmd_str}")
        
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            elapsed_time = time.time() - start_time
            print(f"ScanTailor processing completed successfully in {elapsed_time:.2f} seconds")
            
            output_file_count = len([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))])
            print(f"Generated {output_file_count} output files in {output_dir}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"ScanTailor processing failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def _build_scantailor_command(self, input_dir: str, output_dir: str) -> List[str]:
        cmd = ["scantailor-universal-cli"]
        
        # Basic settings
        cmd.extend([
            "--layout=1",
            "--deskew=off",             # Turn off deskew - handled separately in pipeline
            f"--content-detection={self.content_detection}",
        ])
            
        # Other settings
        cmd.extend([
            "--white-margins",
            "--normalize-illumination",
            "--despeckle=normal",
            "--color-mode=mixed",
            f"--output-dpi={self.dpi}",
            f"--tiff-compression={self.compression}",
            "--tiff-force-keep-color-space",
            # f"--content-detection={self.content_detection}",
            "--enable-page-detection",
            input_dir,
            output_dir
        ])
        
        return cmd