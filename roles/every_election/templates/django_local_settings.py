from .base import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('DC Developers', 'developers+every_election@democracyclub.org.uk'),
)

MANAGERS = ADMINS

ALLOWED_HOSTS = [
    "*",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '{{ ee_name }}',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


PIPELINE['SASS_BINARY'] = "/var/www/every_election/env/bin/sassc"
PIPELINE['JS_COMPRESSOR'] = 'pipeline.compressors.jsmin.JSMinCompressor'
