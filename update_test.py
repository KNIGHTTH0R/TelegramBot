import telepot

from settings import TELEGRAM_BOT_TOKEN

TelegramBot = telepot.Bot(TELEGRAM_BOT_TOKEN)
updates = TelegramBot.getUpdates()
last_update = updates[-1]
last_update = str(last_update)
res = last_update.replace("u\'", "\"")
res = res.replace("\'", "\"")
print res