#!/usr/bin/env python3
"""
MCP-compatible tool for generating images using OpenAI's DALL-E models.
This can be used directly by Claude as an MCP tool.
"""

import os
import sys
import logging
import json
import requests
import tempfile
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPImageGenerator:
    """MCP-compatible image generator class."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        self.client = OpenAI()
    
    def generate(self, 
                prompt,
                model="dall-e-3",
                size="1024x1024",
                quality="standard",
                style="vivid",
                output_format="url"):
        """
        Generate an image based on the provided prompt.
        
        Args:
            prompt (str): Text description of the image to generate
            model (str): DALL-E model to use (default: dall-e-3)
            size (str): Image size (1024x1024, 1024x1792, or 1792x1024)
            quality (str): Image quality (standard or hd)
            style (str): Image style (vivid or natural)
            output_format (str): Output format (url or b64_json)
            
        Returns:
            dict: Dictionary containing the image information
        """
        try:
            logger.info(f"Generating image with prompt: '{prompt}'")
            
            # Generate image
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1,
                response_format=output_format
            )
            
            # Process response based on output format
            if output_format == "url":
                image_url = response.data[0].url
                
                # Create a temporary file and save the image
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    # Download the image
                    img_response = requests.get(image_url, stream=True)
                    img_response.raise_for_status()
                    
                    for chunk in img_response.iter_content(chunk_size=8192):
                        tmp.write(chunk)
                    
                    image_path = tmp.name
                
                return {
                    "success": True,
                    "file_path": image_path,
                    "url": image_url,
                    "prompt": prompt,
                    "model": model,
                    "size": size,
                    "quality": quality,
                    "style": style
                }
            
            elif output_format == "b64_json":
                image_data = response.data[0].b64_json
                
                # Create a temporary file and save the image
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(base64.b64decode(image_data))
                    image_path = tmp.name
                
                return {
                    "success": True,
                    "file_path": image_path,
                    "data": image_data[:20] + "...",  # Truncated for response
                    "prompt": prompt,
                    "model": model,
                    "size": size,
                    "quality": quality,
                    "style": style
                }
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Demonstrate MCP tool functionality."""
    # Example prompt
    example_prompt = "A beautiful sunset over mountains"
    
    # Create generator
    generator = MCPImageGenerator()
    
    # Generate image
    result = generator.generate(
        prompt=example_prompt,
        size="1024x1024",
        quality="standard",
        style="vivid"
    )
    
    # Output result
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()