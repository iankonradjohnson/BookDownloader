#!/usr/bin/env python3
"""
Extract Archive Script

A standalone script for extracting archives (ZIP, TAR, etc.) with progress tracking
and optional cleanup. Can be used independently of the BookDownloader system.

Usage:
    python extract_archives.py --input /path/to/archives --output /path/to/output
    python extract_archives.py --config /path/to/config.yml
"""

import os
import sys
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from python.src.util.archive_manager import ArchiveManager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Extract archives with progress tracking')
    
    # Config file option
    parser.add_argument('-c', '--config', help='Path to configuration YAML file')
    
    # Direct configuration options
    parser.add_argument('-i', '--input', help='Path to archive file or directory containing archives')
    parser.add_argument('-o', '--output', help='Path to output directory (default: same as input)')
    parser.add_argument('--no-subfolders', action='store_true', 
                        help='Do not create subfolders based on archive identifiers')
    parser.add_argument('--keep-archives', action='store_true',
                        help='Do not move archives to trash after extraction')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Search directories recursively for archives')
    parser.add_argument('-j', '--jobs', type=int, default=1,
                        help='Number of parallel extraction jobs (default: 1)')
    
    return parser.parse_args()


def create_config_from_args(args):
    """Create a configuration dictionary from command line arguments."""
    config = {}
    
    if args.input:
        config['input_path'] = args.input
    if args.output:
        config['output_base_path'] = args.output
    if args.no_subfolders:
        config['use_identifier_folders'] = False
    if args.keep_archives:
        config['trash_archives'] = False
    if args.recursive:
        config['recursive'] = True
    
    return config


def extract_archive_with_progress(archive_manager, archive_path, progress_bar):
    """Extract a single archive with progress tracking."""
    try:
        result = archive_manager.extract_single_archive(archive_path)
        progress_bar.update(1)
        return result
    except Exception as e:
        logging.error(f"Error extracting {archive_path}: {e}")
        progress_bar.update(1)
        return False


def main():
    """Main function for the archive extraction script."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = {}
    if args.config:
        config = ArchiveManager.load_config_from_file(args.config)
    
    # Override with command line arguments
    config.update(create_config_from_args(args))
    
    # Validate required configuration
    if 'input_path' not in config:
        logging.error("No input path specified. Use --input or --config")
        return 1
    
    # Create archive manager
    archive_manager = ArchiveManager(config)
    
    # Find archives
    archive_files = archive_manager.find_archives()
    if not archive_files:
        logging.warning(f"No archives found at {config['input_path']}")
        return 0
    
    print(f"Found {len(archive_files)} archives to extract")
    
    # Process archives in parallel if requested
    if args.jobs > 1 and len(archive_files) > 1:
        print(f"Extracting with {args.jobs} parallel jobs")
        
        # Progress bar for overall extraction
        with tqdm(total=len(archive_files), desc="Extracting archives") as pbar:
            with ThreadPoolExecutor(max_workers=args.jobs) as executor:
                # Submit extraction tasks
                futures = [
                    executor.submit(extract_archive_with_progress, archive_manager, path, pbar)
                    for path in archive_files
                ]
                
                # Collect results
                results = [future.result() for future in futures]
                success_count = sum(1 for result in results if result)
    else:
        # Process archives sequentially with progress bar
        success_count = 0
        with tqdm(total=len(archive_files), desc="Extracting archives") as pbar:
            for archive_path in archive_files:
                if archive_manager.extract_single_archive(archive_path):
                    success_count += 1
                pbar.update(1)
    
    # Report results
    failed_count = len(archive_files) - success_count
    print(f"Extraction complete: {success_count} successful, {failed_count} failed")
    
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())