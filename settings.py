# coding: utf-8
# flake8: noqa

import os

from collections import namedtuple
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

import jinja2
import pymorphy2


Row = namedtuple('Row', ['title', 'link'])
RowDist = namedtuple('RowDist', ['title', 'distance', 'link'])
RowCinema = namedtuple('RowCinema', ['short_name', 'address', 'mall', 'link'])

MORPH = pymorphy2.MorphAnalyzer()


def uncd(s):
    if isinstance(s, str):
        s = unicode(s, 'utf-8')
    else:
        s = unicode(s)
    return s


def de_uncd(t):
    if isinstance(t, unicode):
        return t.encode('utf-8')
    return t


def start_markup():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=FILMS),
         KeyboardButton(text=CINEMA)],
        [KeyboardButton(text=SUPPORT_INFO)]
    ])


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

TIMEZONE = 2
bot_username = 'KinohodBot'
KINOHOD_API_KEY = 'f056d104-abcd-3ab7-9132-cfcf3a098bc4'
TELEGRAM_BOT_TOKEN = '209622038:AAGuPWWiLqXXAZlEcfh6tC85DKtHslVUJdA'  # production
# TELEGRAM_BOT_TOKEN = '220697123:AAGHvA89SQ3qVCXyafTB9GObKa7E1f9xRrs'
BOTAN_TOKEN = 'DXKQu6IQbjGwX7HSdLP1OCNHMkOoX0ak'  # production
# BOTAN_TOKEN = 'ip2CSBT89XNqLbzAjcaF4vw6Iyc9LJIx'


BASE_URL = 'https://api.telegram.org/bot{}/'.format(TELEGRAM_BOT_TOKEN)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

URL_GENRES = 'https://kinohod.ru/api/rest/partner/v1/movies/?genre={}&apikey={}'
URL_GENRES_SOON = 'https://kinohod.ru/api/rest/partner/v1/movies/?genre={}&apikey={}&filter=soon'
URL_CINEMAS = 'https://kinohod.ru/api/rest/partner/v1/cinemas/?apikey={}'
URL_SOON_MOVIES = 'https://kinohod.ru/api/rest/partner/v1/movies/?filter=soon&apikey={}'
URL_RUNNING_MOVIES = 'https://api.kinohod.ru/api/data/2/{}/running.json.gz'
URL_MOVIES_INFO = 'https://kinohod.ru/api/rest/partner/v1/movies/{}?apikey={}'
URL_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?apikey={}&rangeStart={}&limit={}'
URL_FULL_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?apikey={}'
URL_CINEMA_SEANCES = 'https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?apikey={}&limit=10&date={}'
URL_CINEMA_MOVIE = 'https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?apikey={}'
URL_CINEMA_MOVIE_DATE = 'https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?date={}&apikey={}'
CINEMA_HALL = 'https://kinohod.ru/api/rest/partner/v1/schedules/{}/hallscheme?apikey={}&limit=20'
URL_IMDB = 'http://www.imdb.com/title/tt{}'
URL_CANCEL_TOKEN = 'https://kinohod.ru/ch/'
URL_CANCEL_TICKET = 'https://kinohod.ru/cancel/{}'
URL_BASE_O = 'https://kinohod.ru/o/'
URL_BASE_P = 'https://kinohod.ru/p/200x300/'
URL_WIDGET_CINEMAS = 'http://kinohod.ru/widget/cinemas'
BASE_KINOHOD = 'https://kinohod.ru'

FILMS_TO_DISPLAY = 10
CINEMAS_TO_DISPLAY = 10
FILMS_DISPLAY_INFO = 5
CINEMA_TO_SHOW = 3
SEANCES_TO_DISPLAY = 10

TODAY = 0
TOMORROW = 1
A_TOMORROW = 2

