# -*- coding: utf8 -*-

import contextlib
import endpoints
import gzip
import json
import logging
import urllib
import urllib2
import ssl
import webapp2

from collections import namedtuple
from datetime import datetime, timedelta
from StringIO import StringIO

import telepot

from telepot.namedtuple import InlineKeyboardMarkup

from draw import draw_cinemahall

from google.appengine.api import urlfetch

import settings

Row = namedtuple('Row', ['title', 'link'])


def uncd(s):
    if isinstance(s, str):
        s = unicode(s, 'utf-8')
    else:
        s = unicode(s)
    return s


def json_me(**kwargs):
    response = webapp2.Response(content_type='application/json')
    json.dump(kwargs, response.out)
    return response


def _display_help(o):
    template = settings.JINJA_ENVIRONMENT.get_template('help.md')
    return template.render({'help': settings.SIGN_SMILE_HELP})


def _display_running_movies(number_of_movies):
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    videos, premiers = [], []
    for film_counter in xrange(number_of_movies - settings.FILMS_TO_DISPLAY,
                               number_of_movies):
        if film_counter < len(data):
            movie = data[film_counter]
        else:
            return ('К сожалению, больше нет фильмов в прокате.',
                    InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Первые 10',
                              callback_data=(
                                  '/movies{}'.format(
                                      settings.FILMS_TO_DISPLAY
                                  )))]
                    ]))
        f_info = Row(uncd(movie['title']), movie['id'])

        if movie['premiereDateRussia']:
            prem_date = datetime.strptime(movie['premiereDateRussia'],
                                          "%Y-%m-%d")
            if prem_date > datetime.now():
                premiers.append(f_info)
            else:
                videos.append(f_info)
        else:
            premiers.append(f_info)

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text='Ещё',
              callback_data=('/movies{}'.format(
                  number_of_movies + settings.FILMS_TO_DISPLAY)
              ))]
    ])

    template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
    return template.render({'videos': videos, 'premiers': premiers,
                            'sign_video': settings.SIGN_VIDEO,
                            'sign_tip': settings.SIGN_TIP,
                            'sign_premier': settings.SIGN_PREMIER}), mark_up


def _display_movie_info(movie_id):

    def get_data(name):
        return ', '.join([a.encode('utf-8') for a in html_data[name]])

    url = settings.URL_MOVIES_INFO.format(movie_id, settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        html_data = json.loads(jf.read())

    movie_poster = _get_movie_poster(html_data['poster'])
    if html_data['trailers']:
        if 'mobile_mp4' in html_data['trailers'][0]:
            kinohod_trailer_hash = (html_data['trailers'][0]
                                    ['mobile_mp4']['filename'])
            trailer_url = _get_movie_trailer_link(kinohod_trailer_hash)
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                dict(text='Трейлер', url=trailer_url),
                dict(text='Выбрать сеанс',
                     callback_data=('/seance{}num{}'.format(html_data['id'],
                                                            20)))
            ]])
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text='Выбрать сеанс',
                 callback_data=('/seance{}num{}'.format(html_data['id'],
                                                        20)))
        ]])

    template = settings.JINJA_ENVIRONMENT.get_template('movies_info.md')
    return(template.render({
        'title': html_data['title'],
        'description': html_data['annotationFull'],
        'duration': '{}'.format(html_data['duration']),
        'genres': get_data('genres').decode('utf-8'),
        'sign_actor': settings.SIGN_ACTOR,
        'actors': get_data('actors').decode('utf-8'),
        'producers': get_data('producers').decode('utf-8'),
        'directors': get_data('directors').decode('utf-8')}), markup,
           movie_poster)


def _display_seances(movie_id, number_of_seances):
    url = settings.URL_SEANCES.format(str(movie_id), settings.KINOHOD_API_KEY,
                                      (number_of_seances -
                                       settings.SEANCES_TO_DISPLAY),
                                      number_of_seances)
    seances = []
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        html_data = json.loads(jf.read())

    for info in html_data:
        seances.append(
            Row(uncd(info['cinema']['shortTitle']),
                '(/c{}m{})'.format(info['cinema']['id'], info['movie']['id']))
        )
    if not html_data:
        template = settings.JINJA_ENVIRONMENT.get_template('no_seances.md')
        return template.render({})

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text='Ещё',
              callback_data=('/seance{}num{}'.
                             format(movie_id, (
                                number_of_seances + settings.SEANCES_TO_DISPLAY
                             ))))]])
    template = settings.JINJA_ENVIRONMENT.get_template('seances.md')
    return template.render({
        'sign_tip': settings.SIGN_TIP,
        'seances': seances
    }), mark_up


