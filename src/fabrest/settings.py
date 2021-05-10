# -*- coding: utf-8 -*-

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.getcwd()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_(ort_!^)ix!c9^3imb%#o+7v2hmfmr#bx3v11e2zec00cm@n#'

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

	'django_createsuperuserwithpassword',
	'rest_framework',

	'fabrest.polls',
#	'fabrest.polls.apps.PollsConfig',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',

	'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

ROOT_URLCONF = 'fabrest.urls'

TEMPLATES = [{
	'BACKEND' : 'django.template.backends.django.DjangoTemplates',
	'DIRS'    : [],
	'APP_DIRS': True,
	'OPTIONS' : {
		'context_processors': [
			'django.template.context_processors.debug',
			'django.template.context_processors.request',
			'django.contrib.auth.context_processors.auth',
			'django.contrib.messages.context_processors.messages',
		],
	},
}]

WSGI_APPLICATION = 'fabrest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'data', 'fabrest.sqlite3'),
	}
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
	'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
}, {
	'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
	'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
	'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ   = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

# Logging
# https://stackoverflow.com/questions/4375784/log-all-sql-queries
LOGGING = {
	'version': 1,
	'filters': {
		'require_debug_true': {
			'()': 'django.utils.log.RequireDebugTrue',
		}
	},
	'handlers': {
		'console': {
			'level'  : 'DEBUG',
			'filters': ['require_debug_true'],
			'class'  : 'logging.StreamHandler',
		}
	},
	'loggers': {
		'django.db.backends': {
			'level'   : 'WARNING',
			'handlers': ['console'],
		},
		'fabrest': {
			'level'   : 'DEBUG',
			'handlers': ['console'],
		}
	}
}



# Django REST Framework

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
	'PAGE_SIZE': 20,
}
