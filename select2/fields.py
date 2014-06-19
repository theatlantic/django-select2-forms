from django import forms
from django.db import models
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models.fields import FieldDoesNotExist
from django.forms.models import ModelChoiceIterator
from django.utils.encoding import force_unicode
from django.db.models.fields.related import add_lazy_relation

from .models.descriptors import SortableReverseManyRelatedObjectsDescriptor
from .widgets import Select, SelectMultiple


__all__ = (
    'Select2FieldMixin', 'Select2ModelFieldMixin', 'ChoiceField',
    'MultipleChoiceField', 'ModelChoiceField', 'ModelMultipleChoiceField',
    'ForeignKey', 'ManyToManyField',)


class Select2FieldMixin(object):

    def __init__(self, *args, **kwargs):
        widget_kwargs = {}
        widget_kwarg_keys = ['overlay', 'js_options', 'sortable', 'ajax']
        for k in widget_kwarg_keys:
            if k in kwargs:
                widget_kwargs[k] = kwargs.pop(k)
        widget = kwargs.pop('widget', None)
        if isinstance(widget, type):
            if not issubclass(widget, Select):
                widget = self.widget
        elif not isinstance(widget, Select):
            widget = self.widget
        if isinstance(widget, type):
            kwargs['widget'] = widget(**widget_kwargs)
        else:
            kwargs['widget'] = widget
        super(Select2FieldMixin, self).__init__(*args, **kwargs)
        # Django 1.2 backwards-compatibility
        if not hasattr(self.widget, 'is_required'):
            self.widget.is_required = self.required


class ChoiceField(Select2FieldMixin, forms.ChoiceField):

    widget = Select


class MultipleChoiceField(Select2FieldMixin, forms.MultipleChoiceField):

    widget = SelectMultiple


class Select2ModelFieldMixin(Select2FieldMixin):

    search_field = None
    case_sensitive = False

    choice_iterator_cls = ModelChoiceIterator

    def __init__(self, search_field=None, case_sensitive=False, *args, **kwargs):
        if search_field is None and kwargs.get('ajax'):
            raise TypeError(
                ("keyword argument 'search_field' is required for field "
                 "%s <%s>") % (self.name, self.__class__.__name__))
        self.search_field = search_field
        self.case_sensitive = case_sensitive
        self.name = kwargs.pop('name')
        self.model = kwargs.pop('model')
        self.choice_iterator_cls = kwargs.pop('choice_iterator_cls', self.choice_iterator_cls)
        super(Select2ModelFieldMixin, self).__init__(*args, **kwargs)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return self.choice_iterator_cls(self)
    
    choices = property(_get_choices, forms.ChoiceField._set_choices)


class ModelChoiceField(Select2ModelFieldMixin, forms.ModelChoiceField):

    widget = Select

    def __init__(self, *args, **kwargs):
        super(ModelChoiceField, self).__init__(*args, **kwargs)
        self.widget.field = self


class ModelMultipleChoiceField(Select2ModelFieldMixin, forms.ModelMultipleChoiceField):

    widget = SelectMultiple

    #: Instance of the field on the through table used for storing sort position
    sort_field = None

    def __init__(self, *args, **kwargs):
        self.sort_field = kwargs.pop('sort_field', self.sort_field)
        if self.sort_field is not None:
            kwargs['sortable'] = True
        super(ModelMultipleChoiceField, self).__init__(*args, **kwargs)
        self.widget.field = self

    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []

        if isinstance(value, basestring):
            value = value.split(',')

        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])

        key = self.to_field_name or 'pk'

        for pk in value:
            try:
                self.queryset.filter(**{key: pk})
            except ValueError:
                raise ValidationError(self.error_messages['invalid_pk_value'] % pk)
        qs = self.queryset.filter(**{
            ('%s__in' % key): value,
        })
        pks = set([force_unicode(getattr(o, key)) for o in qs])

        # Create a dictionary for storing the original order of the items
        # passed from the form
        pk_positions = {}

        for i, val in enumerate(value):
            pk = force_unicode(val)
            if pk not in pks:
                raise ValidationError(self.error_messages['invalid_choice'] % val)
            pk_positions[pk] = i

        if not self.sort_field:
            return qs
        else:
            # Iterate through the objects and set the sort field to its
            # position in the comma-separated request data. Then return
            # a list of objects sorted on the sort field.
            sort_field_name = self.sort_field.name
            objs = []
            for i, obj in enumerate(qs):
                pk = force_unicode(getattr(obj, key))
                setattr(obj, sort_field_name, pk_positions[pk])
                objs.append(obj)
            sorted(objs, key=lambda obj: getattr(obj, sort_field_name))
            return objs

    def prepare_value(self, value):
        return super(ModelMultipleChoiceField, self).prepare_value(value)


