import django
import dj_database_url

from django_admin_testutils.settings import *


DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL', 'sqlite://:memory:'))

INSTALLED_APPS += (
    'select2',
    'select2.tests',
)

ROOT_URLCONF = 'select2.tests.urls'

if 'grappelli' in INSTALLED_APPS:
    # django-grappelli has issues with string_if_invalid,
    # so don't use this setting if testing suit.
    TEMPLATES[0]['OPTIONS'].pop('string_if_invalid')

TEMPLATES[0]['OPTIONS']['debug'] = True
DEBUG_PROPAGATE_EXCEPTIONS = True
