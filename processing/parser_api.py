# coding: utf-8

import re
import itertools
from datetime import datetime, timedelta

from maching import damerau_levenshtein_distance
from mapping import stop_words, when_nearest, when_week, when_month
from data import get_data
from parse_data import Data
from settings import MORPH, de_uncd

import settings


class ParserAPI(object):
    def __init__(self, request, state):

        self.data = Data(place=None, what=None, when=None,
                         genre=None, actors=None)

        self.splitted = []

        if request:
            for w in request.split(' '):
                w = w.decode('utf-8')
                if w not in stop_words and len(w) > 3:
                    parse = MORPH.parse(w)[0]
                    if 'VERB' not in parse.tag:
                        self.splitted.append(de_uncd(parse.normal_form))

        self.state = state

        self.text = request
        self.films, self.places = get_data(self.state)

    def __uncd(self, t):
        if isinstance(t, unicode):
            return t.encode('utf-8')
        return t

    def parse(self):

        scenario = {
            'film': [(self.__parse_film, ), ],  # (self.parser_special, )
            'cinema': [(self.determine_place, settings.CINEMA_TO_SHOW)],
            'time': [(self._detect_time, )],
            'base': [(self.__parse_film, 1), (self.determine_place, 1),
                     (self._detect_time, ), ]  # (self.parser_special, )
        }

        _consequences = []
        for act in scenario[self.state]:
            if self.splitted:
                _consequences.append(act[0](*act[1:]))
        return filter(lambda x: x, _consequences)

    def parser_special(self):
        """
        tasks are already asynchronous
        :return:
        """
        self._parse_special()

    def _parse_special(self):
        # try:
        #     from google.appengine.ext import deferred
        #     deferred.defer(self.__parse_genres())
        # except:
        self.__parse_genres()

        if not self.data.genre and self.splitted:
            # try:
            #     from google.appengine.ext import deferred
            #     deferred.defer(self.__parse_actor_producer())
            # except:
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
                    key=lambda key: self.__key_func(key)
                )[-settings.FILMS_DISPLAY_INFO:]

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
                    key=lambda key: self.__key_func(key)
                )[-settings.FILMS_DISPLAY_INFO:]

    def __key_func(self, key):
        return (datetime.strptime(key['premiereDateRussia'], '%Y-%m-%d')
                if key['premiereDateRussia'] else datetime.now())

    def __parse_film(self, limit=settings.FILMS_TO_DISPLAY):
        self.__parse_film_api()

    def __parse_film_api(self):
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

    def determine_place(self, limit):
        """
        method that allows different ways of place determination
        first is by api and second by cinemas from gae db which copied from api
        :return: self.data.place now not empty
        """

        self.__determine_place_api()

    def __determine_place_api(self):
        def process_part(place_name):
            if not place_name:
                return False

            ps = place_name.lower().split(' ')
            for p in ps:
                if (len(w) > 2 and len(p) > 2 and
                        damerau_levenshtein_distance(p, w) < 3):
                    return True
            return False

        try:
            names = self.places.keys()
        except UnboundLocalError:
            self.data.place = None
        else:
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
        # TODO: write some lewinstein distance here, but not for reg exp

        def word_root(word):
            m = MORPH.parse(when_month[word].decode('utf-8'))[0].normal_form
            if m[-1] == u'ь':
                return m[:-1]
            return m

        def get_text_date(text, d):
            text_date = re.search(
                '\d{1,2} ' + word_root(d.strftime(format='%B').lower()),
                text
            )

            if text_date:
                return datetime.utcnow().replace(
                    day=int(text_date.group(0).split(' ')[0])
                )

        text = text.decode('utf-8').lower()
        n = datetime.utcnow()

        digit_date = re.search('\d{1,2}[\.|:]\d{1,2}', text)
        if digit_date:
            d, m = map(int, re.split('[:\.]', digit_date.group(0)))
            return datetime.utcnow().replace(month=m, day=d)

        _current_month_r = get_text_date(text, n)
        if _current_month_r:
            return _current_month_r

        _next_month_r = get_text_date(text,
                                      datetime.utcnow() + timedelta(days=10))
        if _next_month_r:
            return _next_month_r

        text = text.encode('utf-8')
        for ws, k in when_nearest.iteritems():
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
