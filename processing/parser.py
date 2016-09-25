# coding: utf-8

import contextlib
import gzip
import urllib2
import json

from datetime import datetime, timedelta

from StringIO import StringIO

import pymorphy2

from mapping import categories, stop_words, when_nearest, when_week
from maching import damerau_levenshtein_distance

import settings


morph = pymorphy2.MorphAnalyzer()


def parser(text):
    cmds = {'place': None, 'what': None, 'when': None}

    splitted = [morph.parse(w.decode('utf-8'))[0].normal_form
                for w in text.split(' ') if text]

    sw_decode = [w.decode('utf-8') for w in stop_words]
    splitted = [w for w in splitted if w not in sw_decode]

    film_names, places = get_films()

    if splitted:
        f_names, splitted = parse_film(splitted, film_names.keys())
        cmds['what'] = [film_names[f] for f in f_names] if f_names else None

    if splitted:
        candidate = determine_place(splitted, places.keys())
        cmds['place'] = [places[p] for p in candidate]

    if splitted:
        cmds['when'] = detect_time(text)

    return cmds


def detect_time(text):
    # TODO: write some lewinstein distance here
    n = datetime.utcnow()
    for k, ws in when_nearest.iteritems():
        for w in ws:
            if text.find(w) > -1:
                return n + timedelta(days=k)

    for k, ws in when_week.iteritems():
        for w in ws:
            if text.find(w):
                week_day = n.isoweekday()
                if week_day > k:
                    return n + timedelta(days=(7 - week_day + 1 + k))


def parse_film(spltd, film_names):

    splitted = [w for w in spltd if len(w) > 2]
    candidate = {i: 0 for i, f_name in enumerate(film_names)}

    for i, f_name in enumerate(film_names):
        f_name_list = [morph.parse(f.lower())[0].normal_form
                       for f in f_name.split()]
        #
        count = 0
        for f_w in f_name_list:
            for s_w in splitted:
                m = min(len(s_w), len(f_w))
                if damerau_levenshtein_distance(f_w, s_w) < (1 + 0.25 * m):
                    count += 1
                    break

        if count >= 0.5 * len(f_name_list):
            candidate[i] += 1

    return ([film_names[k] for k, v in candidate.iteritems() if v > 0],
            splitted)


def determine_place(spltd, places):
    candidate = set()
    for w in spltd:
        for place_name in places:
            ps = place_name.lower().split(' ')
            for p in ps:
                # print p, w
                if (len(w) > 2 and len(p) > 2 and
                        damerau_levenshtein_distance(p, w) < 3):
                    candidate.add(place_name)
                    break
    return candidate


def parse_info(spltd):
    return None


def get_films():
    url_movies = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url_movies)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    film_names = {}
    for film in data:
        film_names[film['title']] = film

    url_cinema = settings.URL_CINEMAS.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url_cinema)) as jf:
        data_places = json.loads(jf.read())

    places = {}
    for cinema in data_places:
        places[cinema['shortTitle']] = cinema

    return film_names, places

# request = 'хочу купить билет в кино на механик на новокузнецкой'
# from pprint import pprint
# pprint(parser(request))
