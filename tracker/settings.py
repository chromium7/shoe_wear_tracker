"""
Django settings for tracker project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_DIR = Path(__file__).resolve().parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$_oa*lwe!5#65i0p5b(2ayk#kjh!*as1(72bq_nv909z76-+c)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'compressor',
    'django_extensions',
    'rest_framework',
    'thumbnails',
    'querystring_tag',

    # Local apps
    'tracker.apps.activities',
    'tracker.apps.users',
    'tracker.apps.photos',
    'tracker.apps.shoes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tracker.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = SETTINGS_DIR / 'static'
STATICFILES_DIRS = (
    BASE_DIR / 'static_files',
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_PARSER = 'compressor.parser.LxmlParser'
COMPRESS_ENABLED = True
COMPRESS_MTIME_DELAY = 20
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)


MEDIA_URL = 'media/'
MEDIA_ROOT = SETTINGS_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Redis
REDIS_PASSWORD = ""
CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Thumbnails
IMAGE_S3_BUCKET_NAME = ''
IMAGE_S3_ACCESS_KEY_ID = ''
IMAGE_S3_SECRET_ACCESS_KEY = ''
THUMBNAILS: dict = {
    'METADATA': {
        'PREFIX': 'thumbs',
        'BACKEND': 'thumbnails.backends.metadata.RedisBackend',
        'db': 2,
        'password': REDIS_PASSWORD,
    },
    'STORAGE': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'BASE_DIR': 'thumb',
    'SIZES': {
        'square': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 320, 'height': 320, 'method': 'fill'},
            ],
        },
    },
}


# REST Framework configs
API_AUTHENTICATION_TOKEN = ''
API_REQUIRES_HTTPS = True

HOST_URL = '127.0.0.1'
LOGIN_URL = '/auth/sign-in/'
LOGIN_REDIRECT_URL = ''
APPEND_SLASH = True

STRAVA_CLIENT_ID = ''
STRAVA_CLIENT_SECRET = ''
STRAVA_VERIFY_TOKEN = ''

FIXTURE_DIRS = (
    BASE_DIR / "tests/fixtures",
)
TEST: bool = False
if 'test' in sys.argv:
    TEST = True

try:
    from .local_settings import *  # noqa
except ImportError:
    pass


if DEBUG:
    # Install debug toolbar
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
