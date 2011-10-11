
import hashlib
from sonnar.features.base import Feature
from sonnar.modelfields import ModularFile

class SHA1(Feature):
    def prepare_value(self, instance, field_file, field_name, feature_name, source=None):
        ifile = getattr(instance, field_name)
        if ifile.storage.exists(ifile.name):
            close = ifile.closed
            dfile = ifile.storage.open(ifile.name)
            pos = dfile.tell()
            dat = dfile.read()
            
            hashout = ModularFile._calculate_hash(dat)
            
            if close:
                dfile.close()
            else:
                dfile.seek(pos)
            return hashout
        return None

class HashFeature(Feature):
    
    hasher = staticmethod(lambda data: ModularFile._calculate_hash(data))
    
    def __init__(self, *args, **kwargs):
        hasher = kwargs.pop('hasher', None)
        if hasher is not None:
            self.hasher = hasher
        super(HashFeature, self).__init__(*args, **kwargs)
    
    def prepare_value(self, instance, field_file, field_name, feature_name, source=None):
        ifile = getattr(instance, field_name)
        if ifile.storage.exists(ifile.name):
            
            close = ifile.closed
            dfile = ifile.storage.open(ifile.name)
            pos = dfile.tell()
            dat = dfile.read()
            
            hashout = self.hasher(dat)
            
            if close:
                dfile.close()
            else:
                dfile.seek(pos)
            return hashout
        return None

class SHA1Feature(HashFeature):
    @staticmethod
    def hasher(data):
        return hashlib.sha1(data).hexdigest()


class SHA1Dogg(HashFeature):
    hasher = staticmethod(lambda data: hashlib.sha1(data).hexdigest())



