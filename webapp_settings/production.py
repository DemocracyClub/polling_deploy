from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Sym Roe', 'sym+polling@democracyclub.org.uk'),
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
    'logger': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'logger_prod',
        'USER': 'polling_stations',
        'PASSWORD': '{{ logger_prod_password }}',
        'HOST': 'logger-prod.c0jvejtwfveq.eu-west-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}
DATABASE_ROUTERS = ['polling_stations.db_routers.LoggerRouter',]

STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True

ALLOWED_HOSTS = [
    {% for domain in domains %}
    "{{ domain}}",
    {% endfor %}
]
