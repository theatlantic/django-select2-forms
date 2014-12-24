from django.conf import settings


# Default settings
SELECT2_DEFAULTS = {
    'jquery_url': '//code.jquery.com/jquery.min.js',
    'select2_url': '//cdnjs.cloudflare.com/ajax/libs/select2/3.5.2/',
    'select2_css_url': None,
    'select2_js_url': None,
    'theme_url': None,
    'include_jquery': False,
    'include_select2': False
}

SELECT2 = SELECT2_DEFAULTS.copy()

SELECT2.update(getattr(settings, 'SELECT2', {}))


def get_select2_setting(setting, default=None):
    """
    Read a settting.
    """
    return SELECT2.get(setting, default)


def select2_url(postfix):
    """
    Prefix a relative url with the select2 base url.
    """
    return get_select2_setting('select2_url') + postfix


def djselect2_url(postfix):
    """
    Prefix a relative url with the Django Select2 static url.
    """
    return settings.STATIC_URL + 'select2/' + postfix


def jquery_url():
    """
    Return the full url to the jQuery file to use.
    """
    return get_select2_setting('jquery_url')


def select2_js_url():
    """
    Return the full url to the Select2 JavaScript file.
    """
    return get_select2_setting('javascript_url') or \
        select2_url('select2.min.js')


def djselect2_js_url():
    """
    Return the full url to the Django Select2 Javascript file.
    """
    return djselect2_url('js/djselect2.js')


def select2_css_url():
    """
    Return the full url to the Select2 CSS file.
    """
    return get_select2_setting('css_url') or \
        select2_url('select2.min.css')


def theme_url():
    """
    Return the full url to the theme CSS file.
    """
    return get_select2_setting('theme_url')
