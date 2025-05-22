#!/usr/bin/env python3
"""
Script to generate images using OpenAI's models with support for reference images.
"""

import os
import sys
import argparse
import logging
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv
import requests
from typing import List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate images with OpenAI models")
    
    parser.add_argument(
        "--prompt", 
        type=str, 
        required=True, 
        help="Text description of the image to generate"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./generated_images", 
        help="Directory to save generated images"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="dall-e-3",
        choices=["dall-e-3", "gpt-image-1"], 
        help="Model to use for generation (default: dall-e-3)"
    )
    
    parser.add_argument(
        "--size", 
        type=str, 
        default="1024x1024", 
        choices=["1024x1024", "1024x1792", "1792x1024", "a4"],
        help="Image size for DALL-E 3 (default: 1024x1024, a4 uses portrait format)"
    )
    
    parser.add_argument(
        "--quality", 
        type=str, 
        default="standard", 
        choices=["standard", "hd"],
        help="Image quality for DALL-E models (default: standard)"
    )
    
    parser.add_argument(
        "--style", 
        type=str, 
        default="vivid", 
        choices=["vivid", "natural"],
        help="Image style for DALL-E models (default: vivid)"
    )
    
    parser.add_argument(
        "--filename", 
        type=str, 
        help="Custom filename for the generated image"
    )
    
    parser.add_argument(
        "--reference-images",
        type=str,
        nargs="+",
        help="Paths to reference images to guide the generation (GPT-image-1 only, up to 4 images)"
    )
    
    return parser.parse_args()

def encode_image_to_base64(image_path):
    """Encode an image to base64 format."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

def generate_with_dalle(client, prompt, size, quality, style):
    """Generate images using DALL-E models."""
    logger.info(f"Generating image with DALL-E 3, prompt: '{prompt}'")
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
        style=style
    )
    
    image_url = response.data[0].url
    return image_url

def generate_with_gpt_image(client, prompt, reference_images: Optional[List[str]] = None):
    """
    Generate images using GPT-Image-1 model, with optional reference images.
    
    Args:
        client: OpenAI client
        prompt: Text prompt for image generation
        reference_images: Optional list of image file paths to use as references
    """
    logger.info(f"Generating image with GPT-Image-1, prompt: '{prompt}'")
    
    # Basic parameters
    params = {
        "model": "gpt-image-1",
        "prompt": prompt,
    }
    
    # Add reference images if provided
    if reference_images and len(reference_images) > 0:
        # OpenAI allows up to 4 reference images
        if len(reference_images) > 4:
            logger.warning("More than 4 reference images provided. Only the first 4 will be used.")
            reference_images = reference_images[:4]
        
        logger.info(f"Using {len(reference_images)} reference images")
        
        # Prepare reference images
        encoded_images = []
        for img_path in reference_images:
            base64_image = encode_image_to_base64(img_path)
            if base64_image:
                encoded_images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
            else:
                logger.warning(f"Skipping invalid reference image: {img_path}")
        
        if encoded_images:
            params["reference_images"] = encoded_images
    
    # Generate the image
    result = client.images.generate(**params)
    
    image_base64 = result.data[0].b64_json
    return image_base64

def main():
    """Main function."""
    # Load environment variables
    load_dotenv()
    
    args = parse_args()
    
    # Create output directory if it doesn't exist
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Create OpenAI client
        client = OpenAI()
        
        # Prepare filename
        if args.filename:
            base_filename = args.filename
            if not base_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                base_filename += '.png'
        else:
            base_filename = "generated_image.png"
        
        image_path = os.path.join(args.output_dir, base_filename)
        
        # Check reference images - only supported for GPT-Image-1
        reference_images = args.reference_images
        if reference_images and args.model != "gpt-image-1":
            logger.warning("Reference images are only supported with the gpt-image-1 model. Ignoring reference images.")
            reference_images = None
        
        # Generate image based on selected model
        if args.model == "gpt-image-1":
            # Generate with GPT-Image-1 (base64 output)
            image_base64 = generate_with_gpt_image(client, args.prompt, reference_images)
            image_bytes = base64.b64decode(image_base64)
            
            # Save image directly from base64
            with open(image_path, "wb") as f:
                f.write(image_bytes)
                
            logger.info(f"Image saved to {image_path}")
            
        else:
            # Generate with DALL-E 3 (URL output)
            # Handle A4 size request
            size = args.size
            if args.size.lower() == "a4":
                size = "1024x1792"  # Portrait format similar to A4
                
            image_url = generate_with_dalle(
                client, 
                args.prompt, 
                size, 
                args.quality, 
                args.style
            )
            
            # Download and save image
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            with open(image_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Image saved to {image_path}")
        
        # Return path as JSON for easy parsing
        print(json.dumps({"image_path": image_path}))
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()