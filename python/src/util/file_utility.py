
class FileUtility:

    @staticmethod
    def create_image_name(i):
        return f"image_{str.zfill(str(i), 4)}.png"