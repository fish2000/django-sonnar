import os, unittest, tempfile, signalqueue, random

from django.conf import settings
from django.core.files.base import ContentFile
from django.test import TestCase

from PIL import Image
from core.models import TestModel, TestImageModel, TestHashingModel, TestCustomHashingModel

# this next thing is to avoid a glitch in nose -- see also: 
# https://github.com/jbalogh/django-nose/issues/15#issuecomment-1033686
TestModel._meta.get_all_related_objects()
TestImageModel._meta.get_all_related_objects()
TestHashingModel._meta.get_all_related_objects()
TestCustomHashingModel._meta.get_all_related_objects()

random.seed()


class SonnarBaseTest(TestCase):
    
    modl = TestModel
    
    def generate_image(self):
        w = 800
        h = 600
        tmp = tempfile.TemporaryFile()
        img = Image.new('RGB', (w, h))
        
        for i in xrange(1, 10):
            img.putpixel((
                random.randint(10, 700),
                random.randint(10, 500),
                ), (230, 30+i, 29))
        
        img.save(tmp, 'JPEG')
        tmp.seek(0)
        return tmp
    
    def setUp(self):
        signalqueue.autodiscover()
        self.p = self.modl()
        img = self.generate_image()
        self.p.modfile.save('test.jpg', ContentFile(img.read()), save=False)
        self.p.save()
        img.close()
    
    def tearDown(self):
        path = self.p.modfile.path
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
        os.removedirs(os.path.join(settings.MEDIA_ROOT, 'modfiles'))
        self.p.delete()


class HasherTests(SonnarBaseTest):
    
    modl = TestHashingModel
    
    def test_sha1_data_hash(self):
        self.p.save()
        print "HASH: %s" % self.p.modfile.datahash
        print "HASH: %s" % self.p.modfile.sha1
        print "HASH: %s" % self.p.modfile.sha1feature
        
        self.p.save()
        print "HASH: %s" % self.p.modfile.datahash
        print "HASH: %s" % self.p.modfile.sha1
        print "HASH: %s" % self.p.modfile.sha1feature
    
    def test_featurehash_base_class_two(self):
        #self.p.save()
        self.assertEqual(
            self.p.modfile.datahash,
            self.p.modfile.sha1,
        )
    
    def test_featurehash_base_class_three(self):
        #self.p.save()
        self.assertEqual(
            self.p.modfile.datahash,
            self.p.modfile.sha1feature,
        )
    
    def test_featurehash_base_class_four(self):
        #self.p.save()
        self.assertEqual(
            self.p.modfile.sha1,
            self.p.modfile.datahash,
        )

class CustomHasherTests(SonnarBaseTest):
    
    modl = TestCustomHashingModel
    
    def test_custom_hashers(self):
        print "SHA1: %s" % self.p.modfile.sha1
        print "MD5: %s" % self.p.modfile.md5
        print "SHA512: %s" % self.p.modfile.sha512
        
        print "SHA1: %s" % self.p.modfile.sha1
        print "MD5: %s" % self.p.modfile.md5
        print "SHA512: %s" % self.p.modfile.sha512
        
        print "SHA1: %s" % self.p.modfile.sha1
        print "MD5: %s" % self.p.modfile.md5
        print "SHA512: %s" % self.p.modfile.sha512


class SonnarImageTests(SonnarBaseTest):
    
    modl = TestImageModel
    
    def test_base_feature(self):
        mf = self.p.modfile
        one_feature = mf.a_feature
        one_other_feature = mf.another_feature
        
        #print "\none feature: %s" % one_feature
        #print "\none other feature: %s\n" % one_other_feature
        self.assertTrue('a_feature' in one_feature)
        self.assertTrue('another_feature' in one_other_feature)
    
    def test_pil_feature(self):
        self.assertTrue(isinstance(self.p.modfile.pil, Image.Image))
    
    def test_width_height_features(self):
        self.assertTrue(int(self.p.modfile.width) == 800)
        self.assertTrue(int(self.p.modfile.height) == 600)
    
    def test_opencv_feature_without_source(self):
        print "*** OpenCV (via filesystem): %s" % self.p.modfile.cvfile
    
    def test_opencv_feature_with_source(self):
        print "*** OpenCV (via PIL source): %s" % self.p.modfile.cv
    
    def test_save_image_data(self):
        img = self.generate_image()
        path = self.p.modfile.path
        self.p.modfile.save('test2.jpg', ContentFile(img.read()))
        self.failIf(os.path.isfile(path))
        path = self.p.modfile.path
        img.seek(0)
        self.p.modfile.save('test.jpg', ContentFile(img.read()))
        self.failIf(os.path.isfile(path))
        img.close()
    
    def test_content_hash(self):
        img = self.generate_image()
        img2 = self.generate_image()
        img3 = self.generate_image()
        
        hsh = self.p.filehash
        self.p.modfile.save('test2.jpg', ContentFile(img2.read()))
        self.failIf(hsh == self.p.filehash)
        hsh = self.p.filehash
        img.seek(0)
        self.p.modfile.save('test.jpg', ContentFile(img3.read()))
        self.failIf(hsh == self.p.filehash)
        img.close()
    