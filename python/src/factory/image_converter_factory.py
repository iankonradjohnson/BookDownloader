from typing import Dict, Any

from python.src.processor.converter.image_converter import ImageConverter, PilImageConverter


class ImageConverterFactory:
    """
    Factory for creating ImageConverter instances with the appropriate configuration.
    """
    
    @staticmethod
    def create_converter(
        to_ext: str = "png",
        converter_type: str = "pillow"
    ) -> ImageConverter:
        """
        Create an appropriate ImageConverter based on requested configuration.
        
        Args:
            to_ext: Target file extension
            converter_type: Type of processor to use (pillow, opencv, etc.)
            
        Returns:
            An instance of an ImageConverter
        """
        # Select the appropriate processor implementation
        if converter_type.lower() == "pillow":
            return PilImageConverter(
                output_format=to_ext.upper()
            )
        
        # Default to PIL processor
        return PilImageConverter(
            output_format=to_ext.upper()
        )
    
    @staticmethod
    def create_converter_from_config(config: Dict[str, Any]) -> ImageConverter:
        """
        Create an ImageConverter from a configuration dictionary.
        
        Args:
            config: Dictionary containing processor configuration
            
        Returns:
            An instance of an ImageConverter
        """
        converter_type = config.get("converter_type", "pillow")
        to_ext = config.get("to_ext", "png")
        
        return ImageConverterFactory.create_converter(
            to_ext=to_ext,
            converter_type=converter_type
        )