import sys

from django.db import models
try:
    from django.apps import apps
except ImportError:
    from django.db.models.loading import get_model
else:
    get_model = apps.get_model
from django.db.models.base import ModelBase
from django.utils.functional import SimpleLazyObject


class SortableThroughModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        # This is the super __new__ of the parent class. If we directly
        # call the parent class we'll register the model, which we don't
        # want to do yet
        super_new = super(SortableThroughModelBase, cls).__new__
        base_super_new = super(ModelBase, cls).__new__

        parents = [b for b in bases if isinstance(b, SortableThroughModelBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        module = attrs.get('__module__')

        # Create a class for the purposes of grabbing attributes that would
        # be set from inheritance
        tmp_new_class = base_super_new(cls, name, bases, {'__module__': module})

        attr_meta = attrs.get('Meta', None)
        if not attr_meta:
            meta = getattr(tmp_new_class, 'Meta', None)
        else:
            meta = attr_meta
        if meta is None:
            class Meta: pass
            meta = Meta
            meta.__module__ = module

        attrs['Meta'] = meta

        return super_new(cls, name, bases, attrs)


class SortableThroughModel(models.Model):

    __metaclass__ = SortableThroughModelBase

    class Meta:
        abstract = True