SIGN_CALENDAR = '\xF0\x9F\x93\x85'.decode('utf-8')
SIGN_NEWSPAPER = '\xF0\x9F\x93\xB0'.decode('utf-8')
SIGN_SCREAMING = '\xF0\x9F\x98\xB1'.decode('utf-8')
SIGN_WRITE = '\xF0\x9F\x92\xAC'.decode('utf-8')
SIGN_VIDEO = '\xF0\x9F\x8E\xA5'.decode('utf-8')
SIGN_CLIP = '\xf0\x9f\x93\x8e'.decode('utf-8')
SIGN_PREMIER = '\xF0\x9F\x8E\xAC'.decode('utf-8')
SIGN_TIP = '\xE2\x9C\x94'.decode('utf-8')
SIGN_ACTOR = unicode('\xF0\x9F\x8E\x8E', encoding='utf-8')  # .decode('utf-8')
SIGN_NEW_ROW = '\n'.decode('utf-8')
SIGN_SMILE_HELP = '\xE2\x96\xAA'.decode('utf-8')
SIGN_DOWN_FINGER = '\xF0\x9F\x91\x87'.decode('utf-8')
SIGN_FINGER = '\xF0\x9F\x91\x8D'.decode('utf-8')
SIGN_GENRE = '\xF0\x9F\x8E\xAD'.decode('utf-8')
SIGN_PRODUCER = '\xF0\x9F\x8E\xAC'.decode('utf-8')
SIGN_ALARM = '\xE2\x8F\xB0'.decode('utf-8')
SIGN_CHILD_AGE = '\xF0\x9F\x9A\xB8'.decode('utf-8')


SIGN_RUB = 'P'
FIRST_THREE = 'Первые три'
CHOOSE_SEANCE = 'Выбрать сеанс'.decode('utf-8')
ALLOW_LOCATION = 'Отправьте нам свое местоположение, нажмите {}, после выберите location'.decode('utf-8').format(SIGN_CLIP)
CANNOT_FIND_YOU = 'Не удается найти Вас'
FIND_CINEMA = 'Вы можете ввести часть названия кинотеатра, а мы попытаемся найти его для Вас'
FIRST_TEN = 'Первые 10'
NO_FILMS = 'К сожалению, больше нет фильмов в прокате.'
MORE = 'Ещё'
MORE_INFO = 'Подробнее о предложениях'
TREILER = 'Трейлер'
DONT_UNDERSTAND = 'Извините, я не понял, что именно вас интересует. Спросите еще раз или воспользуйтесь кнопками меню {}'.decode('utf-8').format(SIGN_SCREAMING)
CINEMA_NOT_VALID = 'Кинотеатр не доступен сейчас'
CINEMA_NOT_FOUND = 'Не удалось найти такой кинотеатр, пересмотрите написанное'
ON_TOMORROW = 'Завтра'
ON_A_TOMORROW = 'Послезавтра'
ON_TODAY = 'Сегодня'
NO_FILM_SCHEDULE ='_{}_ фильм *{}* не показывает *{}*, можете выбрать другой день или вообще все другое'.decode('utf-8')
FILM_NO_CINEMA = 'Увы, но фильм сегодня нигде не показывается {}'.decode('utf-8').format(SIGN_SCREAMING)
FILM_NO_PLACE = 'Увы, но фильма в прокате уже нет {}'.decode('utf-8').format(SIGN_SCREAMING)
NO_FILM_SEANCE = 'Увы, но сеансов на выбранный фильм нет {}'.decode('utf-8').format(SIGN_SCREAMING)
NO_SEANCE = 'Нет сеансов на выбранный фильм в этом кинотеатре {}'.decode('utf-8').format(SIGN_SCREAMING)
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
ANOTHER_DAY = 'Другой день'
ENTER_LOCATION = 'Отправьте свое местоположение, для этого нажмите {},а затем location или введите название кинотеатра, торгового центра, станции метро'.decode('utf-8').format(SIGN_CLIP).encode('utf-8')
DAY_CHANGED = 'Что - то не понял дату, выбрал завтра'
ENTER_DATE = 'Введите день, когда хотите пойти посмотреть фильмец'
# ANOTHER_CINEMA = 'Другой кинотеатр'
WHAT_A_PROBLEM = 'В чем проблема?'
TERMINAL_NOT_WORKING = 'Терминал в к/т не работает'
SERTIFICATES = 'Сертификаты'
SEE_MAIL_SERTIFICATES = 'Если Вы активировали сертификат, но билеты не пришли на почту, проверьте папку «Спам». Есть письмо от Кинохода?'
YES_SERT_MAIL = 'Письмо все таки пришло'
NO_SERT_MAIL = 'Письма так и нет'
IF_TERMINAL_NOT_WORKING = 'Если терминал не работает, обратитесь в кассу, предъявите письмо от Кинохода. Кассир выдаст Вам билеты.'

