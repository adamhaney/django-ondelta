#!/usr/bin/env python

import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="ondelta",
    version="0.1",
    author="Adam Haney",
    author_email="adam.haney@campusbellhops.com",
    description=("A mixin that allows models to register methods that are notified when their values change, or register a method that is notified of all changes. Basically, OnDeltaMixin implements the observer pattern."),
    license="LGPL",
    keywords="Django, observer",
    url="",
    packages=['ondelta'],
    long_description=read('README.md'),
    dependency_links = [],
    install_requires=[
        'django'
        ],
    classifiers=[]
)
