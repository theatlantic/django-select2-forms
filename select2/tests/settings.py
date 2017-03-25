import django
import dj_database_url

from django_admin_testutils.settings import *


DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL', 'sqlite://:memory:'))

INSTALLED_APPS += (
    'select2',
    'select2.tests',
)

ROOT_URLCONF = 'select2.tests.urls'

TEMPLATES[0]['OPTIONS']['debug'] = True
DEBUG_PROPAGATE_EXCEPTIONS = True