class RelatedFieldMixin(object):

    search_field = None
    js_options = None
    overlay = None
    case_sensitive = False
    ajax = False

    def __init__(self, *args, **kwargs):
        self.search_field = kwargs.pop('search_field', None)
        self.js_options = kwargs.pop('js_options', None)
        self.overlay = kwargs.pop('overlay', self.overlay)
        self.case_sensitive = kwargs.pop('case_sensitive', self.case_sensitive)
        self.ajax = kwargs.pop('ajax', self.ajax)
        super(RelatedFieldMixin, self).__init__(*args, **kwargs)

    def _get_queryset(self, db=None):
        return self.rel.to._default_manager.using(db).complex_filter(self.rel.limit_choices_to)

    @property
    def queryset(self):
        return self._get_queryset()

    def formfield(self, **kwargs):
        db = kwargs.pop('using', None)
        defaults = {
            'form_class': ModelChoiceField,
            'queryset': self._get_queryset(db),
            'js_options': self.js_options,
            'search_field': self.search_field,
            'ajax': self.ajax,
            'name': self.name,
            'model': self.model,
        }
        defaults.update(kwargs)
        if self.overlay is not None:
            defaults.update({'overlay': self.overlay})

        # If initial is passed in, it's a list of related objects, but the
        # MultipleChoiceField takes a list of IDs.
        if defaults.get('initial') is not None:
            initial = defaults['initial']
            if callable(initial):
                initial = initial()
            defaults['initial'] = [i._get_pk_val() for i in initial]
        return models.Field.formfield(self, **defaults)

    def contribute_to_related_class(self, cls, related):
        if not self.ajax:
            return super(RelatedFieldMixin, self).contribute_to_related_class(cls, related)
        if self.search_field is None:
            raise TypeError(
                ("keyword argument 'search_field' is required for field "
                 "'%(field_name)s' of model %(app_label)s.%(object_name)s") % {
                    'field_name': self.name,
                    'app_label': self.model._meta.app_label,
                    'object_name': self.model._meta.object_name})
        if not callable(self.search_field) and not isinstance(self.search_field, basestring):
            raise TypeError(
                ("keyword argument 'search_field' must be either callable or "
                 "string on field '%(field_name)s' of model "
                 "%(app_label)s.%(object_name)s") % {
                    'field_name': self.name,
                    'app_label': self.model._meta.app_label,
                    'object_name': self.model._meta.object_name})
        if isinstance(self.search_field, basestring):
            opts = related.parent_model._meta
            try:
                opts.get_field(self.search_field)
            except FieldDoesNotExist:
                raise ImproperlyConfigured(
                    ("keyword argument 'search_field' references non-existent "
                     "field '%(search_field)s' in %(field_name)s of model "
                     "<%(app_label)s.%(object_name)s>") % {
                        'search_field': self.search_field,
                        'field_name': self.name,
                        'app_label': opts.app_label,
                        'object_name': opts.object_name})
        super(RelatedFieldMixin, self).contribute_to_related_class(cls, related)


class ForeignKey(RelatedFieldMixin, models.ForeignKey):

    def formfield(self, **kwargs):
        defaults = {
            'to_field_name': self.rel.field_name,
        }
        defaults.update(**kwargs)
        return super(ForeignKey, self).formfield(**defaults)


class ManyToManyField(RelatedFieldMixin, models.ManyToManyField):

    #: Name of the field on the through table used for storing sort position
    sort_field_name = None

    #: Instance of the field on the through table used for storing sort position
    sort_field = None

    def __init__(self, *args, **kwargs):
        self.sort_field_name = kwargs.pop('sort_field', self.sort_field_name)
        help_text = kwargs.get('help_text', u'')
        super(ManyToManyField, self).__init__(*args, **kwargs)
        self.help_text = help_text

    def formfield(self, **kwargs):
        defaults = {
            'form_class': ModelMultipleChoiceField,
            'sort_field': self.sort_field,
        }
        defaults.update(**kwargs)
        return super(ManyToManyField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name):
        """
        Replace the descriptor with our custom descriptor, so that the
        position field (which is saved in the formfield clean()) gets saved
        """
        if self.sort_field_name is not None:
            def resolve_sort_field(field, model, cls):
                field.sort_field = model._meta.get_field(field.sort_field_name)
            if isinstance(self.rel.through, basestring):
                add_lazy_relation(cls, self, self.rel.through, resolve_sort_field)
            else:
                resolve_sort_field(self, self.rel.through, cls)
        super(ManyToManyField, self).contribute_to_class(cls, name)
        if self.sort_field_name is not None:
            setattr(cls, self.name, SortableReverseManyRelatedObjectsDescriptor(self))


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(rules=[
        ((ManyToManyField,), [], {"search_field": ["search_field", {}]}),
    ], patterns=["^select2\.fields\.ManyToManyField"])
    add_introspection_rules(rules=[
        ((ForeignKey,), [], {"search_field": ["search_field", {}]}),
    ], patterns=["^select2\.fields\.ForeignKey"])
