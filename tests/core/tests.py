import os, unittest, tempfile, signalqueue

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase

from PIL import Image
from core.models import TestModel

# this next thing is to avoid a glitch in nose -- see also: 
# https://github.com/jbalogh/django-nose/issues/15#issuecomment-1033686
TestModel._meta.get_all_related_objects()

class SonnarTests(TestCase):
    def generate_image(self):
        tmp = tempfile.TemporaryFile()
        Image.new('RGB', (800, 600)).save(tmp, 'JPEG')
        tmp.seek(0)
        return tmp
    
    def setUp(self):
        signalqueue.autodiscover()
        self.p = TestModel()
        img = self.generate_image()
        self.p.modfile.save('test.jpg', ContentFile(img.read()), save=False)
        self.p.save()
        img.close()
    
    def test_base_feature(self):
        mf = self.p.modfile
        one_feature = mf.a_feature
        one_other_feature = mf.another_feature
        
        print "\none feature: %s" % one_feature
        print "\none other feature: %s\n" % one_other_feature
    
    def test_pil_feature(self):
        print "PIL Image: %s" % self.p.modfile.pil
    
    def test_width_height_features(self):
        #print "PIL Image: %s" % self.p.modfile.pil
        print "*** Width: %s" % self.p.modfile.width
        print "*** Height: %s" % self.p.modfile.height
    
    def test_opencv_feature_without_source(self):
        #print "PIL Image: %s" % self.p.modfile.pil
        print "*** OpenCV (via filesystem): %s" % self.p.modfile.cv2
    
    def test_opencv_feature_with_source(self):
        #print "PIL Image: %s" % self.p.modfile.pil
        print "*** OpenCV (via PIL source): %s" % self.p.modfile.cv
        
    
    def _test_save_image(self):
        img = self.generate_image()
        path = self.p.image.path
        self.p.save_image('test2.jpg', ContentFile(img.read()))
        self.failIf(os.path.isfile(path))
        path = self.p.image.path
        img.seek(0)
        self.p.save_image('test.jpg', ContentFile(img.read()))
        self.failIf(os.path.isfile(path))
        img.close()
    
    def tearDown(self):
        path = self.p.modfile.path
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
        #os.removedirs(os.path.join(settings.MEDIA_ROOT, 'images'))
        self.p.delete()
        #pass
    
    
    