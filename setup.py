#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    readme = open('README.rst', 'rt').read()
except IOError:
    raise AttributeError('Use the create_readme_rst command to convert README to reStructuredText')

setup(
    name='django-select2-forms',
    version='1.1.25',
    description='Django form fields using the Select2 jQuery plugin',
    author='Frankie Dintino',
    author_email='fdintino@theatlantic.com',
    url='https://github.com/theatlantic/django-select2-forms',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    use_2to3=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    entry_points={
        'distutils.commands': [
            'create_readme_rst = select2.build:create_readme_rst',
        ],
    },
)
