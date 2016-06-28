#!/usr/bin/env python3
# crate_anon/crateweb/config/settings.py

"""
Django settings for crateweb project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# import datetime
import importlib.machinery
import logging
import os
from crate_anon.crateweb.config.constants import CRATEWEB_CONFIG_ENV_VAR

# http://stackoverflow.com/questions/2636536/how-to-make-django-work-with-unsupported-mysql-drivers-such-as-gevent-mysql-or-c  # noqa
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pymysql = None

log = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# This is the path of the file FROM WHICH THE MODULE WAS LOADED, NOT THE
# DIRECTORY THIS FILE IS IN. So for command-line execute it's e.g.
# /somewhere/crate/crateweb (the directory in which manage.py runs).
# See https://docs.python.org/2/reference/datamodel.html
# Verify this with:

# log.warning("BASE_DIR: {}".format(BASE_DIR))


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # for nice comma formatting of numbers
    'debug_toolbar',  # for debugging
    'django_extensions',  # for graph_models etc.
    'sslserver',  # for SSL testing
    # 'kombu.transport.django',  # for Celery with Django database as broker

    'crate_anon.crateweb.config.apps.UserProfileAppConfig',  # for user-specific settings  # noqa
    'crate_anon.crateweb.config.apps.ResearchAppConfig',  # the research database query app  # noqa
    'crate_anon.crateweb.config.apps.ConsentAppConfig',  # the consent-to-contact app  # noqa
    'crate_anon.crateweb.config.apps.CoreAppConfig',  # for e.g. the runcpserver command  # noqa
)

MIDDLEWARE_CLASSES = (
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # should be added automatically, but there's a problem (2016-04-14)  # noqa
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Additional:
    'crate_anon.crateweb.extra.middleware.UserBasedExceptionMiddleware',  # provide debugging details to superusers  # noqa
    'crate_anon.crateweb.extra.middleware.LoginRequiredMiddleware',  # prohibit all pages except login pages if not logged in  # noqa
    'crate_anon.crateweb.extra.middleware.DisableClientSideCachingMiddleware',  # no client-side caching  # noqa
    'crate_anon.crateweb.core.middleware.RestrictAdminMiddleware',  # non-developers can't access the devadmin site  # noqa
    # 'crate_anon.crateweb.extra.request_cache.RequestCacheMiddleware',  # per-request cache, UNTESTED  # noqa
)

# Celery things
# BROKER_URL = 'django://'  # for Celery with Django database as broker
BROKER_URL = 'amqp://'  # for Celery with RabbitMQ as broker
CELERY_ACCEPT_CONTENT = ['json']  # avoids potential pickle security problem
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
# Results are OPTIONAL. The CRATE web service doesn't use them.
# But may be helpful for Celery testing.
# See http://docs.celeryproject.org/en/latest/configuration.html#std:setting-CELERY_RESULT_BACKEND  # noqa
CELERY_RESULT_BACKEND = "rpc://"  # uses AMQP
CELERY_RESULT_PERSISTENT = False

LOGIN_URL = '/login/'  # for LoginRequiredMiddleware
LOGIN_VIEW_NAME = 'login'  # for LoginRequiredMiddleware
LOGIN_EXEMPT_URLS = []  # for LoginRequiredMiddleware

ROOT_URLCONF = 'crate_anon.crateweb.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,  # can't use OPTIONS/loaders with this
        'OPTIONS': {
            'context_processors': [
                # 'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'crate_anon.crateweb.research.context_processors.common_context',  # noqa
            ],
            # 'loaders': (
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            #     'apptemplates.Loader',
            # ),
        },
    },
]

WSGI_APPLICATION = 'crate_anon.crateweb.config.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

# USE_L10N = True
USE_L10N = False

# https://docs.djangoproject.com/en/1.8/topics/i18n/timezones/
USE_TZ = True

DATE_FORMAT = "j M Y"  # d for leading zero, j for none
TIME_FORMAT = "H:i"
DATETIME_FORMAT = "d M Y, H:i:s"
# O for timezone e.g. "+0100"

SHORT_DATE_FORMAT = "d/m/Y"
SHORT_TIME_FORMAT = "H:i"
SHORT_DATETIME_FORMAT = "d/m/Y, H:i:s"

# =============================================================================
# Static files (CSS, JavaScript, Images)
# =============================================================================
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/crate_static/'
# This is a bit hard-coded, but at least it prevents conflicts with other
# programs. No way to make Django look up (reverse) static URLs dynamically
# using get_script_prefix()?
# (I know that sounds a bit crazy, but the idea would be to point Apache to
# serve those static files via a Django-site-specific location.)
#
# It seems not. So specifying STATIC_URL like this means that Django will serve
# them correctly from its development server, and Apache should be pointed to
# serve from this URL (and from wherever seems best on the filesystem) during
# production.

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
# ... for collectstatic

# NOTE that deriving from django.contrib.staticfiles.storage.StaticFilesStorage
# and referring to it with STATICFILES_STORAGE only influences the
# "collectstatic" command, not the creation of URLs to static files, so isn't
# relevant here.
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/

# =============================================================================
# Some managed database access goes to the secret mapping database.
# =============================================================================

DATABASE_ROUTERS = ['crate_anon.crateweb.research.models.PidLookupRouter']

# =============================================================================
# Security; https://docs.djangoproject.com/en/1.8/topics/security/
# =============================================================================

CRATE_HTTPS = True  # may be overridden in local settings

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# =============================================================================
# Logging; https://docs.djangoproject.com/en/1.8/topics/logging/
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(name)s:%(levelname)s:%(asctime)s.%(msecs)03d:%(module)s:%(message)s',  # noqa
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(name)s:%(levelname)s:%(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'color': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s.%(msecs)03d:%(name)s:%(levelname)s:%(message)s',  # noqa
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'log_colors': {
                'DEBUG': 'bold_black',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'color',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # root logger; necessary if everything propagates
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },

        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },

        # My Django apps:
        'research': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'consent': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'core': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'extra': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },

        # For CherryPy:
        '__main__': {  # for our CherryPy launch script, if used
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        # Not sure the following are working, despite the docs!
        # http://docs.cherrypy.org/en/latest/basics.html#play-along-with-your-other-loggers  # noqa
        'cherrypy_console': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'cherrypy_access': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
        'cherrypy_error': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
}

# =============================================================================
# PDF generation
# =============================================================================
# https://pypi.python.org/pypi/pdfkit

WKHTMLTOPDF_OPTIONS = {
    # http://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    'page-size': 'A4',
    'dpi': '300',
    'orientation': 'portrait',
    'margin-top': '20mm',
    'margin-right': '20mm',
    'margin-bottom': '20mm',
    'margin-left': '20mm',
    'encoding': 'UTF-8',
    # 'disable-smart-shrinking': None,
    # 'print-media-type': None,
}
PATIENT_FONTSIZE = "11.5pt"  # "12.4pt"
"""
    NB strange wkhtmltopdf bug: word wrap goes awry with font sizes of
      11.6pt to 12.3pt inclusive
    but is fine with
      10, 11, 11.5, 12.4, 12.5, 13, 18...
    Affects addresses and word wrap within tables.
    Using wkhtmltopdf 0.12.2.1 (with patched qt)
    See https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2505
