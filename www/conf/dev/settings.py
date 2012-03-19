from www.conf.settings import *
import os

PROJECT_ROOT = os.environ['DJANGO_PROJECT_ROOT']

DEBUG = True
TEMPLATE_DEBUG = DEBUG
COMPRESS_ENABLED = False
COMPRESS_OUTPUT_DIR = ''
COMPRESS_OFFLINE = False


#CELERY_ALWAYS_EAGER = True
#CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERYD_CONCURRENCY = 10

ADMINS = (
    ('You', 'your@email'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'db' ,'dev.db'),
#        'USER': '',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
