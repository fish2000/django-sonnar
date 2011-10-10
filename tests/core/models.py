
from django.db import models
from django.core.files.storage import FileSystemStorage

from sonnar.modelfields import ModularField
from sonnar.features.base import Feature
from sonnar.features.images import PILImage, WidthFeature, HeightFeature, OpenCVHandle

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


class TestImageModel(models.Model):
    id = models.AutoField(primary_key=True)
    modfile = ModularField(name='modfile',
        upload_to="modfiles",
        storage=FileSystemStorage(),
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

