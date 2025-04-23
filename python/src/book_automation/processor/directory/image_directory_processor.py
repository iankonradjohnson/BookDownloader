from abc import abstractmethod, ABC


class ImageDirectoryProcessor(ABC):
    @abstractmethod
    def inference_command(self, input_dir: str, output_dir: str) -> str:
        pass