
import types
from sonnar import signals

from pprint import pprint

"""
    from sonnar.features import PILFeature, OpenCVFeature, WidthFeature, HeightFeature
    
    class MyModel(models.Model):
        featurefile = FeatureFile(verbose_name="Feature File",
            storage=FileSystemStorage(),
            null=True,
            blank=True,
            max_length=255,
            db_index=True,
            features=(
                PILImage('image'),
                OpenCVHandle('cvdata'),
                WidthFeature('width',
                    source=PILImage),
                HeightFeature('height',
                    source=PILImage),
            ))
    
    ----------------------------------------------------------------
    
    >>> from myapp.models import MyModel
    >>> myinstance = MyModel.objects.all()[0]
    >>> myinstance.featurefile
    'path/to/featurefile.jpg-features/featurefile.jpg
    >>> myinstance.featurefile.image
    <JpegImagePlugin.JpegImageFile image mode=RGB size=600x900 at 0x104832C20>
    >>> myinstance.featurefile.width
    600
    >>> myinstance.featurefile.height
    900
    
    
"""

class FeatureDescriptor(object):
    
    instance = None
    feature_name = None
    field_name = None
    field_file = None
    
    def __init__(self, feature, instance=None, field_name=None, field_file=None):
        object.__init__(self)
        self.feature_name = feature.name
        self.instance = instance
        self.field_name = field_name
        self.field_file = field_file
        
        print "*** FeatureDescriptor initialized for feature %s in %s.%s (%s)" % (
            feature.name, instance.__class__.__name__, field_name, field_file)
    
    def __get__(self, field_file=None, owner=None):
        if field_file is None:
            raise AttributeError(
                "The '%s' feature can only be accessed from %s instances."
                % (self.feature_name, owner.__name__))
        
        feature = field_file._features[self.feature_name]
        
        if feature.value is None:
            print signals.prepare_feature.send_now(
                sender=field_file.__class__,
                instance=self.instance,
                field_name=self.field_name,
                field_file=field_file,
                feature_name=feature.name)
        
        return feature.get_value()

class Feature(object):
    
    name = None
    source = None
    unique = False
    preload = False
    descriptor = FeatureDescriptor
    requires = []
    
    value = None
    
    def __init__(self, name, *args, **kwargs):
        object.__init__(self)
        self.name = name
        self.source = kwargs.pop('source', None)
        self.unique = kwargs.pop('unique', False)
        self.preload = kwargs.pop('preload', False)
        
        requires = kwargs.pop('requires', [])
        if requires is not None:
            if type(requires) in (types.TupleType, types.ListType, type(set())):
                self.requires.extend(list(requires))
            else:
                self.requires.append(requires)
    
    # signal, sender, instance, field_file, field_name, feature_name
    def prepare_value(self, **kwargs):
        instance = kwargs.get('instance')
        field_file = kwargs.get('field_file')
        field_name = kwargs.get('field_name')
        feature_name = kwargs.get('feature_name')
        
        feature = field_file._features[feature_name]
        
        feature.value = "%s %s -> %s -> %s" % (
            instance.__class__.__name__, instance.pk,
            field_name, feature_name)
    
    def get_value(self):
        return self.value
    
    def contribute_to_field(self, field_file, instance, field_name, name):
        if not hasattr(field_file.__class__, name):
            setattr(field_file.__class__, name, self.descriptor(self,
                instance=instance, field_name=field_name, field_file=field_file))
            signals.prepare_feature.connect(self.prepare_value,
                sender=field_file.__class__,
                dispatch_uid="feature-prepare-feature-%s" % field_name)
    
    def contribute_to_class(self, cls, name):
        pass
    
    