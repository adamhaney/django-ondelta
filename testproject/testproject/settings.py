# -*- coding: utf-8 -*-

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}

SECRET_KEY = 'foobarbaz'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = (
    'django_nose',
    'testproject.testapp',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
