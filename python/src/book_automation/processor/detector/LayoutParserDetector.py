import PIL
from PIL import Image
from layoutparser.models import Detectron2LayoutModel
from layoutparser.visualization import draw_box

from book_automation.processor.detector.layout_detector import LayoutDetector
import layoutparser as lp


class LayoutParserDetector(LayoutDetector):

    def __init__(self):
        self.model: Detectron2LayoutModel = Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config')

    def detect(self, img: Image.Image):
        layout = self.model.detect(img)
        result = draw_box(img, layout, box_width=3)
        result.show()

