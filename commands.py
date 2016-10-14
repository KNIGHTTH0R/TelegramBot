# coding: utf-8

import urllib
import requests

from datetime import datetime, timedelta

import botan

from telepot.namedtuple import InlineKeyboardMarkup
from google.appengine.ext import deferred
from validate_email import validate_email

from draw import draw_cinemahall

from screen.seances import display_seances_part
from screen.cinemas import get_nearest_cinemas
from screen.seances import get_seances, display_seances_all
from screen.help import get_help
from screen.movie_info import display_movie_info
from screen.cinema_seances import detect_cinema_seances
from screen.running_movies import (get_cinema_movies, display_running_movies,
                                   display_running_movies_api)
from screen.cinema_where_film import get_cinemas_where_film
from settings import start_markup
from model.base import set_model, get_model
from model.film import Film
from model.base import UserProfile, ReturnTicket
from processing.parser import Parser

import settings


def send_reply(bot, chat_id, func, *args, **kwargs):
    r = func(*args)

    if 'msg' in kwargs and kwargs['msg']:
        bot.sendMessage(chat_id, kwargs['msg'],
                        parse_mode=kwargs.get('parse_mode'))

    markup = None
    if isinstance(r, tuple):
        r, markup = r

    if r is None:
        return False

    try:
        bot.sendMessage(chat_id, r, parse_mode='Markdown', reply_markup=markup)
    except:
        bot.sendMessage(chat_id, settings.DONT_UNDERSTAND,
                        parse_mode='Markdown')

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

    base_url = '/nearest'
    movie_id = None

    if 'callback_query' in payload:
        if 'm' in cmd:
            m_index = cmd.index('m')
            number_to_display = int(cmd[len(base_url): m_index])
            movie_id = int(cmd[m_index + 1:])
            next_url = '/c'
        else:
            number_to_display = int(cmd[len(base_url):])
            next_url = '/show'

        send_reply(bot, chat_id, get_nearest_cinemas,
                   bot, chat_id, number_to_display, movie_id, next_url,
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


def display_cinemas_where_film(bot, payload, cmd, chat_id):

    if 'callback_query' not in payload:
        return

    bot.answerCallbackQuery(
        callback_query_id=int(payload['callback_query']['id']), text=':)'
    )

    index_num = cmd.index('num')
    movie_id = int(cmd[len('/where_film'): index_num])
    num = int(cmd[index_num + len('num'):])

    film = Film.get_by_id(str(movie_id))
    send_reply(bot, chat_id, get_cinemas_where_film, film, num)


def display_movie_nearest_cinemas(tuid, bot, chat_id, text, cmd, profile):
    next_url = '/c'
    i_n = profile.cmd.index('num')
    movie_id = profile.cmd[len('/location'): i_n]
    send_reply(bot, chat_id, get_nearest_cinemas,
               bot, chat_id, settings.CINEMA_TO_SHOW, movie_id, next_url)


def display_cinema(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')

    if 'in' in cmd:
        in_index = cmd.index('in')
        date = cmd[in_index + 2:]
        cmd = cmd[:in_index]
    else:
        date = datetime.now().strftime('%d%m%Y')

    if 'callback_query' in payload:
        index_of_v = cmd.index('v')
        cinema_id = int(cmd[len('/show'): index_of_v])
        number_to_display = int(cmd[index_of_v + 1:])
        send_reply(bot, chat_id, get_cinema_movies,
                   cinema_id, number_to_display, date,
                   success=int(payload['callback_query']['id']))
    else:
        cinema_id = int(cmd[len('/show'):])
        send_reply(bot, chat_id, get_cinema_movies, cinema_id,
                   settings.FILMS_TO_DISPLAY, date)


def display_movies(bot, payload, cmd, chat_id):
    bot.sendChatAction(chat_id, action='typing')
    if 'callback_query' in payload:
        number_to_display = int(cmd[7:len(cmd)])
        # display_running_movies
        send_reply(bot, chat_id, display_running_movies_api,
                   number_to_display,
                   success=int(payload['callback_query']['id']))
    else:
        # display_running_movies
        send_reply(bot, chat_id,
                   display_running_movies_api, settings.FILMS_TO_DISPLAY)


def films_category(bot, payload, cmd, chat_id):
    """
    it is mean that search in parse will be in films determination mode
    :param chat_id: pk
    :return:
    """
    # deferred.defer(set_model, cls=UserProfile, pk=chat_id, state='films')
    display_movies(bot, payload, cmd, chat_id)


def cinema_category(bot, payload, cmd, chat_id):
    """
    it is mean that in search in parse func will cinema status
    :param chat_id: pk
    :return:
    """
    # deferred.defer(set_model, cls=UserProfile, pk=chat_id, state='cinema')
    pass


# def base_category(bot, payload, cmd, chat_id):
#     """
#     it is mean that in search in parse func will be in cinema scenario
#     :param chat_id: pk
#     :return:
#     """
#     deferred.defer(set_model, cls=UserProfile, pk=chat_id, state='base')
#     pass


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
        if 'd' in cmd:
            index_of_d = cmd.index('d')
            movie_id, d = cmd[index_of_m + 1:index_of_d], cmd[index_of_d + 1:]
            d = datetime.strptime(d, '%d%m%Y')
        else:
            movie_id = cmd[index_of_m + 1:]
            d = settings.TODAY

        send_reply(bot, chat_id, detect_cinema_seances,
                   cinema_id, movie_id, d)


def callback_seance_text(tuid, bot, chat_id, text, cmd, profile):

    # in profile.cmd should be movie id
    # need concatenate movie with place

    if 'num' not in profile.cmd:
        return

    i_n = profile.cmd.index('num')
    movie_id = profile.cmd[len('/location'): i_n]

    film = Film.get_by_id(movie_id)

    if not film.cinemas or len(film.cinemas) < 1:
        bot.sendMessage(chat_id, settings.NO_FILM_SEANCE)
        return

    cmd = cmd.encode('utf-8')
    parser = Parser(request=cmd, state='cinema')
    parser.parse()

    bot.sendChatAction(chat_id, action='typing')

    seances = []

    if not parser.data.place:
        pass
        # bot.sendMessage(chat_id, settings.CINEMA_NOT_FOUND)
    else:
        for p in parser.data.place:
            if not p or p.key not in film.cinemas:
                continue

            seances.append(
                settings.RowCinema(
                    p.shortTitle, p.address, p.mall,
                    '/c{}m{}'.format(p.kinohod_id, movie_id)
                )
            )

    if len(seances) < 1:
        bot.sendMessage(chat_id, settings.NO_FILM_SEANCE)
        send_reply(bot, chat_id, get_cinemas_where_film, film)
        return

    template = settings.JINJA_ENVIRONMENT.get_template('cinema_where_film.md')
    msg = template.render({'film_name': film.title, 'seances': seances})

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data='/where_film{}num{}'.format(
                  film.kinohod_id,
                  settings.CINEMAS_TO_DISPLAY
              ))]
    ])

    bot.sendMessage(chat_id, msg, parse_mode='Markdown', reply_markup=mark_up)


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


