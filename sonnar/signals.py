
from django.dispatch import Signal

class SyncSignal(Signal):
    def send_now(self, sender, **named):
        return super(SyncSignal, self).send(sender=sender, **named)

try:
    from signalqueue.dispatcher import AsyncSignal as BaseSignal
    from signalqueue.mappings import ModelInstanceMap, PickleMap, IDMap
except ImportError:
    BaseSignal = SyncSignal
    ModelInstanceMap = IDMap = None


preload_features = BaseSignal(providing_args={
    'instance':             ModelInstanceMap,
    'field_name':           IDMap,
})

clear_features = BaseSignal(providing_args={
    'instance':             ModelInstanceMap,
    'field_name':           IDMap,
})


prepare_feature = BaseSignal(providing_args={
    'instance':             ModelInstanceMap,
    'field_name':           IDMap,
    'feature_name':         IDMap,
})

delete_feature = BaseSignal(providing_args={
    'instance':             ModelInstanceMap,
    'field_file':           PickleMap,
    'field_name':           IDMap,
    'feature_name':         IDMap,
})

