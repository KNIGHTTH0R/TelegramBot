# coding: utf-8

import urllib
import requests

import botan

from telepot.namedtuple import InlineKeyboardMarkup
from google.appengine.ext import deferred
from validate_email import validate_email

from draw import draw_cinemahall

from screen.seances import display_seances_part
from screen.cinemas import get_nearest_cinemas
from screen.seances import get_seances
from screen.help import get_help
from screen.movie_info import display_movie_info
from screen.cinema_seances import detect_cinema_seances
from screen.running_movies import get_cinema_movies, display_running_movies
from settings import start_markup
from model.base import set_model, get_model
from model.base import UserProfile, ReturnTicket


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

    try:
        bot.sendMessage(chat_id, r, parse_mode='Markdown', reply_markup=markup)
    except:
        bot.sendMessage(chat_id, settings.DONT_UNDERSTAND)

    if 'success' in kwargs:
        try:
            bot.answerCallbackQuery(
                callback_query_id=kwargs['success'],
                text=':)'
            )
        except:
            pass

    return True


def display_help(bot, payload, cmd, chat_id):
    bot.sendMessage(
        chat_id,
        get_help(),
        parse_mode='Markdown',
        reply_markup=start_markup())


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


def callback_seance_location(tuid, bot, chat_id, text, cmd, profile):
    bot.sendChatAction(chat_id, action='typing')

    i_n = profile.cmd.index('num')
    movie_id = profile.cmd[len('/location'): i_n]
    n_seances = int(cmd[i_n + len('num'): len(cmd)])

    send_reply(
        bot, chat_id, get_seances, chat_id, movie_id, n_seances,
        msg=(settings.FIND_CINEMA
             if n_seances == settings.SEANCES_TO_DISPLAY else None)
    )


def display_location_seance(bot, payload, cmd, chat_id):
    bot.sendMessage(chat_id, settings.ENTER_LOCATION)

    try:
        bot.answerCallbackQuery(
            callback_query_id=int(payload['callback_query']['id']), text=':)'
        )

    except:
        pass


def display_movie_nearest_cinemas(tuid, bot, chat_id, text, cmd, profile):
    next_url = '/c'

    i_n = profile.cmd.index('num')
    movie_id = profile.cmd[len('/location'): i_n]

    send_reply(bot, chat_id, get_nearest_cinemas,
               bot, chat_id, settings.CINEMA_TO_SHOW, movie_id, next_url)


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


def films_category(bot, payload, cmd, chat_id):
    """
    it is mean that search in parse will be in films determination mode
    :param chat_id: pk
    :return:
    """
    deferred.defer(set_model, cls=UserProfile, pk=chat_id, state='films')


def cinema_category(bot, payload, cmd, chat_id):
    """
    it is mean that in search in parse func will be in cinema scenario
    :param chat_id: pk
    :return:
    """
    deferred.defer(set_model, cls=UserProfile, pk=chat_id, state='cinema')
    pass


def base_category(bot, payload, cmd, chat_id):
    """
    it is mean that in search in parse func will be in cinema scenario
    :param chat_id: pk
    :return:
    """
    deferred.defer(set_model, cls=UserProfile, pk=chat_id, state='base')
    display_movies(bot, payload, cmd, chat_id)
    pass


def display_seances_cinema(bot, payload, cmd, chat_id):

    if 'm' not in cmd:
        bot.sendMessage(chat_id, settings.DONT_UNDERSTAND)
        return

    index_of_m = cmd.index('m')
    cinema_id = cmd[2:index_of_m]
    bot.sendChatAction(chat_id, action='typing')

    if 'callback_query' in payload:
        index_of_d = cmd.index('d')
        movie_id, d = cmd[index_of_m + 1:index_of_d], cmd[index_of_d + 1:]

        send_reply(bot, chat_id, detect_cinema_seances,
                   cinema_id, movie_id, d,
                   success=int(payload['callback_query']['id']))
    else:
        movie_id = cmd[index_of_m + 1:]
        d = settings.TODAY
        send_reply(bot, chat_id, detect_cinema_seances,
                   cinema_id, movie_id, d)


def display_movie_time_selection(bot, payload, cmd, chat_id):
    bot.sendMessage(chat_id, settings.ENTER_DATE)

    try:
        bot.answerCallbackQuery(
            callback_query_id=int(payload['callback_query']['id']), text=':)'
        )

    except:
        pass


def callback_movie_time_selection(tuid, bot, chat_id, text, cmd, profile):
    from processing.parser import Parser

    prev_cmd = profile.cmd[len('/anytime') - 1:]
    index_of_m = prev_cmd.index('m')
    cinema_id = prev_cmd[2:index_of_m]
    index_of_d = prev_cmd.index('d')
    movie_id = prev_cmd[index_of_m + 1:index_of_d]

    deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)

    cmd, d = cmd.encode('utf-8'), None
    try:
        d = Parser.detect_time(cmd)
    except:
        bot.sendMessage(chat_id, settings.DAY_CHANGED)

    send_reply(bot, chat_id, detect_cinema_seances,
               cinema_id, movie_id, d if d else 1)
    return True


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


def callback_seance(tuid, bot, chat_id, text, cmd, profile):
    i_n, l_n = profile.cmd.index('num'), len('num')
    movie_id = profile.cmd[7: i_n]
    number_of_seances = profile.cmd[i_n + l_n: len(profile.cmd)]
    response = display_seances_part(cmd, movie_id, int(number_of_seances))
    if response is not None:
        bot.sendMessage(chat_id, response)

    deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)


def callback_return(tuid, bot, chat_id, text, cmd, profile):

    if profile.cmd[len('/return'):] == '1':
        botan.track(tuid, 'return: validation + sending', 'return')
        cmd = str(cmd).strip()
        if validate_email(cmd):
            deferred.defer(set_model, ReturnTicket, chat_id, email=cmd)
            # set_model(ReturnTicket, chat_id, email=cmd)

        else:
            bot.sendMessage(chat_id, settings.INVALID_EMAIL)
            deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)
            return

    else:
        try:
            botan.track(tuid, 'return: need email', 'return')
            order_numb = int(cmd)
            deferred.defer(set_model, ReturnTicket, chat_id, number=order_numb)
            deferred.defer(set_model, UserProfile, chat_id, cmd='/return1')
            bot.sendMessage(chat_id, settings.ENTER_ORDER_EMAIL)
        except Exception:
            bot.sendMessage(chat_id, settings.INVALID_ORDER)
            deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)
        return

    rt = get_model(ReturnTicket, chat_id)
    if rt.number and rt.email:

        r = requests.post(
            settings.URL_CANCEL_TOKEN,
            json={'order': rt.number, 'email': rt.email}
        )

        r_json = r.json()
        if r_json['error'] != 0:
            bot.sendMessage(chat_id, settings.CANCEL_ERROR)

        else:

            if r_json['data']['error'] != 0:
                botan.track(tuid, 'error in canceling', 'return')
                bot.sendMessage(chat_id, settings.CANCEL_ERROR)
            else:
                botan.track(tuid, 'returning correct', 'return')
                token = r_json['data']['token']
                url = settings.URL_CANCEL_TICKET.format(token)
                cancel_r = requests.get(url)
                bot.sendMessage(chat_id, cancel_r.json())
    else:
        bot.sendMessage(chat_id, settings.ERROR_SERVER_CONN)
        botan.track(tuid, 'invalid email or any else', 'return')