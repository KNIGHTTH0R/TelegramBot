# coding: utf-8

import logging
import contextlib
import urllib2
import json
import gzip
import time

from datetime import datetime
from itertools import chain
from StringIO import StringIO

import settings


def get_list_of_cities():
    url_cities = '{}?apikey={}'.format(settings.URL_CITIES,
                                       settings.KINOHOD_API_KEY)

    with contextlib.closing(urllib2.urlopen(url_cities)) as jf:
        return json.loads(jf.read())


def get_data(state):
    out_data = {'film': None, 'place': None}

    def get_film_data():
        url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
            data = json.loads(stream.read())
        out_data['film'] = {film['title']: film for film in data}

        url = settings.URL_SOON_MOVIES.format(settings.KINOHOD_API_KEY)
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            data_soon = json.loads(jf.read())

        for f in data_soon:
            out_data['film'][f['title']] = f

    def get_place_data():
        cities = get_list_of_cities()
        data_places = []
        for city in cities:
            url_cinema = '{}&city={}'.format(
                settings.URL_CINEMAS.format(settings.KINOHOD_API_KEY),
                city['id']
            )
            with contextlib.closing(urllib2.urlopen(url_cinema)) as jf:
                data_places += json.loads(jf.read())
        out_data['place'] = {(c['shortTitle'], c['mall'], c['address']): c
                             for c in data_places}
    data_scenario = {
        'base': [get_film_data, get_place_data],
        'film': [get_film_data],
        'cinema': [get_place_data],
        'time': []
    }

    # TODO: make it faster like multiprocessing tasks, but not on gae
    # it may be deferred package
    for func in data_scenario[state]:
        func()
    return out_data['film'], out_data['place']


def get_genres(genre_id):
    # TODO, I KNOW THAT IT IS A STUPID IDEA TO GET OBJECT INSTED OF JSON,
    # TODO: BUT IF YOU WANT

    url = settings.URL_GENRES.format(genre_id, settings.KINOHOD_API_KEY)
    url_s = settings.URL_GENRES_SOON.format(genre_id, settings.KINOHOD_API_KEY)

    with contextlib.closing(urllib2.urlopen(url)) as jf:
        genres = json.loads(jf.read())

    with contextlib.closing(urllib2.urlopen(url_s)) as jf:
        genres_soon = json.loads(jf.read())

    return chain(genres, genres_soon)


def get_url_json(url):
    try:
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            return json.loads(jf.read())
    except Exception as e:
        import logging
        logging.debug(e.message)


def get_schedule(film_id, date, city_id=1):
    date = (datetime.now().strftime('%d%m%Y')
            if not date
            else date.strftime('%d%m%Y'))

    url = settings.URL_FULL_SEANCES_CITY.format(
        film_id, settings.KINOHOD_API_KEY, date, city_id
    )

    return get_url_json(url)

