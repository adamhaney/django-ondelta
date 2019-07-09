#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup


DESCRIPTION = (
    "A mixin that allows models to register methods that are notified when their values change,"
    "or register a method that is notified of all changes. Basically, OnDeltaMixin implements"
    "the observer pattern."
)


def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...

    Wrapping this in a try block because it appears that IOErrors are being throw due to README.md not making its way to pypi
    """
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return DESCRIPTION

setup(
    name="ondelta",
    version="0.7.0",
    author="Adam Haney",
    author_email="adam@eatonthehouse.com",
    description=DESCRIPTION,
    license="MIT",
    keywords="Django, observer",
    url="https://github.com/adamhaney/django-ondelta",
    packages=['ondelta'],
    long_description=read('README.md'),
    dependency_links=[],
    install_requires=[
        'django>=2.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
