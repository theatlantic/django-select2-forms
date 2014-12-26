from __future__ import unicode_literals

import re

from django.utils import six


re_spaces = re.compile(r"\s+")


class cached_property(object):
    """
    Decorator that creates converts a method with a single
    self argument into a property cached on the instance.
    (not available in django 1.2)
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, type):
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res


def combine_css_classes(classes, new_classes):
    if not classes:
        if isinstance(new_classes, six.string_types):
            return new_classes
        else:
            try:
                return " ".join(new_classes)
            except TypeError:
                return new_classes

    if isinstance(classes, six.string_types):
        classes = set(re_spaces.split(classes))
    else:
        try:
            classes = set(classes)
        except TypeError:
            return classes

    if isinstance(new_classes, six.string_types):
        new_classes = set(re_spaces.split(new_classes))
    else:
        try:
            new_classes = set(new_classes)
        except TypeError:
            return " ".join(classes)

    return " ".join(classes.union(new_classes))
