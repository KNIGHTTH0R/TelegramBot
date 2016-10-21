# coding: utf-8

import re
import itertools

from datetime import datetime, timedelta

from mapping import (stop_words, when_nearest, when_week,
                     when_month, genre_mapping)

from maching import damerau_levenshtein_distance
from model.search import ModelSearch
from model.film import Genre, Film, set_film_model, Actor, Producer, Director
from parse_data import Data
from data import get_genres, get_schedule

import settings

from settings import MORPH, de_uncd


class Parser(object):
    def __init__(self, request, state):

        self.data = Data(place=None, what=None, when=None,
                         genre=None, actors=None)

        self.splitted = []

        if request:
            for w in request.split(' '):
                w = w.decode('utf-8')
                if w not in stop_words and len(w) > 2:
                    parse = MORPH.parse(w)[0]
                    if 'VERB' not in parse.tag:
                        self.splitted.append(de_uncd(parse.normal_form))

            self.splitted = self.sub_splitted(self.splitted)

        self.state = state
        self.text = request

        self.__ids_inside = []

    def parse(self):

        scenario = {
            'film': [(self.__parse_film, ), ],  # (self.parser_special, )
            'cinema': [(self.determine_place, settings.CINEMAS_TO_DISPLAY)],

            'time': [(self._detect_time, )],
            'base': [(self.__parse_film, ),
                     (self.determine_place, settings.CINEMA_TO_SHOW),
                     (self._detect_time, ), ]  # (self.parser_special, )
        }

        _consequences = []
        for act in scenario[self.state]:
            if self.splitted:
                _consequences.append(act[0](*act[1:]))
        return filter(lambda x: x, _consequences)

    def parser_special(self, is_film_object=True):
        """
        :type is_film_object: regularize output
        if True will return Film object else json with films
        :return: None, put all films in data.genre
        """

        # self.__parse_genres()
        self.__parse_genres_api(is_film_object)
        # self.__parse_actor_producer()

    def __parse_genres_api(self, is_film_object):
        genres = Genre.query().fetch()

        for t in self.splitted:
            for g in genres:
                g_name = MORPH.parse(g.name)[0].normal_form

                g_names = [g_name]
                if g.name in genre_mapping:
                    g_names = itertools.chain(g_names, genre_mapping[g_name])

                is_flag = False
                for name in g_names:
                    is_flag = self.__process_genre(
                        name, t, g, is_film_object
                    )

                    if is_flag:
                        break

                if is_flag:
                    break

    def __process_genre(self, name, t, g, is_film_object):
        if damerau_levenshtein_distance(de_uncd(name), t) < 2:
            if not self.data.genre:
                self.data.genre = []

            if is_film_object:
                films = get_genres(g.kinohod_id)

                for f in films:
                    film_id = f.get('id')

                    if not film_id or film_id in self.__ids_inside:
                        continue

                    o = Film.get_by_id(film_id)
                    if not o:
                        schedules = get_schedule(film_id)
                        o = set_film_model(f, schedules)
                    self.__ids_inside.append(film_id)
                    self.data.genre.append(o)
            else:
                self.data.genre += get_genres(g.kinohod_id)

            return True
        return False

    def __parse_genres(self):
        genres = Genre.query().fetch()

        for t in self.splitted:
            for g in genres:
                g_name = MORPH.parse(g.name)[0].normal_form
                if damerau_levenshtein_distance(de_uncd(g_name), t) < 3:

                    for f in g.films:

                        if not self.data.genre:
                            self.data.genre = [f]
                        else:
                            self.data.genre.append(f)

                        # comment line below if not all to display
                        if len(self.data.genre) >= settings.CINEMA_TO_SHOW:
                            return
                    return

    def __parse_actor_producer(self):
        actors = Actor.query().fetch()
        # producers = Producer.query().fetch()
        # directors = Director.query().fetch()

        for t in self.splitted:
            for o in itertools.chain(actors):
                p_name = MORPH.parse(o.name.split(' ')[-1])[0].normal_form
                p_name, t = p_name.lower(), t.lower()
                if damerau_levenshtein_distance(de_uncd(p_name), t) < 3:
                    for f in o.films:
                        if not self.data.actors:
                            self.data.actors = [f]
                        else:
                            self.data.actors.append(f)
                        if len(self.data.actors) >= settings.CINEMA_TO_SHOW:
                            return
                    # return

    def __parse_film(self, limit=settings.FILMS_TO_DISPLAY):
        self.data.what = ModelSearch.query_film(
            self.splitted,
            need_pre=False,
            limit=limit
        )

    def determine_place(self, limit):
        """
        method that allows different ways of place determination
        first is by api and second by cinemas from gae db which copied from api
        :return: self.data.place now not empty
        """
        self.__determine_place(limit)

    def __determine_place(self, limit=settings.CINEMA_TO_SHOW):
        self.data.place = ModelSearch.query_cinema(
            self.splitted,
            need_pre=False,
            limit=limit
        )

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

        def get_text_date(search_text, d):
            text_date = re.search(
                '\d{1,2} ' + word_root(d.strftime(format='%B').lower()),
                search_text
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

    @staticmethod
    def sub_splitted(splitted):
        return [Parser._sub_string(w) for w in splitted]

    @staticmethod
    def _sub_string(s):
        return re.sub(
            '\d+|\/|\.|,|\?|\}|\{|\[|\]|\-|;|`|~|:|\*|&|$|%|#|@|!|<|>', '', s
        )
