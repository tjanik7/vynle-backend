"""
Django settings for vynle_app project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Loads env var file
load_dotenv()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'  # '!=' expression at end of line converts result from str to bool
if DEBUG:
    print('SERVER IN DEBUG MODE!')

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-v5r7h336p-*sct!hc!7u7)0*3ajopv&89s9lfk&%vm&##v8u(*')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = False  # False is fine here since I'm using nginx as front-facing HTTPS server

# Avoids sending CSRF cookie over HTTP
CSRF_COOKIE_SECURE = not DEBUG

# Avoids sending session cookies over HTTP
SESSION_COOKIE_SECURE = not DEBUG

# TODO: Set this to vynle.com in production
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'corsheaders',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'users.apps.UsersConfig',
    'posts.apps.PostsConfig',
    'knox',
    'spotify.apps.SpotifyConfig',
    'debug_toolbar',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'vynle_app.urls'
AUTH_USER_MODEL = 'users.Account'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'vynle_app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {  # Currently set to use an AWS RDS instance
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': '',
#         'USER': 'postgres',
#         'PASSWORD': '<PASSWORD_GOES_HERE>',
#         'HOST': 'vynle-db-1.crssc8igacsm.us-east-2.rds.amazonaws.com',
#         'PORT': 5432,
#     }
# }

# Here is the default postgresql db (using this while testing for simplicity)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

APPEND_SLASH = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Necessary only for configuring Django Debug Toolbar

# INTERNAL_IPS = [  # Only need this version if not using Docker
#     "127.0.0.1",
# ]

# Use this declaration if using Docker
if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda _: False,  # This toggles whether to show debug toolbar
}

# CORS Headers config
CORS_ALLOW_ALL_ORIGINS = False  # Should never be set to True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = (
    'Authorization',
    'Content-Type',
)
CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS',
)

allowed_origin = os.environ.get('ALLOWED_ORIGIN')

CORS_ALLOWED_ORIGINS = [
    allowed_origin,
]
