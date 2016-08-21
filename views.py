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
from datetime import datetime
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


def _display_running_movies(o):
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)

    with contextlib.closing(urllib2.urlopen(url)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    videos, premiers = [], []
    for film_counter in xrange(settings.FILMS_TO_DISPLAY):
        movie = data[film_counter]
        f_info = Row(uncd(movie['title']), movie['id'])

        prem_date = datetime.strptime(movie['premiereDateRussia'], "%Y-%m-%d")
        if prem_date > datetime.now():
            premiers.append(f_info)
        else:
            videos.append(f_info)

    template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
    return template.render({'videos': videos, 'premiers': premiers,
                            'sign_video': settings.SIGN_VIDEO,
                            'sign_tip': settings.SIGN_TIP,
                            'sign_premier': settings.SIGN_PREMIER})


def _display_movie_info(o, movie_id):

    def get_data(name):
        return ', '.join([a.encode('utf-8') for a in html_data[name]])

    url = settings.URL_MOVIES_INFO.format(movie_id, settings.KINOHOD_API_KEY)

    with contextlib.closing(urllib2.urlopen(url)) as jf:
        html_data = json.loads(jf.read())

    markup = InlineKeyboardMarkup(inline_keyboard=[[
        dict(text='IMDB', url=settings.URL_IMDB.format(html_data['imdb_id'])),
        dict(text=settings.CHOOSE_SEANCE,
             callback_data=('/seance{}'.format(html_data['id'])))
    ]])

    template = settings.JINJA_ENVIRONMENT.get_template('movies_info.md')
    return template.render({
        'title': html_data['title'],
        'description': html_data['annotationFull'],
        'duration': '{}'.format(html_data['duration']),
        'genres': get_data('genres').decode('utf-8'),
        'sign_actor': settings.SIGN_ACTOR,
        'actors': get_data('actors').decode('utf-8'),
        'producers': get_data('producers').decode('utf-8'),
        'directors': get_data('directors').decode('utf-8')}), markup


def _display_seances(o, movie_id):
    url = settings.URL_SEANCES.format(movie_id, settings.KINOHOD_API_KEY)

    with contextlib.closing(urllib2.urlopen(url)) as jf:

        html_data = json.loads(jf.read())

    seances = []
    for info in html_data:
        seances.append(
            Row(uncd(info['cinema']['shortTitle']),
                '(/c{}m{})'.format(info['cinema']['id'],
                                   info['movie']['id']))
        )

    if not html_data:
        template = settings.JINJA_ENVIRONMENT.get_template('no_seances.md')
        return template.render({})

    template = settings.JINJA_ENVIRONMENT.get_template('seances.md')
    return template.render({
        'sign_tip': settings.SIGN_TIP,
        'seances': seances
    })


def _display_cinema_seances(o, cinema_id, movie_id):
    url = settings.URL_CINEMA_SEANCES.format(
        cinema_id, settings.KINOHOD_API_KEY
    )

    with contextlib.closing(urllib2.urlopen(url)) as hd:

        html_data = json.loads(hd.read())

    f = namedtuple('f', ['tip', 'time', 'minPrice', 'id'])
    for info in html_data:
        if int(movie_id) != int(info['movie']['id']):
            continue

        seances = [f(settings.SIGN_TIP, s['time'], s['minPrice'], s['id'])
                   for s in info['schedules']]

        template = settings.JINJA_ENVIRONMENT.get_template('cinema_seances.md')
        return template.render(
            {'title': info['movie']['title'], 'seances': seances}
        )


class CommandReceiveView(webapp2.RequestHandler):

    def post(self):

        telegram_bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
        logger = logging.getLogger('telegram.bot')

        urlfetch.set_default_fetch_deadline(60)
        # if bot_token != settings.TELEGRAM_BOT_TOKEN:
        #     raise endpoints.ForbiddenException(message='Invalid token')

        commands = {
            '/start': _display_help,
            '/movies': _display_running_movies
            # '/info': _display_movie_info(self),
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
                movie_id = cmd[7: len(cmd)]
                response = _display_seances(self, movie_id)
                chat_id = payload['callback_query']['message']['chat']['id']
                telegram_bot.sendMessage(
                    chat_id,
                    response,
                    parse_mode='Markdown')
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
                message, mark_up = _display_movie_info(self, movie_id)
                telegram_bot.sendMessage(
                    chat_id,
                    message,
                    reply_markup=mark_up,
                    parse_mode='Markdown')
            elif cmd.startswith('/c'):
                index_of_m = cmd.index('m')
                cinema_id = cmd[2:index_of_m]
                movie_id = cmd[index_of_m+1:len(cmd)]
                response = _display_cinema_seances(self, cinema_id, movie_id)
                telegram_bot.sendMessage(
                    chat_id,
                    response,
                    parse_mode='Markdown')
            else:
                func = commands.get(cmd)
                if func:
                    text = func(self)
                    telegram_bot.sendMessage(chat_id, text)
                else:
                    telegram_bot.sendMessage(chat_id,
                                             'I do not understand you, Sir!')
                    telegram_bot.sendMessage(chat_id, payload)
                    # telegram_bot.sendMessage(chat_id, cmd)

