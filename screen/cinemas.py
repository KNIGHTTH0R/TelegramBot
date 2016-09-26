# coding: utf-8

from collections import namedtuple

import contextlib
import urllib2
import json

from model import get_model
from model import UserProfile

import settings

from telepot.namedtuple import InlineKeyboardMarkup


Cinema = namedtuple('Cinema', ['title', 'link', 'subways'])
Subway = namedtuple('Subway', ['name', 'distance'])


def get_data(url):
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        return json.loads(jf.read())


def get_nearest_cinemas(bot, chat_id, number_of_cinemas):

    u = get_model(UserProfile, chat_id)
    if not u.location:
        bot.sendMessage(chat_id, settings.CANNOT_FIND_YOU)
        return None, None

    l = json.loads(u.location)
    latitude, longitude = l['latitude'], l['longitude']
    url = '{}?lat={}&long={}&sort=distance&cityId=1'.format(
        settings.URL_WIDGET_CINEMAS,
        latitude,
        longitude,
    )

    r = get_data(url)
    data = r['data'] if 'data' in r else None

    cinemas = []
    template = settings.JINJA_ENVIRONMENT.get_template('cinema.md')
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

        subways = []
        if 'subwayStations' in cinema:
            for m in cinema['subwayStations']:
                s = Subway(m['name'], m['distance'])
                if s.name and s.distance:
                    subways.append(s)

        cinemas.append(
            Cinema(
                cinema['shortTitle'],
                '/show{}'.format(cinema['id']),
                subways
            )
        )

        # add this to cinema.md to use metro stations
        # {% for m in s.subways -%}
        #     {{ help }} {{ m.name }} {{ m.distance }}м
        # {% endfor %}

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data='/nearest{}'.format(
                  number_of_cinemas + settings.CINEMA_TO_SHOW
              ))]
    ])

    return template.render({
        'help': settings.SIGN_SMILE_HELP,
        'cinemas': cinemas
    }), mark_up
