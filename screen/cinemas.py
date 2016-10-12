# coding: utf-8

from collections import namedtuple

import contextlib
import urllib2
import json

from cinema_where_film import get_cinemas_where_film

from model.base import get_model
from model.base import UserProfile
from model.film import Film

from google.appengine.ext import ndb

import settings

from telepot.namedtuple import InlineKeyboardMarkup


Cinema = namedtuple('Cinema', ['title', 'link', 'subways'])
Subway = namedtuple('Subway', ['name', 'distance'])


def get_data(url):
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        return json.loads(jf.read())


def get_nearest_cinemas(bot, chat_id, number_of_cinemas,
                        movie_id=None, next_url='/show'):

    # TODO: REWRITE THIS PEACE OF SHIT, PLEASE

    u = get_model(UserProfile, chat_id)
    if not u.location:
        bot.sendMessage(chat_id, settings.CANNOT_FIND_YOU)
        return None, None

    l = json.loads(u.location)
    url = '{}?lat={}&long={}&sort=distance&cityId=1'.format(
        settings.URL_WIDGET_CINEMAS, l.get('latitude'), l.get('longitude'),
    )

    film = None
    if movie_id:
        film = Film.get_by_id(str(movie_id))

    r = get_data(url)
    data = r.get('data')

    if not data:
        return settings.DONT_UNDERSTAND, None

    cinemas = []
    template = settings.JINJA_ENVIRONMENT.get_template('cinema_where_film.md')
    for film_counter in xrange(number_of_cinemas - settings.CINEMA_TO_SHOW,
                               number_of_cinemas):

        if film_counter < len(data):
            cinema = data[film_counter]
        else:
            return (settings.NO_FILMS,
                    InlineKeyboardMarkup(inline_keyboard=[[
                        dict(text=settings.FIRST_THREE,
                             callback_data=('/nearest{}'.format(
                                 settings.CINEMA_TO_SHOW)))
                    ]]))

        cinema_id = str(cinema.get('id'))
        cinema_title = cinema.get('shortTitle')
        if film and cinema_id:
            # TODO: REWRITE IT IN FREE TIME
            if ndb.Key('Cinema', cinema_id) not in film.cinemas:
                continue

            link = '{}{}m{}'.format(next_url, cinema_id, movie_id)

        else:
            link = '{}{}'.format(next_url, cinema_id)

        cinemas.append(
            settings.RowCinema(
                cinema_title,
                cinema.get('address'),
                cinema.get('mall'),
                link
            )
        )

    if film and len(cinemas) < 1:
        return get_cinemas_where_film(film)

    if film:
        mark_up = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text=settings.MORE,
                  callback_data='/nearest{}m{}'.format(
                      number_of_cinemas + settings.CINEMA_TO_SHOW,
                      movie_id
                  ))]
        ])
    else:
        mark_up = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text=settings.MORE,
                  callback_data='/nearest{}'.format(
                      number_of_cinemas + settings.CINEMA_TO_SHOW
                  ))]
        ])

    film_name = film.title if film else None
    return template.render({
        'film_name': film_name,
        'seances': cinemas
    }), mark_up


def cinemas_from_data(data, movie_id=None):
    cinemas = []

    link = '/c{}m{}' if movie_id else '/show{}'

    for p in data:
        link = (link.format(p.kinohod_id, movie_id)
                if movie_id else link.format(p.kinohod_id))

        cinemas.append(
            settings.RowCinema(
                p.shortTitle,
                p.address,
                p.mall,
                link
            )
        )

    template = settings.JINJA_ENVIRONMENT.get_template('cinema.md')
    return template.render({'cinemas': cinemas})
