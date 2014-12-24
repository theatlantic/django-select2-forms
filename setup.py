#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    # Base information
    name="django-select2-forms",
    version="1.2",
    packages=find_packages(),

    # Pypi Information
    description="Django form fields using the Select2 jQuery plugin.",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    license="BSD",
    author="Frankie Dintino, Joshua Ellis, and more",
    url="https://github.com/JP-Ellis/django-select2-forms",

    # Setup dependencies
    setup_requires=["setuptools_markdown"],
    long_description_markdown_filename="README.md",

    # Dependencies
    install_requires=["django>=1.5"],

    # We also want to include the static files.
    include_package_data=True,
)
