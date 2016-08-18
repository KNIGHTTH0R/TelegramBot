# coding: utf-8

import telepot

from telegram_bot import settings
from telegram_bot.celery import app

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


@app.task(bind=True, name='update_chat')
def update_chat(self):
    TelegramBot.sendMessage(72772783, 'Shut up')
    print 'Hello'
