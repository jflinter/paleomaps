from os.path import abspath, dirname, basename, join
from os import environ

env = lambda e, d: environ[e] if environ.has_key(e) else d

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_PATH = abspath(dirname(__file__))
PROJECT_NAME = basename(ROOT_PATH)
PROJECT_PATH = dirname(ROOT_PATH)

ADMINS = (
    ('Jack Flintermann', 'jflinter11@gmail.com'),
)

MANAGERS = ADMINS
#mongodb://heroku_app3076898:l36umbb1ulk8enm5sipltsp3g1@ds031477.mongolab.com:31477/heroku_app3076898
if env('DEPLOYMENT_ENVIRONMENT', 'development') == 'production':
  DATABASES = {
    'default': {
      'ENGINE': 'django_mongodb_engine',
      'NAME': 'heroku_app3076898',
      'HOST': 'ds031477.mongolab.com',
      'USER': 'heroku_app3076898',
      'PASSWORD': 'l36umbb1ulk8enm5sipltsp3g1',
      'PORT': 31477
    }
  }
else:
  DATABASES = {
     'default' : {
        'ENGINE' : 'django_mongodb_engine',
        'NAME' : 'paleo',
        'HOST': 'localhost',
        'USER': '',
        'PASSWORD': '',
        'PORT': 27017,
     }
  }

YELP_CONSUMER_KEY = 'ZEpWbbj-1S-KGUebyAc-9Q'
YELP_CONSUMER_SECRET = 'Ksi3aMmNKjemvoCA3vTbcX0Ji4U'
YELP_TOKEN = 'Qx_DxSp6EB0uew33eN-aZEKGQyOWUUqT'
YELP_TOKEN_SECRET = '_rNsubphTKXqAeRzOJkJpUKiqEM'
GOOGLE_API_KEY = 'AIzaSyAZVLuVEQ8VfkBfHgpME9RGkvwyzJYXfGo'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = join(PROJECT_PATH, 'staticfiles')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
  join(PROJECT_PATH, 'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^^xgwsz4a09s@5eajw2x)5#8a&8(e^strtcj(!ja$sa&bl^@m&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'paleo.urls'

TEMPLATE_DIRS = (
    join(ROOT_PATH, 'templates')
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'paleo_webapp',
    'gunicorn',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


