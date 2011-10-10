
import hashlib

from django.db import models
from django.core.files.storage import FileSystemStorage

from sonnar.modelfields import FileHashField, ModularField
from sonnar.features.base import Feature
from sonnar.features.images import PILImage, WidthFeature, HeightFeature, OpenCVHandle
from sonnar.features.hashing import SHA1, HashFeature, SHA1Feature

class TestModel(models.Model):
    id = models.AutoField(primary_key=True)
    modfile = ModularField(name='modfile',
        upload_to="modfiles",
        features=(
            Feature('a_feature'),
            Feature('another_feature'),
        ),
        verbose_name="Modular File",
        blank=True,
        null=True)

class TestHashingModel(models.Model):
    id = models.AutoField(primary_key=True)
    modfile = ModularField(name='modfile',
        upload_to="modfiles",
        features=(
            SHA1('filehash', preload=True),
            SHA1Feature('shaaaa1', preload=True),
            
            HashFeature('featurehash', preload=True),
            HashFeature('sha1feature', preload=True,
                hasher=lambda data: hashlib.sha1(data).hexdigest()),
        ),
        verbose_name="Modular File",
        blank=True,
        null=True)


class TestCustomHashingModel(models.Model):
    id = models.AutoField(primary_key=True)
    modfile = ModularField(name='modfile',
        upload_to="modfiles",
        
        features=(
            HashFeature('sha1',
                hasher=lambda data: hashlib.sha1(data).hexdigest()),
            HashFeature('md5',
                hasher=lambda data: hashlib.md5(data).hexdigest()),
            HashFeature('sha512',
                hasher=lambda data: hashlib.sha512(data).hexdigest()),
            ),
        
        verbose_name="Modular File",
        blank=True,
        null=True)


class TestImageModel(models.Model):
    id = models.AutoField(primary_key=True)
    
    filehash = FileHashField(verbose_name="File data hash",
        unique=False,
        editable=True,
        blank=True,
        null=True)
    
    modfile = ModularField(name='modfile',
        upload_to="modfiles",
        storage=FileSystemStorage(),
        hash_field='filehash',
        features=(
            PILImage('pil', preload=True),
            
            WidthFeature('width', source='pil'),
            HeightFeature('height', source='pil'),
            OpenCVHandle('cv', source='pil'),
            OpenCVHandle('cv2'),
            
            Feature('a_feature'),
            Feature('another_feature'),
        ),
        verbose_name="Modular File",
        blank=True,
        null=True)

