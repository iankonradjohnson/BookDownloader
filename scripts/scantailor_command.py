#!/usr/bin/env python3
"""
Script to run ScanTailor with the specified command line parameters.
This is a wrapper around the ScanTailor command line tool that handles
common errors and provides a more user-friendly interface.
"""

import os
import argparse
import subprocess
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Parse arguments and run ScanTailor command."""
    parser = argparse.ArgumentParser(description='Run ScanTailor with specified parameters')
    parser.add_argument('--input-dir', required=True, help='Input directory containing images')
    parser.add_argument('--output-dir', required=True, help='Output directory for processed images')
    parser.add_argument('--book-type', default='text_heavy', choices=['standard', 'text_heavy', 'image_heavy'], 
                        help='Type of book to process')
    parser.add_argument('--dpi', type=int, default=600, help='Output DPI')
    parser.add_argument('--color-mode', default='mixed', 
                        choices=['black_white', 'color_grayscale', 'mixed'], 
                        help='Color mode')
    parser.add_argument('--compression', default='lzw', 
                        choices=['none', 'lzw', 'deflate'], 
                        help='TIFF compression')
    parser.add_argument('--force-color', action='store_true', 
                        help='Force RGB color space')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    if not os.path.isdir(args.input_dir):
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Build ScanTailor command
    cmd = build_scantailor_command(args)
    
    # Print command for user reference
    cmd_str = ' '.join(cmd)
    logger.info(f"Running command: {cmd_str}")
    print(f"\nCommand:\n{cmd_str}\n")
    
    # Run the command
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        logger.info("ScanTailor processing completed successfully")
        print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        logger.error(f"ScanTailor processing failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        print(f"Error: {e}")
        print(e.stderr)
        return 1

def build_scantailor_command(args):
    """Build the ScanTailor command from the provided arguments."""
    # Basic command
    cmd = ["scantailor-universal-cli"]
    
    # Layout and deskew settings
    cmd.extend(["--layout=auto", "--deskew=off"])
    
    # Content detection based on book type
    content_detection = "normal"
    if args.book_type == 'text_heavy':
        content_detection = "aggressive"
    elif args.book_type == 'image_heavy':
        content_detection = "cautious"
        
    cmd.append(f"--content-detection={content_detection}")
    
    # Margins based on book type
    if args.book_type == 'text_heavy':
        cmd.extend([
            "--margins-left=5",
            "--margins-right=5",
            "--margins-top=5",
            "--margins-bottom=5"
        ])
    elif args.book_type == 'image_heavy':
        cmd.append("--margins=10")
    else:
        cmd.append("--margins=5")
    
    # Add common settings
    cmd.extend([
        "--white-margins",
        "--normalize-illumination",
    ])
    
    # Despeckle based on book type
    despeckle = "normal"
    if args.book_type == 'image_heavy':
        despeckle = "cautious"
    cmd.append(f"--despeckle={despeckle}")
    
    # Color mode and output settings
    cmd.extend([
        f"--color-mode={args.color_mode}",
        f"--output-dpi={args.dpi}",
        f"--tiff-compression={args.compression}"
    ])
    
    # Advanced settings for text-heavy books
    if args.book_type == 'text_heavy':
        cmd.extend([
            "--enable-page-detection",
            "--enable-fine-tuning"
        ])
    
    # Color handling
    if args.force_color:
        cmd.append("--tiff-force-rgb")
    else:
        cmd.append("--tiff-force-keep-color-space")
    
    # Add input and output directories
    cmd.append(args.input_dir)
    cmd.append(args.output_dir)
    
    return cmd

if __name__ == "__main__":
    sys.exit(main())