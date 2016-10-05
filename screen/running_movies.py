# coding: utf-8

import contextlib
import urllib2
import gzip
import json

from collections import namedtuple

from datetime import datetime
from StringIO import StringIO

from telepot.namedtuple import InlineKeyboardMarkup

from model.film import Film

import settings

IMovieCinema = namedtuple('IMovieCinema', ['title', 'link', 'link_info'])


def process_movies(data, number_of_movies, callback_url,
                   next_url='/info', **kwargs):

    cinema_id = kwargs.get('cinema_id')
    separator = kwargs.get('separator')
    next_info_url = kwargs.get('info_url')

    videos, premiers = [], []

    to_show = settings.FILMS_TO_DISPLAY
    if len(data) == 0:
        to_show = 0

    elif len(data) < settings.FILMS_TO_DISPLAY:
        to_show = len(data)

    expanded_info = False
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

        if cinema_id and separator and next_info_url:
            expanded_info = True

            link = '{}{}{}{}'.format(next_url, cinema_id,
                                     separator, movie['id'])
            f_info = IMovieCinema(
                movie['title'], link,
                '{}{}'.format(next_info_url, movie['id'])
            )

        else:
            link = '{}{}'.format(next_url, movie['id'])
            f_info = settings.Row(settings.uncd(movie['title']), link)

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

    if expanded_info:
        template = (settings.JINJA_ENVIRONMENT.
                    get_template('running_movies_ext.md'))

        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_calendar': settings.SIGN_CALENDAR,
                               'sign_newspaper': settings.SIGN_NEWSPAPER,
                               'sign_premier': settings.SIGN_PREMIER})
    else:
        template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_premier': settings.SIGN_PREMIER})

    return msg, mark_up


def display_running_movies_api(number_of_movies):
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    callback_url = '/movies{}'
    return process_movies(data, number_of_movies, callback_url)


def process_movies_db(number_of_movies, callback_url,
                      next_url='/info', **kwargs):

    data = Film.query().fetch(
        offset=number_of_movies - settings.FILMS_TO_DISPLAY,
        limit=settings.FILMS_TO_DISPLAY
    )

    cinema_id = kwargs.get('cinema_id')
    separator = kwargs.get('separator')
    next_info_url = kwargs.get('info_url')

    videos, premiers = [], []

    expanded_info = False
    for f in data:

        if cinema_id and separator and next_info_url:
            expanded_info = True

            link = '{}{}{}{}'.format(next_url, cinema_id,
                                     separator, f.kinohod_id)
            f_info = IMovieCinema(
                f.title, link,
                '{}{}'.format(next_info_url, f.kinohod_id)
            )

        else:
            link = '{}{}'.format(next_url, f.kinohod_id)
            f_info = settings.Row(settings.uncd(f.title), link)

        if f.premiereDateRussia:
            now = datetime.utcnow()
            if f.premiereDateRussia > now:
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

    if expanded_info:
        template = (settings.JINJA_ENVIRONMENT.
                    get_template('running_movies_ext.md'))

        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_calendar': settings.SIGN_CALENDAR,
                               'sign_newspaper': settings.SIGN_NEWSPAPER,
                               'sign_premier': settings.SIGN_PREMIER})
    else:
        template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_premier': settings.SIGN_PREMIER})

    return msg, mark_up


def display_running_movies(number_of_movies):
    callback_url = '/movies{}'
    return process_movies_db(number_of_movies, callback_url)


def get_cinema_movies(cinema_id, number_of_movies):
    url = settings.URL_CINEMA_MOVIE.format(cinema_id, settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        data = json.loads(jf.read())

    data = [d['movie'] for d in data]
    callback_url = '/show' + str(cinema_id) + 'v{}'

    if len(data) < number_of_movies:
        number_of_movies = len(data)

    return process_movies(data, number_of_movies, callback_url,
                          next_url='/c', info_url='/info',
                          cinema_id=cinema_id, separator='m')