def _display_cinema_seances(cinema_id, movie_id, day):
    day = int(day)
    day_str = _day_of_seance(day)

    url = settings.URL_CINEMA_SEANCES.format(
        cinema_id, settings.KINOHOD_API_KEY, day_str
    )
    with contextlib.closing(urllib2.urlopen(url)) as hd:
        html_data = json.loads(hd.read())

    f = namedtuple('f', ['tip', 'time', 'minPrice', 'id'])
    for info in html_data:
        if int(movie_id) != int(info['movie']['id']):
            continue
        seances = []
        for s in info['schedules']:
            if _calculate_is_onsale(s['startTime']):
                seances.append(
                    f(settings.SIGN_TIP, s['time'],
                      s['minPrice'], int(s['id']))
                )
            else:
                seances.append(
                    f(settings.SIGN_TIP, s['time'], s['minPrice'], 0)
                )
        markup = _construct_markup(cinema_id, movie_id, day)
        template = settings.JINJA_ENVIRONMENT.get_template('cinema_seances.md')
        return template.render(
            {'title': info['movie']['title'], 'seances': seances}
        ), markup


def _calculate_is_onsale(start_time_str):
    start_time = datetime.strptime(start_time_str[0:16],
                                   '%Y-%m-%dT%H:%M')

    if start_time_str[19] == '+':
        start_time -= timedelta(hours=int(start_time_str[20:22]),
                                seconds=int(start_time_str[22:]))
    elif start_time_str[19] == '-':
        start_time += timedelta(hours=int(start_time_str[20:22]),
                                seconds=int(start_time_str[22:]))

    now = datetime.utcnow()
    delta = start_time - now

    if delta < timedelta(minutes=30):
        return False
    else:
        return True


def _convert_digit_repr(digit):
    if int(digit) < 10:
        return '0{}'.format(digit)
    return digit


def _day_of_seance(day):
    day_str = ''
    if day == settings.TODAY:
        today = datetime.now()
        day_str = '{}{}{}'.format(_convert_digit_repr(today.day),
                                  _convert_digit_repr(today.month),
                                  _convert_digit_repr(today.year))

    elif day == settings.TOMORROW:
        tomorrow = datetime.now() + timedelta(days=settings.TOMORROW)
        day_str = '{}{}{}'.format(_convert_digit_repr(tomorrow.day),
                                  _convert_digit_repr(tomorrow.month),
                                  _convert_digit_repr(tomorrow.year))

    elif day == settings.DAY_AFTER_TOMORROW:
        d_a_tomorrow = (datetime.now() +
                        timedelta(days=settings.DAY_AFTER_TOMORROW))
        day_str = '{}{}{}'.format(_convert_digit_repr(d_a_tomorrow.day),
                                  _convert_digit_repr(d_a_tomorrow.month),
                                  _convert_digit_repr(d_a_tomorrow.year))
    return day_str


def _construct_markup(cinema_id, movie_id, day):

    if day == 0:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text='На завтра',
                 callback_data=('/c{}m{}d{}'.format(cinema_id, movie_id, 1))),
            dict(text='На послезавтра',
                 callback_data=('/c{}m{}d{}'.format(cinema_id, movie_id, 2)))

        ]])

    if day == 1:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text='На сегодня',
                 callback_data=('/c{}m{}d{}'.format(cinema_id, movie_id, 0))),
            dict(text='На послезавтра',
                 callback_data=('/c{}m{}d{}'.format(cinema_id, movie_id, 2)))

        ]])

    if day == 2:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text='На сегодня',
                 callback_data=('/c{}m{}d{}'.format(cinema_id, movie_id, 0))),
            dict(text='На завтра',
                 callback_data=('/c{}m{}d{}'.format(cinema_id, movie_id, 1)))

        ]])

    return markup


def _get_movie_poster(poster_hash):
    ab = poster_hash[0:2]
    cd = poster_hash[2:4]
    url = 'https://kinohod.ru/o/{}/{}/{}'.format(ab, cd, poster_hash)
    poster = urllib2.urlopen(url)
    return poster


def _get_movie_trailer_link(trailer_hash):
    ab = trailer_hash[0:2]
    cd = trailer_hash[2:4]
    url = 'https://kinohod.ru/o/{}/{}/{}'.format(ab, cd, trailer_hash)
    return url


