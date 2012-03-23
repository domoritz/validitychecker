"""
This file is still under development
A good description of what has to be done can be found here: http://senko.net/en/django-nginx-gunicorn/
"""



from www.conf.settings import *
import os

PROJECT_ROOT = os.environ['DJANGO_PROJECT_ROOT']

ADMINS = (
    ('admin', 'admin@localhost'),
)
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'postgresql',                 # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'climate-goggles',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'



TEMPLATE_DEBUG = False
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

COMPRESS_OUTPUT_DIR = 'CACHE'

#http://django_compressor.readthedocs.org/en/latest/settings/#backend-settings
#COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter']
#COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.JSMinFilter']

#CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

MIDDLEWARE_CLASSES += ((),
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
)

#==============================================================================
# Celery
#==============================================================================

CELERYD_CONCURRENCY = 50

# Enables error emails.
CELERY_SEND_TASK_ERROR_EMAILS = True

# Email address used as sender (From field).
SERVER_EMAIL = "no-reply@example.com"

# Mailserver configuration
EMAIL_HOST = "mail.example.com"
EMAIL_PORT = 25
# EMAIL_HOST_USER = "servers"
# EMAIL_HOST_PASSWORD = "s3cr3t"

CELERY_SEND_EVENTS=False
