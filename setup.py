#!/usr/bin/env python
import codecs
import os
from setuptools import setup, find_packages

readme_rst = os.path.join(os.path.dirname(__file__), 'README.rst')

setup(
    name='django-select2-forms',
    version='3.0.0',
    description='Django form fields using the Select2 jQuery plugin',
    long_description=codecs.open(readme_rst, encoding='utf-8').read(),
    author='Frankie Dintino',
    author_email='fdintino@theatlantic.com',
    url='https://github.com/theatlantic/django-select2-forms',
    packages=find_packages(),
    license='BSD',
    platforms='any',
    install_requires=[
        'django-sortedm2m',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

    ],
    include_package_data=True,
    zip_safe=False
)
