# coding: utf-8

import os

from collections import namedtuple

import jinja2


Row = namedtuple('Row', ['title', 'link'])
RowDist = namedtuple('RowDist', ['title', 'distance', 'link'])


def uncd(s):
    if isinstance(s, str):
        s = unicode(s, 'utf-8')
    else:
        s = unicode(s)
    return s


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

bot_username = 'KinohodTest_bot'
KINOHOD_API_KEY = 'f056d104-abcd-3ab7-9132-cfcf3a098bc4'
TELEGRAM_BOT_TOKEN = '220697123:AAGHvA89SQ3qVCXyafTB9GObKa7E1f9xRrs'
BOTAN_TOKEN = 'ip2CSBT89XNqLbzAjcaF4vw6Iyc9LJIx'


BASE_URL = 'https://api.telegram.org/bot{}/'.format(TELEGRAM_BOT_TOKEN)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

URL_CINEMAS = 'https://kinohod.ru/api/rest/partner/v1/cinemas/?apikey={}'
URL_RUNNING_MOVIES = 'https://api.kinohod.ru/api/data/2/{}/running.json.gz'
URL_MOVIES_INFO = 'https://kinohod.ru/api/rest/partner/v1/movies/{}?apikey={}'
URL_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?apikey={}&rangeStart={}&limit={}'
URL_FULL_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?apikey={}'
URL_CINEMA_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?apikey={}&limit=10&date={}'
CINEMA_HALL = 'https://kinohod.ru/api/rest/partner/v1/schedules/{}/hallscheme?apikey={}&limit=20'
URL_IMDB = 'http://www.imdb.com/title/tt{}'
URL_BASE_O = 'https://kinohod.ru/o/'
URL_WIDGET_CINEMAS = 'http://kinohod.ru/widget/cinemas'

FILMS_TO_DISPLAY = 10
CINEMAS_TO_DISPLAY = 10
SEANCES_TO_DISPLAY = 10

TODAY = 0
TOMORROW = 1
A_TOMORROW = 2


SIGN_VIDEO = '\xF0\x9F\x8E\xA5'.decode('utf-8')
SIGN_PREMIER = '\xF0\x9F\x8E\xAC'.decode('utf-8')
SIGN_TIP = '\xE2\x9C\x94'.decode('utf-8')
SIGN_ACTOR = unicode('\xF0\x9F\x91\xA4', encoding='utf-8')  # .decode('utf-8')
SIGN_NEW_ROW = '\n'.decode('utf-8')
SIGN_SMILE_HELP = '\xE2\x96\xAA'.decode('utf-8')



SIGN_RUB = 'P'
CHOOSE_SEANCE = 'Выбрать сеанс'.decode('utf-8')
FIND_CINEMA = 'Вы можете ввести часть названия кинотеатра, а мы попытаемся найти его для Вас'
FIRST_TEN = 'Первые 10'
NO_FILMS = 'К сожалению, больше нет фильмов в прокате.'
MORE = 'Ещё'
TREILER = 'Трейлер'
DONT_UNDERSTAND = 'Я Вас не понимаю'
CINEMA_NOT_VALID = 'Кинотеатр не доступен сейчас'
ON_TOMORROW = 'На завтра'
ON_A_TOMORROW = 'На послезавтра'
ON_TODAY = 'На сегодня'
SERVER_NOT_VALID = 'Увы, сервер недоступен.'
BUY_TICKET = 'Купить билеты'
SHARE_LOCATION = 'Мое местоположение'
THANK_FOR_INFORMATION = 'Спасибо за информацию.'
THANK_FOR_INFORMATION_AGAIN = 'Спасибо за информацию, Ваши данные обновлены'
FAIL_CODE_WORD = 'Не знаю кодового слова'
PROBLEM_BUY_TICKET = 'Проблемы с покупкой билета'

TICKET_RETURNING = 'Возврат билета'
TICKET_RETURNING_REPLY = 'У каждого кинотеатра свои правила возврата билета. Перейдите по ссылке «Вернуть билеты» в письме от Кинохода.'

