import os
import requests
import logging
from typing import Optional, List, Dict, Any, Union
from openai import OpenAI

class OpenAIImageClient:
    """
    Client for generating images using OpenAI's DALL-E models.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "dall-e-3"):
        """
        Initialize the OpenAI Image Client.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable
            model: The model to use for image generation (default: dall-e-3)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either as an argument or as OPENAI_API_KEY environment variable")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
    
    def generate_image(self, 
                     prompt: str, 
                     size: str = "1024x1024",
                     quality: str = "standard",
                     n: int = 1,
                     style: str = "vivid",
                     output_dir: Optional[str] = None) -> List[str]:
        """
        Generate image(s) based on the prompt.
        
        Args:
            prompt: The text description of the image to generate
            size: Image size (1024x1024, 1024x1792, or 1792x1024)
            quality: Image quality (standard or hd)
            n: Number of images to generate (1-10)
            style: The style of the generated images (vivid or natural)
            output_dir: If specified, saves images to this directory
            
        Returns:
            List of image URLs or local file paths (if output_dir specified)
        """
        try:
            self.logger.info(f"Generating image with prompt: '{prompt}'")
            
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
                style=style
            )
            
            image_urls = [item.url for item in response.data]
            
            # If output_dir is specified, download and save the images
            if output_dir and image_urls:
                os.makedirs(output_dir, exist_ok=True)
                saved_paths = []
                
                for i, url in enumerate(image_urls):
                    image_path = os.path.join(output_dir, f"generated_image_{i}.png")
                    self._download_image(url, image_path)
                    saved_paths.append(image_path)
                
                return saved_paths
            
            return image_urls
            
        except Exception as e:
            self.logger.error(f"Error generating image: {e}")
            raise
    
    def _download_image(self, url: str, save_path: str) -> None:
        """
        Download an image from URL and save to local file.
        
        Args:
            url: The URL of the image
            save_path: Local path to save the image
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            self.logger.info(f"Image saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error downloading image: {e}")
            raise