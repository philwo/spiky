# -*- coding: utf-8 -*-

# Spiky / Django settings

DEBUG = True

ADMINS = (
    ("Philipp Wollermann", "philipp.wollermann@gmail.com"),
)

DATABASE_ENGINE = 'mysql'              # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = ''                     # Or path to database file if using sqlite3.
DATABASE_USER = ''                     # Not used with sqlite3.
DATABASE_PASSWORD = ''                 # Not used with sqlite3.
DATABASE_HOST = ''                     # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                     # Set to empty string for default. Not used with sqlite3.

# <SPIKY SETTINGS>
COMPILER_ENABLED = True
TEMPLATE_DIR = "default/"
BASE_SITE = TEMPLATE_DIR + "base.html"
SPIKY_BASEURL = "http://spiky.phorge.de"
SPIKY_CACHEPATH = "/home/philwo/www/spiky.phorge.de/persistent"
# </SPIKY SETTINGS>

# Absolute path to the directory that holds media.
MEDIA_ROOT = '/home/philwo/www/spiky.phorge.de/htdocs/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = 'http://spiky.phorge.de/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '123456789123456789123456789123456789123456789'

SERVER_EMAIL = "vz102@igowo.de"
DEFAULT_FROM_EMAIL = "vz102@igowo.de"

TEMPLATE_DIRS = (
    "/home/philwo/www/spiky.phorge.de/templates",
)

################ NO NEED TO CUSTOMIZE BEYOND THIS LINE ##############

TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS

DATABASE_OPTIONS = {
    "init_command": "SET storage_engine=INNODB",
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
#   'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'spiky.urls'

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/Start/"
AUTH_PROFILE_MODULE = "wiki.userprofile"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
#   'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.sites',
    'django.contrib.markup',
    'spiky.wiki',
)
