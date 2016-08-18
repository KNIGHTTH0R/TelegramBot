# coding: utf8
# noqa: flake8

import os
# import djcelery

# import environ
# root = environ.Path(__file__) - 2
# env = environ.Env(DEBUG=(bool, False))
# environ.Env.read_env()

from datetime import timedelta

# djcelery.setup_loader()

# CELERY_ALWAYS_EAGER=False
# BROKER_BACKEND = "djkombu.transport.DatabaseTransport"

# djcelery.setup_loader()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'my_santa'# env.str('SECRET_KEY', 'my-santa-claus')

DEBUG = True

# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
DJANGO_SETTINGS_MODULE = "login_proj.settings"

# CELERY_IMPORTS = ('telegram_bot',)
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Application definition
BROKER_URL = 'django://'
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERYBEAT_SCHEDULE = {
    'update-every-30-seconds': {
        'task': 'update_chat',
        'schedule': timedelta(seconds=30),
    },
}

INSTALLED_APPS = [
    'telegram_bot',
    # 'djcelery',
    # 'djkombu',
    # 'kombu.transport.django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'telegram_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s]: %(levelname)s: %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler'
        },
        'file_handler': {
            'filename': os.path.join(BASE_DIR, 'logs', 'telegram.log'),
            'class': 'logging.handlers.RotatingFileHandler',
            'encoding': 'utf-8',
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 50,
            'backupCount': 50,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'telegram.bot': {
            'handlers': ['file_handler'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

KINOHOD_API_KEY = 'f056d104-abcd-3ab7-9132-cfcf3a098bc4'
TELEGRAM_BOT_TOKEN = '220697123:AAEFcaCsvNkAHpz9QKooGJjlGKAmPUL1SAc'

URL_RUNNING_MOVIES = 'https://api.kinohod.ru/api/data/2/{}/running.json.gz'
URL_MOVIES_INFO = 'https://kinohod.ru/api/rest/partner/v1/movies/{}?apikey={}'
URL_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?apikey={}&limit=30'
URL_CINEMA_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?apikey={}&limit=10'
URL_IMDB = 'http://www.imdb.com/title/tt{}'

SIGN_VIDEO = '\xF0\x9F\x8E\xA5'
SIGN_PREMIER = '\xF0\x9F\x8E\xAC'
SIGN_TIP = '\xE2\x9C\x94'
SIGN_ACTOR = '\xF0\x9F\x91\xA4'
SIGN_NEW_ROW = '\n'
SIGN_SMILE_HELP = '\xE2\x96\xAA'


FILMS_TO_DISPLAY = 10


CINEMA_HALL = 'https://kinohod.ru/api/rest/partner/v1/schedules/{}/hallscheme?apikey={}&limit=20'
SIGN_RUB = 'P'
SIGN_MIN = 'мин.'
CHOOSE_SEANCE = 'Выбрать сеанс'
