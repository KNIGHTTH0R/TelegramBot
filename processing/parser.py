# coding: utf-8

import re

from datetime import datetime, timedelta

from mapping import stop_words, when_nearest, when_week, when_month
from maching import damerau_levenshtein_distance
from model.search import ModelSearch
from model.film import Genre
from parse_data import Data

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

    def parser_special(self):
        """
        tasks are already asynchronous
        :return:
        """

        self.__parse_genres()
        self.__parse_actor_producer()

    def __parse_genres(self):
        genres = Genre.query().fetch()

        for t in self.splitted:
            for g in genres:
                if damerau_levenshtein_distance(de_uncd(g.name), t) < 3:
                    for g in g.films:

                        if not self.data.genre:
                            self.data.genre = [g]
                        else:
                            self.data.genre.append(g)

                        if len(self.data.genre) >= settings.CINEMA_TO_SHOW:
                            return
                    return

    def __parse_actor_producer(self):
        pass

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
