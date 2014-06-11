from itertools import chain
import json

import django
from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from .utils import combine_css_classes


__all__ = ('Select', 'SelectMultiple',)


class Select(widgets.Input):

    allow_multiple_selected = False

    class Media:
        js = (
            "%s%s?v=2" % (settings.STATIC_URL, "select2/js/select2.jquery_ready.js"),
            "%s%s?v=1" % (settings.STATIC_URL, "select2/js/select2.js"),
        )
        css = {
            "all": (
                "%s%s?v=1" % (settings.STATIC_URL, "select2/css/select2.css"),
                "%s%s?v=2" % (settings.STATIC_URL, "select2/css/djselect2.css"),
            )}

    js_options_map = {
        'maximum_selection_size': 'maximumSelectionSize',
        'allow_clear': 'allowClear',
        'minimum_input_length': 'minimumInputLength',
        'minimum_results_for_search': 'minimumResultsForSearch',
        'close_on_select': 'closeOnSelect',
        'open_on_enter': 'openOnEnter',
        'token_separators': 'tokenSeparators',
        'ajax_quiet_millis': 'quietMillis',
        'quiet_millis': 'quietMillis',
        'data_type': 'dataType',
    }

    js_options = None
    sortable = False
    default_class = ('django-select2',)
    ajax = False

    def __init__(self, attrs=None, choices=(), js_options=None, *args, **kwargs):
        self.ajax = kwargs.pop('ajax', self.ajax)
        self.js_options = {}
        if js_options is not None:
            for k, v in js_options.iteritems():
                if k in self.js_options_map:
                    k = self.js_options_map[k]
                self.js_options[k] = v

        if attrs is None:
            attrs = {}

        self.attrs = getattr(self, 'attrs', {}) or {}

        self.attrs.update({
            'data-placeholder': kwargs.pop('overlay', None),
            'class': combine_css_classes(attrs.get('class', ''), self.default_class),
            'data-sortable': json.dumps(kwargs.pop('sortable', self.sortable)),
        })

        self.attrs.update(attrs)
        self.choices = iter(choices)

    def reverse(self, lookup_view):
        opts = getattr(self, 'model', self.field.model)._meta
        return reverse(lookup_view, kwargs={
            'app_label': opts.app_label,
            'model_name': opts.object_name.lower(),
            'field_name': self.field.name,
        })

    def render(self, name, value, attrs=None, choices=(), js_options=None):
        options = {}
        attrs = attrs or {}
        js_options = js_options or {}

        for k, v in dict(self.js_options, **js_options).iteritems():
            if k in self.js_options_map:
                k = self.js_options_map[k]
            options[k] = v

        if self.ajax:
            ajax_url = options.pop('ajax_url', None)
            quiet_millis = options.pop('quietMillis', 100)
            is_jsonp = options.pop('jsonp', False)

            ajax_opts = options.get('ajax', {})

            default_ajax_opts = {
                'url': ajax_url or self.reverse('select2_fetch_items'),
                'dataType': 'jsonp' if is_jsonp else 'json',
                'quietMillis': quiet_millis,
            }
            for k, v in ajax_opts.iteritems():
                if k in self.js_options_map:
                    k = self.js_options_map[k]
                default_ajax_opts[k] = v
            options['ajax'] = default_ajax_opts

        if not self.is_required:
            options.update({'allowClear': options.get('allowClear', True)})

        attrs.update({
            'data-select2-options': json.dumps(options),
        })

        if self.ajax:
            attrs.update({
                'data-init-selection-url': self.reverse('select2_init_selection'),
            })
            self.input_type = 'hidden'
            self.is_hidden = True
            return super(Select, self).render(name, value, attrs=attrs)
        else:
            return self.render_select(name, value, attrs=attrs, choices=choices)

    def render_select(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select%s>' % flatatt(final_attrs)]
        if not isinstance(value, (list, tuple)):
            value = [value]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append(u'</select>')
        return mark_safe(u'\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return u'<option value="%s"%s>%s</option>' % (
            escape(option_value), selected_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)


class SelectMultiple(Select):

    allow_multiple_selected = True

    def __init__(self, attrs=None, choices=(), js_options=None, *args, **kwargs):
        options = {}
        default_attrs = {}
        ajax = kwargs.get('ajax', self.ajax)
        if ajax:
            options.update({'multiple': True,})
        else:
            default_attrs.update({
                'multiple': 'multiple',
            })
        attrs = dict(default_attrs, **attrs) if attrs else default_attrs
        if js_options is not None:
            options.update(js_options)

        super(SelectMultiple, self).__init__(attrs=attrs, choices=choices,
                js_options=options, *args, **kwargs)

    def _format_value(self, value):
        if isinstance(value, list):
            value = u','.join([force_unicode(v) for v in value])
        return value

    # Restrict defining the _has_changed method to earlier than Django 1.6.
    if django.VERSION < (1, 6):
        def _has_changed(self, initial, data):
            initial = self._format_value(initial)
            return super(SelectMultiple, self)._has_changed(initial, data)

    def value_from_datadict(self, data, files, name):
        # Since ajax widgets use hidden or text input fields, when using ajax the value needs to be a string.
        if not self.ajax and isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)
