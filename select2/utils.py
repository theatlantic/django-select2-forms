import re

from django.utils import six


re_spaces = re.compile(r"\s+")


def combine_css_classes(classes, new_classes):
    if not classes:
        if isinstance(new_classes, six.string_types):
            return new_classes
        else:
            try:
                return u" ".join(new_classes)
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
            return u" ".join(classes)

    return u" ".join(classes.union(new_classes))
