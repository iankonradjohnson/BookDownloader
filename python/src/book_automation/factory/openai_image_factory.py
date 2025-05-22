from typing import Dict, Optional, Any
from ..externals.openai_image_client import OpenAIImageClient

class OpenAIImageFactory:
    """
    Factory for creating OpenAI image generation clients.
    """
    
    @staticmethod
    def create_client(config: Dict[str, Any]) -> OpenAIImageClient:
        """
        Create an OpenAI image generation client from configuration.
        
        Args:
            config: Configuration dictionary
                {
                    "api_key": Optional[str],
                    "model": Optional[str]
                }
                
        Returns:
            Configured OpenAIImageClient
        """
        api_key = config.get("api_key")
        model = config.get("model", "dall-e-3")
        
        return OpenAIImageClient(
            api_key=api_key,
            model=model
        )