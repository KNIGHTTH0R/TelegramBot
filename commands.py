# coding: utf-8

import urllib

import botan

from telepot.namedtuple import InlineKeyboardMarkup

from draw import draw_cinemahall

from screen.cinemas import get_nearest_cinemas
from screen.seances import get_seances
from screen.help import get_help
from screen.movie_info import display_movie_info
from screen.cinema_seances import display_cinema_seances
from screen.running_movies import get_cinema_movies, display_running_movies

import settings


def send_reply(bot, chat_id, func, *args, **kwargs):
    r = func(*args)

    if 'msg' in kwargs and kwargs['msg']:
        bot.sendMessage(chat_id, kwargs['msg'])

    markup = None
    if isinstance(r, tuple):
        r, markup = r

    if r is None:
        return False

    bot.sendMessage(chat_id, r, parse_mode='Markdown', reply_markup=markup)

    if 'success' in kwargs:
        bot.answerCallbackQuery(callback_query_id=kwargs['success'], text=':)')

    return True


def display_help(bot, payload, cmd, chat_id):
    bot.sendMessage(chat_id, get_help(), parse_mode='Markdown')


def display_nearest(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')
    if 'callback_query' in payload:
        number_to_display = int(cmd[len('/nearest'):])
        send_reply(bot, chat_id, get_nearest_cinemas,
                   bot, chat_id, number_to_display,
                   success=int(payload['callback_query']['id']))
    else:
        bot.sendMessage(chat_id, settings.ALLOW_LOCATION)


def display_seance(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')

    if 'callback_query' in payload:
        i_n = cmd.index('num')
        movie_id = cmd[len('/seance'): i_n]
        n_seances = int(cmd[i_n + len('num'): len(cmd)])
        send_reply(bot, chat_id, get_seances, chat_id,
                   movie_id, n_seances,
                   msg=(settings.FIND_CINEMA
                        if n_seances == settings.SEANCES_TO_DISPLAY
                        else None),
                   success=int(payload['callback_query']['id']))


def display_cinema(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')

    if 'callback_query' in payload:
        index_of_v = cmd.index('v')
        cinema_id = int(cmd[len('/show'): index_of_v])
        number_to_display = int(cmd[index_of_v + 1:])
        send_reply(bot, chat_id, get_cinema_movies,
                   cinema_id, number_to_display,
                   success=int(payload['callback_query']['id']))
    else:
        cinema_id = int(cmd[len('/show'):])
        send_reply(bot, chat_id, get_cinema_movies, cinema_id,
                   settings.FILMS_TO_DISPLAY)


def display_movies(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')
    if 'callback_query' in payload:
        number_to_display = int(cmd[7:len(cmd)])
        send_reply(bot, chat_id, display_running_movies,
                   number_to_display,
                   success=int(payload['callback_query']['id']))
    else:
        send_reply(bot, chat_id,
                   display_running_movies, settings.FILMS_TO_DISPLAY)


def display_seances_cinema(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')
    index_of_m = cmd.index('m')
    cinema_id = cmd[2:index_of_m]

    if 'callback_query' in payload:
        index_of_d = cmd.index('d')
        movie_id, d = cmd[index_of_m + 1:index_of_d], cmd[-1]
        send_reply(bot, chat_id, display_cinema_seances,
                   cinema_id, movie_id, d,
                   success=int(payload['callback_query']['id']))
    else:
        movie_id = cmd[index_of_m + 1:len(cmd)]
        d = settings.TODAY
        send_reply(bot, chat_id, display_cinema_seances,
                   cinema_id, movie_id, d)


def display_schedule(bot, payload, cmd, chat_id):
    def _send_company_offers(bot, chat_id):
        template = settings.JINJA_ENVIRONMENT.get_template('offers.md')
        msg = template.render({'finger': settings.SIGN_FINGER})
        bot.sendMessage(chat_id, msg)

    bot.sendChatAction(chat_id, action='typing')
    schedule_id = cmd[9: len(cmd)]
    telegram_user_id = payload['message']['from']['id']

    try:
        hall_image = draw_cinemahall(schedule_id)
        city_name_dict = {'cityName': u'Москва'.encode('utf-8')}
        url_encoded_dict = urllib.urlencode(city_name_dict)
        shorten_url = botan.shorten_url(
            'https://kinohod.ru/widget/?{}#scheme_{}'.format(
                url_encoded_dict, schedule_id
            ), settings.BOTAN_TOKEN, telegram_user_id
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text=settings.BUY_TICKET, url=shorten_url)]
        ])

        _send_company_offers(bot, chat_id)
        bot.sendChatAction(chat_id, 'upload_photo')
        bot.sendPhoto(chat_id, ('hall.bmp', hall_image), reply_markup=markup)
    except:
        bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)


def display_info_full(bot, payload, cmd, chat_id):
    bot.sendMessage(chat_id, settings.INFO_FULL)


def display_info(bot, payload, cmd, chat_id):
    t_uid = payload['message']['from']['id']
    movie_id = cmd[5:len(cmd)]

    if not str(movie_id).isdigit():
        bot.sendMessage(chat_id, settings.INFO_NOT_FULL.format(movie_id))

        return
    message, mark_up, movie_poster = display_movie_info(movie_id, t_uid)

    if not message or not mark_up or not movie_poster:
        bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
        return

    bot.sendChatAction(chat_id, 'upload_photo')
    bot.sendPhoto(chat_id, ('poster.jpg', movie_poster))
    bot.sendMessage(chat_id, message, reply_markup=mark_up,
                    parse_mode='Markdown')


def display_return(bot, payload, cmd, chat_id):
    bot.sendMessage(chat_id, settings.ENTER_ORDER_NUMBER)
