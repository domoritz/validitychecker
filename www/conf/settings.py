#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *
import os

PROJECT_ROOT = os.environ['DJANGO_PROJECT_ROOT']

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

#==============================================================================
# Calculation of directories relative to the module location
#==============================================================================
import sys
import www

PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.realpath(www.__file__))
)

PYTHON_BIN = os.path.dirname(sys.executable)
if os.path.exists(os.path.join(PYTHON_BIN, 'activate_this.py')):
    # Assume that the presence of 'activate_this.py' in the python bin/
    # directory means that we're running in a virtual environment. Set the
    # variable root to $VIRTUALENV/var.
    VAR_ROOT = os.path.join(os.path.dirname(PYTHON_BIN), 'var')
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
else:
    # Set the variable root to the local configuration location (which is
    # ignored by the repository).
    VAR_ROOT = os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'conf', 'local')

#==============================================================================
# Project URLS and media settings
#==============================================================================

ROOT_URLCONF = 'www.conf.urls'

LOGIN_URL = '/accounts/login/'
LOGOUT_URL = '/accounts/logout/'
LOGIN_REDIRECT_URL = '/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
#MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'tmp')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# compressor settings
# pyscss https://github.com/Kronuz/pyScss/blob/master/scss/tool.py

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'pyscss -C {infile}'),
)

KEEP_COMMENTS_ON_MINIFYING = True

#==============================================================================
# Templates
#==============================================================================

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

#==============================================================================
# Middleware
#==============================================================================

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

#==============================================================================
# Celery
#==============================================================================

# use redis
BROKER_URL = "redis://localhost:6379/0"
BROKER_USER = ""
BROKER_PASSWORD =""
BROKER_VHOST = "0"
REDIS_CONNECT_RETRY = True

#CELERY_SEND_EVENTS=True use -E option instead
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0

CELERY_TASK_RESULT_EXPIRES =  10
CELERYBEAT_SCHEDULER="djcelery.schedulers.DatabaseScheduler"

## Worker settings
## If you're doing mostly I/O you can have more processes,
## but if mostly spending CPU, try to keep it close to the
## number of CPUs on your machine. If not set, the number of CPUs/cores
## available will be used.
## We have IO (network) so lets have a high number
CELERYD_CONCURRENCY = 20

CELERY_TRACK_STARTED = True

CELERY_IMPORTS = ("celery.task.http", )

CELERY_TASK_SERIALIZER = 'pickle'

CELERY_TASK_RESULT_EXPIRES = 3600  # 1 hour = 3600, 5 hours = 18000.

CELERYD_TASK_TIME_LIMIT = 180 # maximum time you have to wait for a task

#def my_on_failure(self, exc, task_id, args, kwargs, einfo):
#    print("Oh no! Task failed: %r" % (exc, ))

#CELERY_ANNOTATIONS = {"*": {"on_failure": my_on_failure}}

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

import djcelery
djcelery.setup_loader()

#==============================================================================
# Apps
#==============================================================================

INSTALLED_APPS = (
    'django.contrib.auth', #for admin
    'django.contrib.contenttypes', #for admin
    'django.contrib.sessions', #for admin
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'south', # for migrations
    'compressor', # for js and css minification
    'djcelery', # for queues
    'gunicorn',

    # project apps
    'www.apps.validitychecker',
)

#==============================================================================
# Validitychecker App Settings
#==============================================================================

# urls for wweb of knwoledge/isi index
# you may want to use a url behind a proxy/ ssh tunnel in order to use the ip
# authentication

# wok web service
WOK_AUTH_URL = 'http://search.isiknowledge.com:2003/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
WOK_SEARCH_URL = 'http://search.isiknowledge.com:2003/esti/wokmws/ws/WokSearchLite?wsdl'

# website
WOK_QUERY_URL = 'http://apps.webofknowledge.com/WOS_GeneralSearch.do'
WOK_SID_URL = 'http://www.webofknowledge.com/?DestApp=WOS'

