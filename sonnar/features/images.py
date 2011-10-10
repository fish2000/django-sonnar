
import cv
from sonnar.features.base import Feature

try:
    from PIL import Image
except ImportError:
    import Image

class PILImage(Feature):
    def prepare_value(self, instance, field_file, field_name, source=None):
        if field_file.storage.exists(field_file.name):
            return Image.open(field_file.storage.open(field_file.name))
        return None

class WidthFeature(Feature):
    default = 0
    def prepare_value(self, instance, field_file, field_name, source=None):
        if source is None:
            return self.default
        return source.get_value().size[0]

class HeightFeature(Feature):
    default = 0
    def prepare_value(self, instance, field_file, field_name, source=None):
        if source is None:
            return self.default
        return source.get_value().size[1]

class OpenCVHandle(Feature):
    def prepare_value(self, instance, field_file, field_name, source=None):
        if source is None:
            return cv.LoadImage(field_file.path)
        else:
            pilim = source.get_value()
            cvim = cv.CreateImageHeader(pilim.size, cv.IPL_DEPTH_8U, 1)
            cv.SetData(cvim, pilim.tostring())
            return cvim
        print "WTF!"
        return None
