#!/usr/bin/env python

import os
from setuptools import setup, find_packages

DESCRIPTION = ("A mixin that allows models to register methods that are notified when their values change, or register a method that is notified of all changes. Basically, OnDeltaMixin implements the observer pattern.")

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
    version="0.2.0",
    author="Adam Haney",
    author_email="adam.haney@campusbellhops.com",
    description=DESCRIPTION,
    license="LGPL",
    keywords="Django, observer",
    url="",
    packages=['ondelta'],
    long_description=read('README.md'),
    dependency_links = [],
    install_requires=[
        'django'
        ],
    classifiers=[],
)
