import re


re_spaces = re.compile(ur"\s+")


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
        if isinstance(new_classes, basestring):
            return new_classes
        else:
            try:
                return u" ".join(new_classes)
            except TypeError:
                return new_classes

    if isinstance(classes, basestring):
        classes = set(re_spaces.split(classes))
    else:
        try:
            classes = set(classes)
        except TypeError:
            return classes

    if isinstance(new_classes, basestring):
        new_classes = set(re_spaces.split(new_classes))
    else:
        try:
            new_classes = set(new_classes)
        except TypeError:
            return u" ".join(classes)

    return u" ".join(classes.union(new_classes))
