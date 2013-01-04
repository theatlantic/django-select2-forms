import re


re_spaces = re.compile(ur"\s+")


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
