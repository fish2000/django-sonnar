
from django.db import models
from sonnar.modelfields import ModularField
from sonnar.features.base import Feature

class TestModel(models.Model):
    id = models.AutoField(primary_key=True)
    modfile = ModularField(verbose_name="Modular File",
        name='modfile',
        upload_to="modfiles",
        features=(
            Feature('a_feature'),
            Feature('another_feature'),
        ),
        blank=True,
        null=True)

