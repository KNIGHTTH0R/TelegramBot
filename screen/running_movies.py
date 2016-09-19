# coding: utf-8

import contextlib
import urllib2
import gzip
import json

from datetime import datetime
from StringIO import StringIO

from telepot.namedtuple import InlineKeyboardMarkup

import settings


def process_movies(data, number_of_movies, callback_url):
    videos, premiers = [], []

    to_show = settings.FILMS_TO_DISPLAY
    if len(data) == 0:
        to_show = 0

    elif len(data) < settings.FILMS_TO_DISPLAY:
        to_show = len(data)

    for film_counter in xrange(number_of_movies - to_show,
                               number_of_movies):

        if film_counter < len(data):
            movie = data[film_counter]
        else:
            return (settings.NO_FILMS,
                    InlineKeyboardMarkup(inline_keyboard=[[
                        dict(text=settings.FIRST_TEN,
                             callback_data=(callback_url.format(
                                 settings.FILMS_TO_DISPLAY)))
                    ]]))

        f_info = settings.Row(settings.uncd(movie['title']), movie['id'])

        if movie['premiereDateRussia']:
            t_str = movie['premiereDateRussia']
            if 'T' in t_str:
                t_str = t_str.split('T')[0]

            prem_date = datetime.strptime(t_str, '%Y-%m-%d')
            now = datetime.utcnow()
            if prem_date > now:
                premiers.append(f_info)
            else:
                videos.append(f_info)
        else:
            premiers.append(f_info)

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data=(callback_url.format(
                  number_of_movies + settings.FILMS_TO_DISPLAY)
              ))]
    ])

    template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
    return template.render({'videos': videos, 'premiers': premiers,
                            'sign_video': settings.SIGN_VIDEO,
                            'sign_tip': settings.SIGN_TIP,
                            'sign_premier': settings.SIGN_PREMIER}), mark_up


def display_running_movies(number_of_movies):
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    callback_url = '/movies{}'
    return process_movies(data, number_of_movies, callback_url)


def get_cinema_movies(cinema_id, number_of_movies, bot, chat_id):
    url = settings.URL_CINEMA_MOVIE.format(cinema_id, settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        data = json.loads(jf.read())

    data = [d['movie'] for d in data]
    callback_url = '/show' + str(cinema_id) + 'v{}'

    if len(data) < number_of_movies:
        number_of_movies = len(data)

    return process_movies(data, number_of_movies, callback_url)
