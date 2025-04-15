from abc import ABC, abstractmethod
from typing import Optional

from python.src.processor.image_processor import ImageProcessor


class ImageConverter(ImageProcessor, ABC):
    """
    Abstract base class for image converters.
    All image converters must implement this interface.
    Implements the ImageProcessor interface.
    """
    def __init__(
        self,
        output_format: str = "PNG",
    ):
        """
        Initialize the image converter.
        
        Args:
            output_format: The format to convert to (PNG, JPEG, etc.)
        """
        self.output_format = output_format
    
    @abstractmethod
    def convert(self, input_filepath: str, output_filepath: Optional[str] = None) -> str:
        """
        Convert an image from one format to another.
        
        Args:
            input_filepath: Path to the input image file
            output_filepath: Optional path for the output file
                             If None, replace the original file
                             If provided, save to this path and keep the original
            
        Returns:
            Path to the converted image file
        """
        pass
    
    def process(self, input_filepath: str, output_filepath: Optional[str] = None) -> str:
        return self.convert(input_filepath, output_filepath)

