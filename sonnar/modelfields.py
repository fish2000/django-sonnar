
import uuid, hashlib
from django.db.models import fields
from django.db.models.fields import files
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy

from django.db import models
from django.db.models import signals
from sonnar.features.base import Feature


class FileHashField(fields.CharField):
    """
    Store the sha1 of the file we're looking at.
    
    See also:
    https://github.com/fish2000/django-imagekit/blob/develop/imagekit/modelfields.py#L449
    
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('max_length', 40)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        super(FileHashField, self).__init__(*args, **kwargs)


class ModularFile(files.File):
    """ django.core.files.File subclass """
    @staticmethod
    def _calculate_hash(hshdata):
        return hashlib.sha1(hshdata).hexdigest()
    
    def _load_file_hash(self):
        if not hasattr(self, "_file_hash"):
            close = self.closed
            self.open()
            pos = self.tell()
            dat = self.read()
            self._file_hash = ModularFile._calculate_hash(dat)
            
            if close:
                self.close()
            else:
                self.seek(pos)
        return self._file_hash
    
    def _get_hsh(self):
        return self._load_file_hash()
    hsh = property(_get_hsh)


class ModularFileDescriptor(files.FileDescriptor):
    """ django.db.models.fields.files.FileDescriptor subclass """
    def __set__(self, instance, value):
        previous_file = instance.__dict__.get(self.field.name)
        super(ModularFileDescriptor, self).__set__(instance, value)
        if previous_file is not None:
            self.field.update_data_fields(instance, force=True)


class FeaturefulFieldFile(files.FieldFile):
    def __new__(cls, instance, field, name):
        supercls = files.FieldFile
        
        def __init__(mself, minstance, mfield, mname):
            supercls.__init__(mself, minstance, mfield, mname)
        
        outdic = dict(cls.__dict__)
        outdic.update({
            '_features': field._features,
            '__init__': __init__,
        })
        
        OutCls = type(cls.__name__, (supercls,), outdic)
        out_field_file = OutCls(instance, field, name)
        
        for feature in field._features.values():
            feature.contribute_to_field(out_field_file,
                instance, field.name, feature.name)
        
        return out_field_file


class ModularFieldFile(FeaturefulFieldFile, ModularFile):
    """ django.db.models.fields.files.FileDescriptor subclass """
    
    def __init__(self, *args, **kwargs):
        FeaturefulFieldFile.__init__(self, *args, **kwargs)
        ModularFile.__init__(self, *args, **kwargs)
    
    def save(self, name, content, save=True):
        if hasattr(self, '_file'):
            files.FieldFile.delete(self, save=save)
        files.FieldFile.save(self, name, content, save=save)
    
    def delete(self, save=True):
        if hasattr(self, '_file_hash'):
            del self._file_hash
        super(ModularFieldFile, self).delete(save)
    
    def _load_file_hash(self):
        if not hasattr(self, "_file_hash"):
            close = self.closed
            self.open()
            pos = self.tell()
            dat = self.read()
            self._file_hash = ModularFile._calculate_hash(dat)
            
            if close:
                self.close()
            else:
                self.seek(pos)
        return self._file_hash
    
    @property
    def hsh(self):
        return self._load_file_hash()


class ModularField(files.FileField):
    """ django.db.models.fields.files.FileField subclass """
    attr_class = ModularFieldFile
    descriptor_class = ModularFileDescriptor
    description = ugettext_lazy("Modular file path")
    _features = {}
    
    def __init__(self, verbose_name=None, name=None, hash_field=None, **kwargs):
        self.hash_field = hash_field
        
        features = list(kwargs.pop('features', []))
        for feature in features:
            if isinstance(feature, Feature):
                if feature.unique:
                    if feature.__class__ in [f.__class__ for f in self.features]:
                        raise ImproperlyConfigured("%s is a unique feature -- you can only add one per %s" % (
                            feature.__class__.__name__, self.__class__.__name__))
                self._features.update({ feature.name: feature })
            else:
                raise ImproperlyConfigured("%s isn't a valid feature." % (
                    feature.__class__.__name__,))
        
        self.__class__.__base__.__init__(self, verbose_name, name, **kwargs)
    
    def contribute_to_class(self, cls, name):
        super(ModularField, self).contribute_to_class(cls, name)
        
        for feature in self._features.values():
            feature.contribute_to_class(cls, name)
        
        signals.post_init.connect(self.update_data_fields, sender=cls,
            dispatch_uid="post-init-update-data-fields")
        
        signals.post_save.connect(self.update_data_fields, sender=cls,
            dispatch_uid="post-save-update-data-fields")
        
    
    def preload_features(self, instance, **kwargs):
        if instance.pk:
            for feature in self._features.values():
                if feature.preload:
                    feature._prepare_value(
                        instance=instance,
                        field_file=self,
                        field_name=self.name,
                        feature_name=feature.name,
                    )
    
    def update_data_fields(self, instance, force=False, *args, **kwargs):
        if not self.hash_field:
            return
        
        ffile = getattr(instance, self.attname)
        if not ffile and not force:
            return
        
        fields_filled = not(
            (self.hash_field and not getattr(instance, self.hash_field))
        )
        if fields_filled and not force:
            return
        
        try:
            if ffile:
                if ffile.hsh:
                    hsh = ffile.hsh
                else:
                    hsh = None
            else:
                hsh = None
        except ValueError:
            hsh = None
        
        if self.hash_field:
            setattr(instance, self.hash_field, hsh)
