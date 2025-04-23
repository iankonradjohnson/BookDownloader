from abc import ABC, abstractmethod
from typing import Optional, List


class ImageDirectoryProcessor(ABC):
    """
    Abstract base class for image processors.
    Defines a simple interface for any component that processes images.
    This could be conversion, enhancement, or any other image operation.
    """
    
    @abstractmethod
    def process(self, input_filepath: str, output_filepath: Optional[str] = None) -> str:
        """
        Process an image file.
        
        Args:
            input_filepath: Path to the input image file
            output_filepath: Optional path for the output file
                             If None, replace the original file after processing
                             If provided, save to this path and keep the original
            
        Returns:
            Path to the processed output file
        """
        pass