# BookDownloader Project Notes

## Code Style Guidelines
- Factory pattern used for dependency injection
- Services take explicit parameters rather than config dictionaries
- Configuration extraction happens in factory classes

## Key Code Examples

### ScanTailor Service Usage
```python
# Create a ScanTailor service using the factory
from python.src.factory import ScanTailorFactory

config = {
    'enabled': True,
    'book_type': 'text_heavy',
    'dpi': 600
}

# The factory handles config extraction
scantailor_service = ScanTailorFactory.create_service(config)

# Use the service
scantailor_service.process_images(input_dir, output_dir)
```