HOW_CAN_HELP = 'Чем я могу Вам помочь?'
CANNOT_HELP = 'Продажа билетов онлайн заканчивается за 30 минут до начала сеанса'
SECRET_WORD = 'Наше секретное слово - Киноход. Приятного просмотра!'
BACK = 'Назад'
SUPPORT_HELP = 'Чем я могу Вам помочь? {}'.decode('utf-8').format(SIGN_DOWN_FINGER)
WHAT_PROBLEM = 'В чем проблема?'
NO_MAIL_TICKET = 'Не пришло письмо с билетом'
FILM_PREVIEW = 'Введите часть названия фильма или его жанр, чтобы я нашел его {}'.decode('utf-8').format(SIGN_FINGER)

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

DO_NOT_KNOW = 'не известно'.decode('utf-8')

QR_CODE_PROBLEM = 'QR-код не распознан'
QR_SPECIAL = 'Введите в терминале код заказа, этот код Вы найдете в письме от Кинохода, которое получили после покупки билетов.'
YES_QR = 'Получилось.'
NO_QR = 'Не вышло.'
QR_SPECIAL_VALID = 'Возможно, терминал не работает. Такое случается. Пожалуйста, обратитесь в кассу кинотеатра и предъявите письмо от Кинохода. Кассир выдаст Вам билеты!'

TIMEOUT_TICKET = 'Уже прошло 20 минут после оплаты?'
YES_IT_WAS = 'Да, прошло'
NO_IT_ISNT = 'Еще нет'

SEE_MAIL_KINOHOD = 'Проверьте папку «Спам» в своем почтовом ящике. Есть письмо от Кинохода?'
MAIL_IN_SPAM = 'Письмо как раз там'
NO_MAIL = 'Письма нет'

MAILS_A_LOT = 'Возможно, Ваш ящик переполнен, и письмо не может попасть во «Входящие». Освободите место в ящике и проверьте его еще раз. Пришло?'

MAIL_SENDED = 'Теперь пришло'
NO_MAIL_SENDED = 'Письма все еще нет'

INFO_NOT_FULL = 'нет фильма с таким номером {}'
NEED_CONTACT = 'Мы взяли Ваш запрос в обработку и свяжемся с Вами в самое ближайшее время'
NEED_CONTACT_MAIL = 'Пожалуйста введите Ваш email, чтобы наш специалист мог связаться с Вами.'
PAY_ERROR = 'Какая ошибка появилась на сайте/в приложении?'
INFO_FULL = 'Допишите id фильма в команду /info и получите подробную информацию о фильме '
CANNOT_FIND_SEANCE = 'Не удалось найти расписание'
SUPPORT_INFO = 'Обращение в службу поддержки'
FILMS = 'Фильмы'
FILM_INFO = 'Вам под силу написать название фильма, можно его часть или же жанр - мы очень постараемся вам угодить {}'.decode('utf-8').format(SIGN_FINGER)
CINEMA = 'Кинотеатры'
CINEMA_NAME = '*Кинотеатр:* {}'
CINEMA_INFO = 'Вам выпадает шанс ввести адресс или станцию метро или хоть что-нибудь, что говорит о месте кинотеатра, в который вы хотите'
AFISHA = 'Афиша'
AFISHA_INFO = 'В таком режиме вы можете писать произвольные высказывания на тему выдачи актуальных фильмов'

NEAREST_SEANCES = 'ближайшие сеансы'
CINEMA_IS_NOT_SHOWN = 'Фильм не идет в рассматриваемом кинотеатре'
ENTER_ORDER_NUMBER = 'Введите номер заказа'
ENTER_ORDER_EMAIL = 'Введите email на который был выслан билет'
INVALID_ORDER = 'Неправильный номер заказа'
INVALID_EMAIL = 'Некорректный email'
CANCEL_SUCCESS = 'Отмена заказа прошла успешно'
CANCEL_ERROR = 'Отмена заказа завершилась ошибкой'

support_a = {
    NO_AGAIN.decode('utf-8').lower(): '{} > {} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_PAY,
        CANNOT_PAY, YES_VALID_CASH, NO_AGAIN),

    NO_MAIL_SENDED.decode('utf-8').lower():
        '{} > {} > {} > {} > {} > {}'.format(
            SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_MAIL_TICKET,
            YES_IT_WAS, NO_MAIL, NO_MAIL_SENDED),

    ANOTHER_PAY_ER.decode('utf-8').lower(): '{} > {} > {} > {}'.format(
        SUPPORT_INFO, PROBLEM_BUY_TICKET, NO_PAY, ANOTHER_PAY_ER)
}
