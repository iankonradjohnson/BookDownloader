# BookDownloader

A utility for downloading books and other documents from various online sources.

## Features

- Download books from multiple sources including Archive.org
- Support for various file formats including PDF and images
- Archive extraction support for ZIP and TAR files
- Automatic archive cleanup (moves to system trash)
- Batch downloading capability
- Real-time progress tracking for downloads and extractions
- Standalone archive extraction tool

## Archive Extraction

The system automatically extracts downloaded archive files (ZIP, TAR) to the output folder. The extraction happens in a subfolder named after the archive identifier. After successful extraction, the original archive file is moved to the system trash (recycle bin on Windows). 

Supported archive formats:
- ZIP files (.zip)
- TAR files (.tar, .tar.gz, .tgz, .tar.bz2)

You can control the behavior with the following parameters:
- `extract_archives` (default: `True`) - Enable/disable automatic extraction
- `trash_archives` (default: `True`) - Enable/disable moving archives to trash after extraction

The `trash_archives` option uses system-appropriate methods:
- macOS: Uses AppleScript to move to Finder trash
- Windows: Uses the winshell library to move to Recycle Bin
- Linux: Uses trash-cli if available, otherwise creates a .trash directory
- Fallback: Creates a local .trash directory in the same folder as the archive

## Progress Tracking

BookDownloader provides detailed progress tracking throughout the download and extraction process:

- **Overall progress**: Shows the total number of books being processed and current progress
- **Download progress**: Individual progress bars for each file being downloaded, showing speed and ETA
- **Extraction progress**: Detailed progress for archive extraction, showing file-by-file progress
- **Trash confirmation**: Confirmation when archives are moved to trash after extraction

This makes it easy to monitor long-running downloads of large book archives.

## Standalone Archive Extraction Tool

A standalone archive extraction tool is included that can be used independently of the main BookDownloader system. This is useful for extracting archives that have already been downloaded or for batch processing existing archives.

### Usage

```bash
# Basic usage with command line arguments
python scripts/extract_archives.py --input /path/to/archives --output /path/to/output

# Advanced options
python scripts/extract_archives.py --input /path/to/archives --output /path/to/output --recursive --jobs 4

# Using a configuration file
python scripts/extract_archives.py --config config/archive_extractor_config.yml
```

### Command Line Options

- `--input` / `-i`: Path to archive file or directory containing archives
- `--output` / `-o`: Path to output directory (default: same as input)
- `--config` / `-c`: Path to YAML configuration file
- `--no-subfolders`: Do not create subfolders based on archive identifiers
- `--keep-archives`: Do not move archives to trash after extraction
- `--recursive` / `-r`: Search directories recursively for archives
- `--jobs` / `-j`: Number of parallel extraction jobs (default: 1)

### Configuration File

Example configuration (see `config/archive_extractor_config.yml`):

```yaml
# Input/Output Paths
input_path: "/path/to/archives" 
output_base_path: "/path/to/output"

# Extraction Options
use_identifier_folders: true  # Create subfolders per archive
trash_archives: true          # Move archives to trash after extraction
recursive: false              # Whether to search subdirectories
```

The standalone extractor supports all the same features as the integrated extractor, including progress tracking and archive cleanup.