from .base import *
import socket

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

# We need to also respond to the private IP address of the instance as that's
# what the ELB will send healthcheck requests to
local_ip_addresses = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())[1] for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]]
ALLOWED_HOSTS = local_ip_addresses + [
    {% for domain in domains %}
    "{{ domain}}",
    {% endfor %}
]
