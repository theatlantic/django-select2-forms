from __future__ import unicode_literals

from django import template

import select2.select2 as sl2


register = template.Library()


@register.filter
def select2_setting(value):
    """
    A simple way to read select2 settings in a template.
    Please consider this filter private for now, do not use it in your own
    templates.
    """
    return sl2.get_select2_setting(value)


@register.simple_tag
def select2_jquery_url():
    """
    Return the full url to jQuery file to use

    Default: ``//code.jquery.com/jquery.min.js``

    This value is configurable, see Settings section

    # Example

        {% select2_jquery_url %}
    """
    return sl2.jquery_url()


@register.simple_tag
def select2_js_url():
    """
    Return the full url to the Select2 JavaScript library

    Default: ``None``

    # Example

        {% select2_js_url %}
    """
    return sl2.select2_js_url()


@register.simple_tag
def select2_django_js_url():
    """
    Return the full url to the JavaScript file integrating Select2 with Django.

    Default: ``{STATIC_URL}/select2/js/djselect2.js``

    # Example

        {% select2_django_js_url %}
    """
    return sl2.djselect2_js_url()


@register.simple_tag
def select2_css_url():
    """
    Return the full url to the Select2 CSS library

    Default: ``None``

    # Example

        {% select2_css_url %}
    """
    return sl2.select2_css_url()


@register.simple_tag
def select2_theme_url():
    """
    Return the full url to a Select2 theme CSS library

    Default: ``None``

    # Example

        {% select2_css_url %}
    """
    return sl2.theme_url()


@register.simple_tag
def select2_django_css_url():
    """
    Return the full url to the CSS file integrating Select2 with Django.

    Default: ``{STATIC_URL}/select2/css/djselect2.css``

    # Example

        {% select2_django_css_url %}
    """
    return sl2.djselect2_css_url()


@register.simple_tag
def select2_css(select2=None):
    """
    Return HTML for all the CSS files.

    Which CSS files are included can be adjusted in the settings.  If no url is
    returned, we don't want this statement to return any HTML.

    # Arguments

    - `select2` Default: None
                If not None, will force the Select2 CSS to be included.

    # Example

        {% select2_css select2=1 %}
    """

    css_tag = '<link rel="stylesheet" href="{href}" media="all">'
    css = ''

    if select2 is None:
        select2 = sl2.get_select2_setting('include_select2', False)
    if select2:
        url = select2_css_url()
        if url:
            css += css_tag.format(href=url)

    url = sl2.theme_url()
    if url:
        css += css_tag.format(href=url)

    return css


@register.simple_tag
def select2_javascript(jquery=None, select2=None):
    """
    Return HTML for all the CSS files.

    Which CSS files are included can be adjusted in the settings.  If no url is
    returned, we don't want this statement to return any HTML.

    # Arguments

    - `jquery`  Default: None
                If not None, will force the jQuery JS to be included.

    - `select2` Default: None
                If not None, will force the Select2 JS to be included.

    # Example

        {% select2_javascript jquery=1 select2=1 %}
    """

    js_tag = '<script type="text/javascript" src="{url}"></script>'
    javascript = ''

    # See if we have to include jQuery
    if jquery is None:
        jquery = sl2.get_select2_setting('include_jquery', False)
    if jquery:
        url = select2_jquery_url()
        if url:
            javascript += js_tag.format(url=url)

    if select2 is None:
        select2 = sl2.get_select2_setting('include_select2', False)
    if select2:
        url = select2_js_url()
        if url:
            javascript += js_tag.format(url=url)

    url = select2_django_js_url()
    if url:
        javascript += js_tag.format(url=url)

    return javascript
