# coding: utf-8

import telepot
import logging

from collections import namedtuple

from settings import (TELEGRAM_BOT_TOKEN, KINOHOD_API_KEY, URL_RUNNING_MOVIES,
                      SIGN_PREMIER, SIGN_TIP, SIGN_VIDEO, SIGN_ACTOR, SIGN_MIN,
                      FILMS_TO_DISPLAY, URL_MOVIES_INFO, URL_SEANCES,
                      URL_CINEMA_SEANCES)

TelegramBot = telepot.Bot(TELEGRAM_BOT_TOKEN)
logger = logging.getLogger('telegram.bot')


import json

print json.dumps(TelegramBot.getUpdates())