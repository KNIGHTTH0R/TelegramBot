# coding: utf-8

import contextlib
import gzip
import urllib2
import json
import re
import itertools

from datetime import datetime, timedelta
from StringIO import StringIO

import pymorphy2

from mapping import stop_words, when_nearest, when_week, when_month
from maching import damerau_levenshtein_distance

import settings


MORPH = pymorphy2.MorphAnalyzer()


class Data(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Parser(object):
    def __init__(self, request, state):

        self.data = Data(place=None, what=None, when=None,
                         genre=None, actors=None)

        splitted = [MORPH.parse(w.decode('utf-8'))[0].normal_form
                    for w in request.split(' ') if request]

        sw_decode = [w.decode('utf-8') for w in stop_words]
        self.splitted = [w for w in splitted if w not in sw_decode]

        self.state = state

        self.text = request
        self.films, self.places = get_data(self.state)

    def parse(self):

        scenario = {
            'film': [(self.__parse_film, ), (self.parser_special, )],
            'cinema': [(self.__determine_place, )],
            'time': [(self._detect_time, )],
            'base': [(self.__parse_film, ), (self.__determine_place, ),
                     (self._detect_time, ), (self.parser_special, )]
        }

        _consequences = []
        for act in scenario[self.state]:
            if self.splitted:
                _consequences.append(act[0](*act[1:]))
        return filter(lambda x: x, _consequences)

    def parser_special(self):
        self._parse_special()

    def _parse_special(self):
        try:
            from google.appengine.ext import deferred
            deferred.defer(self.__parse_genres())
        except:
            self.__parse_genres()

        if not self.data.genre and self.splitted:
            try:
                from google.appengine.ext import deferred
                deferred.defer(self.__parse_actor_producer())
            except:
                self.__parse_actor_producer()

    def __parse_genres(self):
        genre_name = None
        for k, v in self.films.iteritems():
            if 'genres' in v and isinstance(v['genres'], list):
                genre = v['genres'][0]['name'].lower()

            if not genre_name:
                for s_w in self.splitted:
                    if damerau_levenshtein_distance(genre, s_w) < 2:
                        self.data.genre = [v]
                        genre_name = genre
            else:
                if (genre_name == genre and self.data.genre and
                        isinstance(self.data.genre, list)):
                    self.data.genre.append(v)

        # else mean that it is a premier of film
        # TODO: need faster method
        if self.data.genre:
            if len(self.data.genre) > settings.FILMS_DISPLAY_INFO:
                self.data.genre = sorted(
                    self.data.genre,
                    key=lambda key: self.key_func(key)
                )[-settings.FILMS_DISPLAY_INFO:]

    @staticmethod
    def key_func(key):
        return (datetime.strptime(key['premiereDateRussia'], '%Y-%m-%d')
                if key['premiereDateRussia'] else datetime.now())

    def __parse_actor_producer(self):
        base_actors_prods = None
        for k, v in self.films.iteritems():
            if 'actors' in v and 'producers' in v:
                acts = v['actors'] if isinstance(v['actors'], list) else []
                ps = v['producers'] if isinstance(v['producers'], list) else []
                actors_prods = [a['name'] for a in itertools.chain(acts, ps)]

                if not base_actors_prods:
                    for f_w in actors_prods:
                        for s_w in self.splitted:
                            w = min(len(s_w), len(f_w)) * 0.25 + 1
                            if damerau_levenshtein_distance(f_w, s_w) < w:
                                if base_actors_prods:
                                    base_actors_prods = [f_w]
                                else:
                                    base_actors_prods.append(f_w)

                    if base_actors_prods:
                        self.data.actors = [v]
                else:
                    for f_w in actors_prods:
                        if f_w in base_actors_prods:
                            self.data.actors.append(v)

        if self.data.actors:
            if len(self.data.actors) > settings.FILMS_DISPLAY_INFO:
                self.data.actors = sorted(
                    self.data.actors,
                    key=lambda key: self.key_func(key)
                )[-settings.FILMS_DISPLAY_INFO:]

    def __parse_film(self):
        names = self.films.keys()
        splitted = [w for w in self.splitted if len(w) > 2]
        c = {i: 0 for i, f_name in enumerate(names)}

        for i, f_name in enumerate(names):
            f_name_list = [MORPH.parse(f.lower())[0].normal_form
                           for f in f_name.split()]
            count = 0
            for f_w in f_name_list:
                for s_w in splitted:
                    w = min(len(s_w), len(f_w)) * 0.25 + 1
                    if damerau_levenshtein_distance(f_w, s_w) < w:
                        count += 1
                        break

            if count >= 0.5 * len(f_name_list):
                c[i] += 1

        if len(c):
            self.data.what = [self.films[names[k]]
                              for k, v in c.iteritems() if v > 0]
        self.splitted = splitted

    def __determine_place(self):
        def process_part(place_name):
            if not place_name:
                return False

            ps = place_name.lower().split(' ')
            for p in ps:
                if (len(w) > 2 and len(p) > 2 and
                        damerau_levenshtein_distance(p, w) < 3):
                    return True
            return False

        names = self.places.keys()

        c = set()
        for w in self.splitted:
            for place_name in names:
                for e in place_name:
                    flag = process_part(e)
                    if flag:
                        c.add(place_name)
                        break
        if len(c):
            self.data.place = [self.places[p] for p in c]

    def _detect_time(self):
        self.data.when = self.detect_time(self.text)

    @staticmethod
    def detect_time(text):
        # TODO: write some lewinstein distance here

        def word_root(word):
            m = MORPH.parse(when_month[word].decode('utf-8'))[0].normal_form
            if m[-1] == u'ь':
                return m[:-1]
            return m

        text = text.decode('utf-8').lower()
        n = datetime.utcnow()

        digit_date = re.search('\d{1,2}[\.|:]\d{1,2}', text)
        if digit_date:
            d, m = map(int, re.split('[:\.]', digit_date.group(0)))
            return datetime.utcnow().replace(month=m, day=d)

        text_date = re.search(
            '\d{1,2} ' + word_root(n.strftime(format='%B').lower()),
            text
        )

        if text_date:
            return datetime.utcnow().replace(
                day=int(text_date.group(0).split(' ')[0])
            )

        text = text.encode('utf-8')
        for k, ws in when_nearest.iteritems():
            for w in ws:
                if text.find(w) > -1:
                    return n + timedelta(days=k)

        for k, ws in when_week.iteritems():
            for w in ws:
                if text.find(w) > -1:
                    week_day = n.isoweekday()
                    if week_day > k:
                        return n + timedelta(days=(7 - week_day + 1 + k))
                    else:
                        return n + timedelta(days=(k - week_day + 1))
        return n


def get_data(state):
    out_data = {'film': None, 'place': None}

    def get_film_data():
        url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
            data = json.loads(stream.read())
        out_data['film'] = {film['title']: film for film in data}

    def get_place_data():
        url_cinema = settings.URL_CINEMAS.format(settings.KINOHOD_API_KEY)
        with contextlib.closing(urllib2.urlopen(url_cinema)) as jf:
            data_places = json.loads(jf.read())
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