def display_full_info(bot, payload, cmd, chat_id):
    display_info(bot, payload, cmd, chat_id,
                 full=True,
                 prefix_length=len('/fullinfo'))


def display_info(bot, payload, cmd, chat_id, full=False,
                 prefix_length=len('/info')):

    t_uid = payload['message']['from']['id']
    movie_id = cmd[prefix_length:len(cmd)]

    if not str(movie_id).isdigit():
        bot.sendMessage(chat_id, settings.INFO_NOT_FULL.format(movie_id))
        return

    film = Film.get_by_id(str(movie_id))
    now = datetime.now()
    two_weeks = timedelta(days=14)

    if (len(film.cinemas) < 1 and
        not ((film.premiereDateRussia and
              (now < film.premiereDateRussia < (now + two_weeks))) or
             (film.premiereDateWorld and
              (now < film.premiereDateWorld < (now + two_weeks))))):
        return

    message, mark_up, movie_poster = display_movie_info(
        movie_id, t_uid, next_url='/location', full=full
    )

    if not message:
        bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
        return

    if movie_poster:
        bot.sendChatAction(chat_id, 'upload_photo')
        bot.sendPhoto(chat_id, ('poster.jpg', movie_poster))

    bot.sendMessage(chat_id, message, reply_markup=mark_up,
                    parse_mode='Markdown')


def display_future_seances(bot, payload, cmd, chat_id):
    if 'callback_query' in payload:
        if '/future' not in cmd:
            bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
            return

        movie_id = cmd[len('/future'):]
        film = Film.get_by_id(movie_id)

        premier = film.premiereDateRussia
        if not premier or not isinstance(premier, datetime):
            bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
            return

        send_reply(
            bot, chat_id, display_seances_all,
            movie_id, settings.SEANCES_TO_DISPLAY, premier.strftime('%d%m%Y'),
            success=int(payload['callback_query']['id'])
        )


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