import os
import subprocess
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ScanTailorService:
    """
    Service responsible for processing images with ScanTailor.
    This class follows SRP by focusing solely on the ScanTailor operations.
    """
    
    def __init__(self, enabled: bool = True,
                 book_type: str = 'standard',
                 color_mode: Optional[str] = None,
                 force_color: bool = False,
                 dpi: int = 600,
                 compression: str = 'lzw'):
        """
        Initialize the ScanTailor service with explicit parameters.
        
        Args:
            enabled: Whether ScanTailor processing is enabled
            book_type: Type of book ('standard', 'text_heavy', 'image_heavy')
            color_mode: Color mode to use (overrides book_type default if provided)
            force_color: Whether to force RGB color mode
            dpi: Output DPI resolution
            compression: TIFF compression type
        """
        self.enabled = enabled
        self.book_type = book_type
        self.color_mode = color_mode
        self.force_color = force_color
        self.dpi = dpi
        self.compression = compression

        # Book type specific parameters
        self.content_detection = self._get_content_detection_for_book_type()
        self.margins = self._get_margins_for_book_type()
        self.despeckle = self._get_despeckle_for_book_type()
    
    def process_images(self, input_dir: str, output_dir: str) -> bool:
        """
        Process images in input directory with ScanTailor.
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory to save processed images
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.info("ScanTailor processing is disabled")
            return False
            
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if ScanTailor is installed
        if not self._is_scantailor_available():
            logger.error("ScanTailor is not available. Skipping processing.")
            return False
        
        # Get ScanTailor version info for logging
        version_info = self._get_scantailor_version()
        logger.debug(f"ScanTailor version: {version_info}")
        
        # Determine color mode to use
        color_mode = self._get_color_mode()
        
        # Build ScanTailor command
        cmd = self._build_scantailor_command(input_dir, output_dir, color_mode)
        
        # Run ScanTailor
        cmd_str = ' '.join(cmd)
        print(f"Running ScanTailor command: {cmd_str}")
        logger.info(f"ScanTailor command: {cmd_str}")
        
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            logger.info("ScanTailor processing completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"ScanTailor processing failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            
            # Try fallback approach
            logger.info("Trying fallback ScanTailor approach...")
            return self._run_fallback_scantailor(input_dir, output_dir, color_mode)
    
    def _is_scantailor_available(self) -> bool:
        """
        Check if ScanTailor is available.
        
        Returns:
            True if ScanTailor is available, False otherwise
        """
        try:
            result = subprocess.run(["which", "scantailor-universal-cli"], 
                                   check=True, text=True, capture_output=True)
            scantailor_path = result.stdout.strip()
            logger.info(f"ScanTailor found at: {scantailor_path}")
            
            subprocess.run(["scantailor-universal-cli", "--help"], 
                         check=True, capture_output=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"ScanTailor not available: {e}")
            return False
    
    def _get_scantailor_version(self) -> str:
        """
        Get ScanTailor version information.
        
        Returns:
            Version string or error message
        """
        try:
            result = subprocess.run(["scantailor-universal-cli", "--version"], 
                                  check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            return "Unknown (could not detect version)"
    
    def _get_content_detection_for_book_type(self) -> str:
        """
        Get content detection setting based on book type.
        
        Returns:
            Content detection setting
        """
        if self.book_type == 'text_heavy':
            return "aggressive"
        elif self.book_type == 'image_heavy':
            return "cautious"
        else:  # standard
            return "normal"
    
    def _get_margins_for_book_type(self) -> Dict[str, Any]:
        """
        Get margins settings based on book type.
        
        Returns:
            Margins settings
        """
        if self.book_type == 'text_heavy':
            return {
                'type': 'individual',
                'left': 5,
                'right': 5,
                'top': 5,
                'bottom': 5
            }
        elif self.book_type == 'image_heavy':
            return {
                'type': 'uniform',
                'value': 10
            }
        else:  # standard
            return {
                'type': 'uniform',
                'value': 5
            }
    
    def _get_despeckle_for_book_type(self) -> str:
        """
        Get despeckle setting based on book type.
        
        Returns:
            Despeckle setting
        """
        if self.book_type == 'text_heavy':
            return "normal"
        elif self.book_type == 'image_heavy':
            return "cautious"
        else:  # standard
            return "normal"
    
    def _get_color_mode(self) -> str:
        """
        Determine color mode to use.
        
        Returns:
            Color mode setting
        """
        if self.color_mode:
            return self.color_mode
            
        if self.book_type == 'text_heavy':
            return "mixed"
        elif self.book_type == 'image_heavy':
            return "color_grayscale"
        else:  # standard
            return "mixed"
    
    def _build_scantailor_command(self, input_dir: str, output_dir: str, color_mode: str) -> List[str]:
        """
        Build ScanTailor command based on configuration.
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            color_mode: Color mode to use
            
        Returns:
            List of command components
        """
        cmd = ["scantailor-universal-cli"]
        
        # Add basic settings
        cmd.extend([
            "--layout=auto",
            "--deskew=off",  # We already deskewed with ImageMagick
            f"--content-detection={self.content_detection}",
        ])
        
        # Add margins based on book type
        if self.margins['type'] == 'individual':
            cmd.extend([
                f"--margins-left={self.margins['left']}",
                f"--margins-right={self.margins['right']}",
                f"--margins-top={self.margins['top']}",
                f"--margins-bottom={self.margins['bottom']}"
            ])
        else:
            cmd.extend([f"--margins={self.margins['value']}"])
        
        # Add common settings
        cmd.extend([
            "--white-margins",
            "--normalize-illumination",
            f"--despeckle={self.despeckle}",
            f"--color-mode={color_mode}",
            f"--output-dpi={self.dpi}",
            f"--tiff-compression={self.compression}"
        ])
        
        # Add advanced settings for text-heavy books
        if self.book_type == 'text_heavy':
            cmd.extend([
                "--enable-page-detection",
                "--enable-fine-tuning"
            ])
        
        # Add color handling
        if self.force_color:
            cmd.append("--tiff-force-rgb")
        else:
            cmd.append("--tiff-force-keep-color-space")
        
        # Add input and output directories
        cmd.append(input_dir)
        cmd.append(output_dir)
        
        return cmd
    
    def _run_fallback_scantailor(self, input_dir: str, output_dir: str, color_mode: str) -> bool:
        """
        Run a simplified fallback ScanTailor command.
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            color_mode: Color mode to use
            
        Returns:
            True if successful, False otherwise
        """
        # Simplified command with fewer options for fallback
        cmd = [
            "scantailor-universal-cli",
            "--layout=single",  # Simplest layout option
            "--deskew=off",
            "--margins=10",
            "--white-margins",
            f"--color-mode={color_mode}",
            f"--output-dpi={self.dpi}",
            input_dir,
            output_dir
        ]
        
        # Add color handling
        if self.force_color:
            cmd.append("--tiff-force-rgb")
        else:
            cmd.append("--tiff-force-keep-color-space")
        
        cmd_str = ' '.join(cmd)
        logger.info(f"Running fallback ScanTailor command: {cmd_str}")
        try:
            fallback_result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            logger.info("Fallback ScanTailor processing completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Fallback ScanTailor processing also failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False