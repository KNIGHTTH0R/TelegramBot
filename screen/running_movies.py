# coding: utf-8

import contextlib
import urllib2
import gzip
import json

from datetime import datetime
from StringIO import StringIO

from telepot.namedtuple import InlineKeyboardMarkup

import settings


def display_running_movies(number_of_movies):
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
            return (settings.NO_FILMS,
                    InlineKeyboardMarkup(inline_keyboard=[[
                        dict(text=settings.FIRST_TEN,
                             callback_data=('/movies{}'.format(
                                 settings.FILMS_TO_DISPLAY)))
                    ]]))

        f_info = settings.Row(settings.uncd(movie['title']), movie['id'])

        if movie['premiereDateRussia']:
            prem_date = datetime.strptime(movie['premiereDateRussia'],
                                          '%Y-%m-%d')
            if prem_date > datetime.now():
                premiers.append(f_info)
            else:
                videos.append(f_info)
        else:
            premiers.append(f_info)

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data=('/movies{}'.format(
                  number_of_movies + settings.FILMS_TO_DISPLAY)
              ))]
    ])

    template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
    return template.render({'videos': videos, 'premiers': premiers,
                            'sign_video': settings.SIGN_VIDEO,
                            'sign_tip': settings.SIGN_TIP,
                            'sign_premier': settings.SIGN_PREMIER}), mark_up
