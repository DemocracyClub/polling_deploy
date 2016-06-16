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
    }
}

STATIC_PRECOMPILER_DISABLE_AUTO_COMPILE = True

ALLOWED_HOSTS = [
    {% for domain in domains %}
    "{{ domain}}",
    {% endfor %}
]
