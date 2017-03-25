#!/usr/bin/env python
import warnings
import django_admin_testutils


def main():
    warnings.simplefilter("error", Warning)
    # Ignore warning from sortedm2m
    warnings.filterwarnings("ignore", "Usage of field.rel")
    warnings.filterwarnings("ignore", "Usage of ForeignObjectRel.to")
    warnings.filterwarnings("ignore", "on_delete")
    warnings.filterwarnings("ignore", "add_lazy_relation")
    runtests = django_admin_testutils.RunTests(
        "select2.tests.settings", "select2")
    runtests()


if __name__ == '__main__':
    main()
