from itertools import chain

from django.core.urlresolvers import reverse
from django.conf import settings
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils import simplejson

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

        self.attrs = {
            'data-placeholder': kwargs.pop('overlay', None),
            'class': combine_css_classes(attrs.get('class', ''), self.default_class),
            'data-sortable': simplejson.dumps(kwargs.pop('sortable', self.sortable)),
        }

        self.attrs.update(attrs)
        self.choices = iter(choices)

    def reverse(self, lookup_view):
        opts = self.field.model._meta
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
            'data-select2-options': simplejson.dumps(options),
            'data-init-selection-url': self.reverse('select2_init_selection'),
        })

        if self.ajax:
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
        options = self.render_options(choices, [value])
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

    def __init__(self, js_options=None, *args, **kwargs):
        options = {
            'multiple': True,
        }
        if js_options is not None:
            options.update(js_options)
        super(SelectMultiple, self).__init__(js_options=options, *args, **kwargs)

    def _format_value(self, value):
        if isinstance(value, list):
            value = u','.join([force_unicode(v) for v in value])
        return value

    def _has_changed(self, initial, data):
        initial = self._format_value(initial)
        return super(SelectMultiple, self)._has_changed(initial, data)
