
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
                PILFeature('image'),
                OpenCVFeature('cvdata'),
                WidthFeature('width',
                    source=features.PILFeature),
                HeightFeature('height',
                    source=features.PILFeature),
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
        
        if feature.preload:
            signals.prepare_feature.send_now(
                sender=self.field_file.__class__,
                instance=self.instance,
                field_name=self.field_name,
                field_file=self.field_file,
                feature_name=feature.name)
    
    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError(
                "The '%s' feature can only be accessed from %s instances."
                % (self.feature_name, owner.__name__))
        
        #print "*** instance: %s" % type(instance)
        #print "*** instance.__dict__: %s" % dict(instance.__dict__)
        feature = instance._features[self.feature_name]
        
        #print "*** self.field_file.__dict__: %s" % dict(self.field_file.__dict__)
        #print "*** feature.value: %s" % feature.value
        if feature.value is None:
            print signals.prepare_feature.send_now(
                sender=self.field_file.__class__,
                instance=self.instance,
                field_name=self.field_name,
                field_file=instance,
                feature_name=feature.name)
        
        return feature.get_value()
        
        #print "**~ self.feature.value: %s" % self.feature.value
        #return self.feature.get_value()
        #return getattr(self.field_file, self.feature.name).get_value()
        #return self.field_file.__dict__[self.feature.name].get_value()

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
    
    def prepare_value(self, **kwargs): # signal, sender, instance, field_name, feature_name
        #print "*** Feature.prepare_value() called: %s" % kwargs
        sender = kwargs.get('sender')
        instance = kwargs.get('instance')
        field_file = kwargs.get('field_file')
        field_name = kwargs.get('field_name')
        feature_name = kwargs.get('feature_name')
        
        feature = field_file._features[feature_name]
        
        feature.value = "%s: %s %s -> %s -> %s" % (
            sender.__name__,
            instance.__class__.__name__, instance.pk,
            field_name, feature_name)
        print "+++ %s" % feature.get_value()
        return feature.get_value()
    
    def get_value(self):
        return self.value
    
    def contribute_to_field(self, field_file, instance, field_name, name):
        if not hasattr(field_file.__class__, name):
            setattr(field_file.__class__, name, self.descriptor(self,
                instance=instance, field_name=field_name, field_file=field_file))
            signals.prepare_feature.connect(self.prepare_value, sender=field_file.__class__,
                dispatch_uid="feature-prepare-feature-%s" % field_name)
    
    def contribute_to_class(self, cls, name):
        #signals.prepare_feature.connect(self.prepare_value, sender=self.__class__,
        #    dispatch_uid="feature-prepare-feature-%s" % self.name)
        pass
    
    