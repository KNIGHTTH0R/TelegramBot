# coding: utf-8

import os

import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

from datetime import timedelta

# djcelery.setup_loader()

# CELERY_ALWAYS_EAGER=False
# BROKER_BACKEND = "djkombu.transport.DatabaseTransport"

# djcelery.setup_loader()



# CELERY_IMPORTS = ('telegram_bot',)
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Application definition
# CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
#
# CELERYBEAT_SCHEDULE = {
#     'update-every-30-seconds': {
#         'task': 'update_chat',
#         'schedule': timedelta(seconds=30),
#     },
# }


KINOHOD_API_KEY = 'f056d104-abcd-3ab7-9132-cfcf3a098bc4'
TELEGRAM_BOT_TOKEN = '220697123:AAEFcaCsvNkAHpz9QKooGJjlGKAmPUL1SAc'
BOTAN_TOKEN = 'ip2CSBT89XNqLbzAjcaF4vw6Iyc9LJIx'
BASE_URL = 'https://api.telegram.org/bot{}/'.format(TELEGRAM_BOT_TOKEN)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
# HELP = os.path.join(TEMPLATES_DIR, 'help.md')
# CINEMA_SEANCES = os.path.join(BASE_DIR, 'cinema_seances.md')
# MOVIES_INFO = os.path.join(BASE_DIR, 'movies_info.md')
# NO_SEANCES = os.path.join(BASE_DIR, 'no_seances.md')
# RUNNING_MOVIES = os.path.join(BASE_DIR, 'running_movies.md')
# SEANCES = os.path.join(BASE_DIR, 'seances.md')


URL_RUNNING_MOVIES = 'https://api.kinohod.ru/api/data/2/{}/running.json.gz'
URL_MOVIES_INFO = 'https://kinohod.ru/api/rest/partner/v1/movies/{}?apikey={}'
URL_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?apikey={}&rangeStart={}&limit={}'
URL_CINEMA_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?apikey={}&limit=10&date={}'
URL_IMDB = 'http://www.imdb.com/title/tt{}'

SIGN_VIDEO = '\xF0\x9F\x8E\xA5'.decode('utf-8')
SIGN_PREMIER = '\xF0\x9F\x8E\xAC'.decode('utf-8')
SIGN_TIP = '\xE2\x9C\x94'.decode('utf-8')
SIGN_ACTOR = unicode('\xF0\x9F\x91\xA4', encoding='utf-8')  # .decode('utf-8')
SIGN_NEW_ROW = '\n'.decode('utf-8')
SIGN_SMILE_HELP = '\xE2\x96\xAA'.decode('utf-8')


FILMS_TO_DISPLAY = 10
SEANCES_TO_DISPLAY = 20

TODAY = 0
TOMORROW = 1
DAY_AFTER_TOMORROW = 2

CINEMA_HALL = 'https://kinohod.ru/api/rest/partner/v1/schedules/{}/hallscheme?apikey={}&limit=20'
SIGN_RUB = 'P'
CHOOSE_SEANCE = 'Выбрать сеанс'.decode('utf-8')
