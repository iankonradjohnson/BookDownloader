import os


class ZipUtil:
    @staticmethod
    def extract_and_rename(output_dir, folder_name):
        named_output_dir = os.path.join(output_dir, folder_name)
        os.makedirs(named_output_dir, exist_ok=True)
        return named_output_dir