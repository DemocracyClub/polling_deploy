from .base import *
import os
import raven
import socket

DEBUG = False
TEMPLATE_DEBUG = DEBUG

RAVEN_CONFIG = {
    'dsn': '{{ vault_sentry_dsn }}',
}

PROD_APPS = (
    'raven.contrib.django.raven_compat',
)

ADMINS = (
    ('DC developers', 'developers@democracyclub.org.uk'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '{{ project_name }}',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

{% if use_logger %}
DATABASES['logger'] = {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'logger_prod',
    'USER': 'polling_stations',
    'PASSWORD': '{{ logger_prod_password }}',
    'HOST': 'logger-prod.c0jvejtwfveq.eu-west-1.rds.amazonaws.com',
    'PORT': '5432',
}

DATABASE_ROUTERS = ['polling_stations.db_routers.LoggerRouter',]
{% endif %}


STATIC_URL = 'https://s3-eu-west-1.amazonaws.com/pollingstations-assets2/{{ image_id.stdout }}/'
PIPELINE['SASS_BINARY'] = "/var/www/polling_stations/env/bin/sassc"
PIPELINE['UGLIFYJS_BINARY'] = '/var/www/polling_stations/code/node_modules/uglify-js/bin/uglifyjs'


# We need to also respond to the private IP address of the instance as that's
# what the ELB will send healthcheck requests to
local_ip_addresses = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())[1] for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]]
ALLOWED_HOSTS = local_ip_addresses + [
    {% for domain in domains %}
    "{{ domain }}",
    {% endfor %}
]

{% if google_maps_api_key %}
GOOGLE_API_KEY = '{{ google_maps_api_key }}'
{% endif %}
{% if vault_mapzen_api_key %}
MAPZEN_API_KEY = '{{ vault_mapzen_api_key }}'
{% endif %}

EMAIL_SIGNUP_API_KEY = '{{ vault_email_signup_api_key }}'
CUSTOM_UA = "DemocracyClub/wheredoivote.co.uk"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://wdiv-micro-cache.5ww5u6.0001.euw1.cache.amazonaws.com:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
