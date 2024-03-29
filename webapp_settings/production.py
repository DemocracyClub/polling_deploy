from dc_logging_client import DCWidePostcodeLoggingClient

from .base import *
from ec2_tag_conditional.util import InstanceTags
import os
import raven
import socket


def get_env():
    tags = InstanceTags()
    server_env = None
    if tags['Env']:
        server_env = tags['Env']

    if server_env not in ['test', 'prod', 'packer-ami-build']:
        # if we can't work out our environment, don't attempt to guess
        # fail to bootstrap the application and complain loudly about it
        raise Exception('Failed to infer a valid environment')
    return server_env


# settings that are the same across all instance types

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SECRET_KEY = '{{ vault_django_secret }}'

RAVEN_CONFIG = {
    'dsn': '{{ vault_sentry_dsn }}',
}

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
        'CONN_MAX_AGE': 60,
    },
}

# infer environment from the EC2 tags
SERVER_ENVIRONMENT = get_env()

if SERVER_ENVIRONMENT != 'packer-ami-build':
    DATABASE_ROUTERS = ['polling_stations.db_routers.LoggerRouter',]


STATIC_URL = 'https://s3-eu-west-1.amazonaws.com/pollingstations-assets2/{{ image_id.stdout }}/'
PIPELINE['SASS_BINARY'] = "/var/www/polling_stations/env/bin/sassc"

GOOGLE_API_KEYS = [
    '{{ vault_google_maps_api_key1 }}',
    #'{{ vault_google_maps_api_key2 }}',
    #'{{ vault_google_maps_api_key3 }}',
]

MAPBOX_API_KEY = '{{ vault_mapbox_api_key }}'

EMAIL_SIGNUP_API_KEY = '{{ vault_email_signup_api_key }}'
CUSTOM_UA = "DemocracyClub/wheredoivote.co.uk"

# when you change this, remember to turn sync back on
# in roles/every_election/tasks/main.yml and
# deploy to a meatier instance than a t3.micro
EE_BASE = 'http://localhost:8000/'

NEXT_CHARISMATIC_ELECTION_DATE = None

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://wdiv-micro-cache.5ww5u6.0001.euw1.cache.amazonaws.com:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}




# settings that are conditional on env

RAVEN_CONFIG['environment'] = SERVER_ENVIRONMENT


local_ip_addresses = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())[1] for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]]
if SERVER_ENVIRONMENT == 'packer-ami-build':
    ALLOWED_HOSTS = ['*']
if SERVER_ENVIRONMENT == 'test':
    ALLOWED_HOSTS = local_ip_addresses + [
        "stage.wheredoivote.co.uk",
    ]
if SERVER_ENVIRONMENT == 'prod':
    ALLOWED_HOSTS = local_ip_addresses + [
        {% for domain in domains %}
        "{{ domain }}",
        {% endfor %}
    ]


if SERVER_ENVIRONMENT == 'packer-ami-build':
    PRIVATE_DATA_PATH = '{{ private_data_path }}'


if SERVER_ENVIRONMENT in ['prod', 'test']:
    DATABASES['logger'] = {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'polling_stations',
        'PASSWORD': '{{ vault_logger_prod_password }}',
        'HOST': 'logger-prod.c0jvejtwfveq.eu-west-1.rds.amazonaws.com',
        'PORT': '5432',
    }
    if SERVER_ENVIRONMENT == 'prod':
        DATABASES['logger']['NAME'] = 'logger_prod'
    if SERVER_ENVIRONMENT == 'test':
        DATABASES['logger']['NAME'] = 'logger_staging'

if SERVER_ENVIRONMENT == 'prod':
    S3_UPLOADS_BUCKET = "pollingstations-uploads"
if SERVER_ENVIRONMENT == 'test':
    S3_UPLOADS_BUCKET = "pollingstations-uploads-dev"


if SERVER_ENVIRONMENT == 'test':
    BASICAUTH_DISABLE = False
    BASICAUTH_REALM = 'Staging'
    BASICAUTH_USERS = {
        'staging': 'staging'
    }
    BASICAUTH_ALWAYS_ALLOW_URLS = [
        r'^/status_check/$',
        r'^/api/beta/uploads/$'
    ]

if SERVER_ENVIRONMENT != 'packer-ami-build':
    DEFAULT_FROM_EMAIL = "pollingstations@democracyclub.org.uk"
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = 587
    EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = '{{ vault_smtp_user }}'
    EMAIL_HOST_PASSWORD = '{{ vault_smtp_password }}'

    GITHUB_API_KEY = '{{ vault_github_api_key }}'

# Logging client
FIREHOSE_ACCOUNT_ARN = None
if SERVER_ENVIRONMENT == 'prod':
    FIREHOSE_ACCOUNT_ARN = "{{ vault_dc_logging_prod_arn }}"
if SERVER_ENVIRONMENT == 'test':
    FIREHOSE_ACCOUNT_ARN = "{{ vault_dc_logging_stage_arn }}"

if FIREHOSE_ACCOUNT_ARN:
    POSTCODE_LOGGER = DCWidePostcodeLoggingClient(assume_role_arn=FIREHOSE_ACCOUNT_ARN)
