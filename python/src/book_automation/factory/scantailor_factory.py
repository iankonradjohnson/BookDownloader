from typing import Dict, Any

from python.src.book_automation.scantailor.scantailor_service import ScanTailorService


class ScanTailorFactory:
    """
    Factory for creating ScanTailorService instances with the appropriate configuration.
    Follows the factory pattern to properly handle dependency injection.
    """
    
    @staticmethod
    def create_service(config: Dict[str, Any]) -> ScanTailorService:
        """
        Create a ScanTailorService instance with the given configuration.
        
        Args:
            config: Configuration dictionary with ScanTailor settings
            
        Returns:
            Configured ScanTailorService instance
        """
        # Extract basic settings from config
        enabled = config.get('enabled', True)
        book_type = config.get('book_type', 'standard')
        color_mode = config.get('color_mode')
        force_color = config.get('force_color', False)
        dpi = config.get('dpi', 600)
        compression = config.get('compression', 'lzw')
        output_dir = config.get('output_dir', None)
        
        # Create and return the service with explicit parameters
        return ScanTailorService(
            enabled=enabled,
            book_type=book_type,
            color_mode=color_mode,
            force_color=force_color,
            dpi=dpi,
            compression=compression
        )