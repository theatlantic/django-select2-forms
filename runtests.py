#!/usr/bin/env python
import sys
import warnings
import selenosis

def main():
    warnings.simplefilter("error", Warning)
    # Ignore warning from sortedm2m
    warnings.filterwarnings("ignore", "Usage of field.rel")
    warnings.filterwarnings("ignore", "Usage of ForeignObjectRel.to")
    warnings.filterwarnings("ignore", "on_delete")
    warnings.filterwarnings("ignore", "add_lazy_relation")
    if sys.version_info >= (3, 7):
        warnings.filterwarnings("ignore", "Using or importing the ABCs")
    runtests = selenosis.RunTests("select2.tests.settings", "select2")
    runtests()


if __name__ == '__main__':
    main()
