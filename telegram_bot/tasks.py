import telepot
from djcelery import app

from telegram_bot import settings

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


@app.task(name='update_chat')
def update_chat(self):
    TelegramBot.sendMessage(72772783, 'Shut up')
    print 'Hello'