class CommandReceiveView(webapp2.RequestHandler):

    def post(self):

        telegram_bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
        logger = logging.getLogger('telegram.bot')

        urlfetch.set_default_fetch_deadline(60)

        commands = {
            '/start': _display_help,
            '/movies': _display_running_movies
        }

        raw = self.request.body.decode('utf-8')

        logger.info(raw)

        try:
            payload = json.loads(raw)
            self.response.write(json.dumps(payload))
        except ValueError:
            raise endpoints.BadRequestException(message='Invalid request body')
        else:

            if 'message' in payload:
                chat_id = payload['message']['chat']['id']
                cmd = payload['message'].get('text')  # command

            if 'callback_query' in payload:
                cmd = payload['callback_query']['data']
                callback_query_id = int(payload['callback_query']['id'])
                chat_id = payload['callback_query']['message']['chat']['id']
                if cmd.startswith('/seance'):
                    index_of_n = cmd.index('num')
                    movie_id = cmd[7: index_of_n]
                    number_of_seances = cmd[index_of_n + len('num'): len(cmd)]
                    response, mark_up = _display_seances(movie_id,
                                                         int(
                                                             number_of_seances)
                                                         )

                    chat_id = payload['callback_query']['message']['chat'][
                        'id']
                    if mark_up:
                        telegram_bot.sendMessage(
                            chat_id,
                            response,
                            parse_mode='Markdown',
                            reply_markup=mark_up)
                    else:
                        telegram_bot.sendMessage(
                            chat_id,
                            response,
                            parse_mode='Markdown')

                    telegram_bot.answerCallbackQuery(
                        callback_query_id=callback_query_id,
                        text=':)')
                elif cmd.startswith('/movies'):
                    number_to_display = int(cmd[7:len(cmd)])
                    response, markup = _display_running_movies(
                        number_to_display
                    )
                    telegram_bot.sendMessage(
                        chat_id,
                        response,
                        reply_markup=markup)
                    telegram_bot.answerCallbackQuery(
                        callback_query_id=callback_query_id,
                        text=':)')

                elif cmd.startswith('/c'):
                    index_of_m = cmd.index('m')
                    index_of_d = cmd.index('d')
                    cinema_id = cmd[2:index_of_m]
                    movie_id = cmd[index_of_m + 1:index_of_d]
                    day = cmd[-1]
                    response, markup = _display_cinema_seances(cinema_id,
                                                               movie_id,
                                                               day)
                    telegram_bot.sendMessage(
                        chat_id,
                        response,
                        parse_mode='Markdown',
                        reply_markup=markup)

                    telegram_bot.answerCallbackQuery(
                        callback_query_id=callback_query_id,
                        text=':)')

            elif cmd.startswith('/schedule'):
                schedule_id = cmd[9:len(cmd)]
                try:
                    hall_image = draw_cinemahall(schedule_id)
                    telegram_bot.sendChatAction(chat_id, 'upload_photo')
                    telegram_bot.sendPhoto(
                        chat_id,
                        ('hall.bmp', hall_image)
                    )
                    city_name_dict = {'cityName': u'Москва'.encode('utf-8')}
                    url_encoded_dict = urllib.urlencode(city_name_dict)
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Купить билеты',
                              url=('https://kinohod.ru/widget/?{}'
                                   '#scheme_{}'.format(url_encoded_dict,
                                                       schedule_id)))]
                    ])
                    telegram_bot.sendMessage(
                        chat_id,
                        'Серые - занято. Синие - свободно.',
                        reply_markup=markup, )
                except:
                    telegram_bot.sendMessage(
                        chat_id,
                        'Увы, сервер недоступен.')

            elif cmd.startswith('/info'):
                movie_id = cmd[5:len(cmd)]
                message, mark_up, movie_poster = _display_movie_info(movie_id)
                telegram_bot.sendChatAction(chat_id, 'upload_photo')
                telegram_bot.sendPhoto(
                    chat_id,
                    ('poster.jpg', movie_poster)
                )
                telegram_bot.sendMessage(
                    chat_id,
                    message,
                    reply_markup=mark_up,
                    parse_mode='Markdown')

            elif cmd.startswith('/c'):
                index_of_m = cmd.index('m')
                cinema_id = cmd[2:index_of_m]
                movie_id = cmd[index_of_m + 1:len(cmd)]
                response, markup = _display_cinema_seances(cinema_id,
                                                           movie_id,
                                                           settings.TODAY)
                telegram_bot.sendMessage(
                    chat_id,
                    response,
                    parse_mode='Markdown',
                    reply_markup=markup)

            elif cmd.startswith('/movies'):
                response, markup = _display_running_movies(
                    settings.FILMS_TO_DISPLAY
                )
                telegram_bot.sendMessage(chat_id, response, reply_markup=markup)

            else:
                func = commands.get(cmd.split()[0].lower())
                if func:
                    text = func()
                    telegram_bot.sendMessage(chat_id, text)

                else:
                    telegram_bot.sendMessage(chat_id,
                                            'I do not understand you, Sir!')

