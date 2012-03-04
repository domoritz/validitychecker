from www.conf.settings import *
import os

PROJECT_ROOT = os.environ['DJANGO_PROJECT_ROOT']

TEMPLATE_DEBUG = False
COMPRESS_ENABLED = True

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
