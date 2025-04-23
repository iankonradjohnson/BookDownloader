from dataclasses import dataclass

from book_automation.processor.directory.image_directory_processor import ImageDirectoryProcessor


@dataclass
class RealESRGANProcessor(ImageDirectoryProcessor):
    model: str = "net_g_1000000"
    tile: int = 1000
    tile_pad: int = 0
    postscale: float = 0.75

    def inference_command(self, input_dir: str, output_dir: str) -> str:
        return (
            f"python inference_realesrgan.py "
            f"-i {input_dir} -o {output_dir} -n {self.model} "
            f"-t {self.tile} --tile_pad {self.tile_pad} -p {self.postscale}"
        )