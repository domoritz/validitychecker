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

#CACHE_BACKEND

MIDDLEWARE_CLASSES += ((),
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
)


# Enables error emails.
CELERY_SEND_TASK_ERROR_EMAILS = True

# Email address used as sender (From field).
SERVER_EMAIL = "no-reply@example.com"

# Mailserver configuration
EMAIL_HOST = "mail.example.com"
EMAIL_PORT = 25
# EMAIL_HOST_USER = "servers"
# EMAIL_HOST_PASSWORD = "s3cr3t"