ANOTHER = 'Другое'
WHAT_A_PROBLEM = 'В чем проблема?'
TERMINAL_NOT_WORKING = 'Терминал в к/т не работает'
SERTIFICATES = 'Сертификаты'
SEE_MAIL_SERTIFICATES = 'Если Вы активировали сертификат, но билеты не пришли на почту, проверьте папку «Спам». Есть письмо от Кинохода?'
YES_SERT_MAIL = 'Письмо все таки пришло'
NO_SERT_MAIL = 'Письма так и нет'
IF_TERMINAL_NOT_WORKING = 'Если терминал не работает, обратитесь в кассу, предъявите письмо от Кинохода. Кассир выдаст Вам билеты.'

HOW_CAN_HELP = 'Чем я могу Вам помочь?'
SECRET_WORD = 'Наше секретное слово - Киноход. Приятного просмотра!'
BACK = 'Назад'
SUPPORT_HELP = 'Чем я могу Вам помочь?'
WHAT_PROBLEM = 'В чем проблема?'
NO_MAIL_TICKET = 'Не пришло письмо с билетом'


NO_PAY = 'Не прошла оплата'
CANNOT_PAY = 'Невозможно оплатить'
ERROR_SERVER_CONN = 'Ошибка соединения с сервером'
PLEASE_WAIT_2_MIN = 'Пожалуйста, повторите попытку через несколько минут.'
ONLINE_ISNT_VALID = 'Продажа билетов онлайн невозможна'
TIME_PAY_EXC = 'Время для оплаты истекло'
YOU_MAY_PAY = 'У вас есть 15 минут, чтобы ввести свои платежные данные. Если это время прошло, попробуйте оплатить еще раз.'
ANOTHER_PAY_ER = 'Другая ошибка'
YES_VALID_CASH = 'Средств достаточно'
NO_CASH_INVALID = 'Нет, придется пополнить'
SEE_CASH = 'Проверьте, достаточно ли у Вас средств для оплаты билетов на карте/на мобильном счете/на Qiwi-кошельке.'
TRY_AGAIN = 'Пожалуйста, попробуйте еще раз через несколько минут. Получилось?'
YES_AGAIN = 'Теперь все отлично'
NO_AGAIN = 'Ничего не изменилось'


QR_CODE_PROBLEM = 'QR-код не распознан'
QR_SPECIAL = 'Введите в терминале код заказа, этот код Вы найдете в письме от Кинохода, которое получили после покупки билетов.'
YES_QR = 'Получилось.'
NO_QR = 'Не вышло.'
QR_SPECIAL_VALID = 'Возможно, терминал не работает. Такое случается. Пожалуйста, обратитесь в кассу кинотеатра и предъявите письмо от Кинохода. Кассир выдаст Вам билеты!'

TIMEOUT_TICKET = 'Уже прошло двадцать 20 минут после оплаты?'
YES_IT_WAS = 'Да, прошло'
NO_IT_ISNT = 'Еще нет'

SEE_MAIL_KINOHOD = 'Проверьте папку «Спам» в своем почтовом ящике. Есть письмо от Кинохода?'
MAIL_IN_SPAM = 'Письмо как раз там'
NO_MAIL = 'Письма нет'

MAILS_A_LOT = 'Возможно, Ваш ящик переполнен, и письмо не может попасть во «Входящие». Освободите место в ящике и проверьте его еще раз. Пришло?'

MAIL_SENDED = 'Теперь пришло'
NO_MAIL_SENDED = 'Письма все еще нет'

NEED_CONTACT = 'Мы взяли Ваш запрос в обработку и свяжемся с Вами в самое ближайшее время'
NEED_CONTACT_MAIL = 'Пожалуйста введите Ваш email, чтобы наш специалист мог связаться с Вами.'
PAY_ERROR = 'Какая ошибка появилась на сайте/в приложении?'
INFO_FULL = 'Допишите id фильма в команду /info и получите подробную информацию о фильме '
SUPPORT_INFO = 'Обращение в службу поддержки'
CINEMA_IS_NOT_SHOWN = 'Фильм не идет в рассматриваемом кинотеатре'

support_a = {
    NO_AGAIN: '{} > {} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_PAY,
        CANNOT_PAY, YES_VALID_CASH, NO_AGAIN),

    NO_MAIL_SENDED: '{} > {} > {} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_MAIL_TICKET,
        YES_IT_WAS, NO_MAIL, NO_MAIL_SENDED),

    ANOTHER_PAY_ER: '{} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_PAY, ANOTHER_PAY_ER)
}
