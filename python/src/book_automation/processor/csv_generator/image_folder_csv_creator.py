import os
import csv
from pathlib import Path
from typing import List


class ImageFolderCsvCreator:
    
    def __init__(
        self,
        img_dir: Path,
        csv_path: Path,
    ):
        self.img_dir = Path(img_dir)
        self.csv_path = Path(csv_path)
    
    def _find_images(self) -> List[Path]:
        extensions = ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp']
        
        return sorted([
            p for p in self.img_dir.iterdir() 
            if p.is_file() and p.suffix.lower() in extensions
        ])
    
    def create(self) -> Path:
        images = self._find_images()
        
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        with open(self.csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(['Name', '@images'])
            
            for img_path in images:
                writer.writerow([
                    img_path.name,
                    str(img_path)
                ])
        
        return self.csv_path