"""
RESEARCHER_FONTSIZE = "10pt"

# =============================================================================
# Import from a site-specific file
# =============================================================================
# First attempt: import file with a fixed name from the PYTHONPATH.
#       from crate_local_settings import *  # noqa
# Better: import a file named in an environment variable.

if ('CRATE_RUN_WITHOUT_LOCAL_SETTINGS' in os.environ and
        os.environ['CRATE_RUN_WITHOUT_LOCAL_SETTINGS'].lower() in
        ['true', '1', 't', 'y', 'yes']):
    log.info("Running without local settings")
    # We will only get here for the collectstatic command in the Debian
    # postinst file, so we just need the minimum specified.
    CLINICAL_LOOKUP_DB = 'dummy_clinical'
    EMAIL_SENDER = 'dummy'
    FORCE_SCRIPT_NAME = ''
    MAX_UPLOAD_SIZE_BYTES = 1000
    PRIVATE_FILE_STORAGE_ROOT = '/tmp'
    RESEARCH_DB_TITLE = "dummy database title"
    SECRET_KEY = 'dummy'
    SECRET_MAP = {
        'TABLENAME': 'dummy',
        'PID_FIELD': 'dummy',
        'RID_FIELD': 'dummy',
        'MASTER_PID_FIELD': 'dummy',
        'MASTER_RID_FIELD': 'dummy',
        'TRID_FIELD': 'dummy',
        'MAX_RID_LENGTH': 255,
    }
else:
    if CRATEWEB_CONFIG_ENV_VAR not in os.environ:
        raise ValueError("""
    You must set the {e} environment variable first.
    Aim it at your settings file, like this:

    export {e}=/etc/crate/my_secret_crate_settings.py
        """.format(e=CRATEWEB_CONFIG_ENV_VAR))
    log.info("Loading local settings")
    _loader = importlib.machinery.SourceFileLoader(
        'local_settings',
        os.environ[CRATEWEB_CONFIG_ENV_VAR])
    _local_module = _loader.load_module()
    # noinspection PyUnresolvedReferences
    from local_settings import *  # noqa

# =============================================================================
# Extra actions from the site-specific file
# =============================================================================

if CRATE_HTTPS:
    # https://docs.djangoproject.com/en/1.8/ref/settings/
    # We could do
    #   SECURE_SSL_REDIRECT = True  # redirect all HTTP to HTTPS
    #   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    #   ... trust the X-Forwarded-Proto header from the front-end browser;
    #       if it's 'https', we trust the connection is secure
    # but it is a bit tricky to get right:
    #   https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-SECURE_PROXY_SSL_HEADER  # noqa
    # Instead, YOU SHOULD RESTRICT THE FRONT END. See instructions.txt.
    SESSION_COOKIE_SECURE = True  # cookies only via HTTPS
    CSRF_COOKIE_SECURE = True  # CSRF cookies only via HTTPS
