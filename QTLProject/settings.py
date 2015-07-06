"""
Django settings for QTLProject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4ml=o-n*2l(0s9)v*zn(%6!icyoluh_+xlw0%9fgz=abyj0%yk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login', 
    'upload',
    'cistrans',
    'investigation',
    'usersession',
    'about',
    'documentation',
    'go',
    'south'
)

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

MIDDLEWARE_CLASSES = (
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'QTLProject.urls'

WSGI_APPLICATION = 'QTLProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'QTL2',
        'USER': 'qtl',
        'PASSWORD': 'qtl',
        'HOST': '',
        'PORT': ''
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR,'media')
#MEDIA_ROOT = '/Users/yaya/www/QTLProject/media'
#MEDIA_ROOT = '/mnt/geninf15/prog/www/django/QTL/QTL/media' # server production

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
#STATIC_ROOT = '/mnt/geninf15/prog/www/django/QTL/qtl/static'
STATIC_URL = '/static/'
#STATICFILES_DIRS = (
#                    '/mnt/geninf15/prog/www/django/QTL/qtl/static',
#                    )



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


# if a user is not logged in, then it will redirect the user to login page

LOGIN_URL= '/login/'
LOGIN_REDIRECT_URL = '/Documentation/'
LOGOUT_URL = '/login/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 

#EMAIL setting
EMAIL_HOST = 'smtp.wur.nl'
EMAIL_HOST_USER = 'jiao.long@wur.nl'
EMAIL_HOST_PASSWORD = 'Gasthuisbouwing50'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'jiao.long@wur.nl'
