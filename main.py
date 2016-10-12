#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json

import webapp2

from google.appengine.ext import deferred

from views import CommandReceiveView
from model.search import ModelSearch, create_film_documents
from data import get_data, get_schedule
from processing.maching import damerau_levenshtein_distance
from model.cinema import Cinema, set_cinema_model
from model.film import Film, Genre, set_film_model

import settings


def set_cinema_models():
    films, places = get_data('cinema')
    for k, p in places.iteritems():
        set_cinema_model(p)


def set_film_models():
    films, places = get_data('film')
    for k, f in films.iteritems():
        schedules = get_schedule(f.get('id'))
        set_film_model(f, schedules)


def update_film_table(index_name='films'):
    films, places = get_data('film')

    for k, f in films.iteritems():

        o = Film.get_by_id(f.get('id'))

        if not o:
            film_id = f.get('id')

            schedules = get_schedule(film_id)
            set_film_model(f, schedules)

            o = Film.get_by_id(film_id)

            ModelSearch.add_document(
                ModelSearch.create_film_document(
                    doc_id=o.key.urlsafe(),
                    film=o
                ), index_name=index_name
            )


class UpdateBFilmView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        deferred.defer(set_film_models, )


class UpdateBCinemaView(webapp2.RedirectHandler):

    def get(self, *args, **kwargs):
        deferred.defer(set_cinema_models, )


class CountCinemasView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        films, places = get_data('cinema')

        self.response.write(
            'places: {} and cinemas: {}'.format(
                str(len(places.values())),
                str(len(Cinema.query().fetch())),
            )
        )


class CountFilmsView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        films, places = get_data('film')

        self.response.write(
            'films: {} and db films: {}'.format(
                str(len(films.values())),
                str(len(Film.query().fetch())),
            )
        )


class CinemaSearchIndexView(webapp2.RedirectHandler):

    def get(self, *args, **kwargs):
        ModelSearch.create_cinema_documents()


class FilmSearchIndexView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        deferred.defer(create_film_documents, )


class CinemaSearchIndexTestView(webapp2.RedirectHandler):

    def get(self, *args, **kwargs):
        text = 'хочу на арбат'

        self.response.write(
            json.dumps(
                [m.to_dict() for m in ModelSearch.query_cinema(text)]
            )
        )


class DeleteAllSearchFilmDocumentsView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        ModelSearch.delete_documents(index_name='films')


class DeleteAllSearchCinemaDocumentsView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        ModelSearch.delete_documents(index_name='cinemas')


class FilmSearchIndexTestView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):

        a = []
        for text in ['russian_title',
                     'Рожденные на воле', 'жених хочу посмотреть',
                     'Зачинщики', 'хочу на аист']:

            r = ModelSearch.query_film(text)
            a.append(
                ([m.title for m in r] if r else [])
            )

        self.response.write(
            json.dumps(
                a  # ModelSearch.query_film(text)
            )
        )


class FilmGenreTestView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):

        text = 'комедия'.decode('utf-8')

        a = []

        for g in Genre.query().order().fetch():
            if damerau_levenshtein_distance(g.name, text) < 3:
                for k in g.films:
                    a.append(k.title)
                break

        sorted(a, key=lambda f: (-f['premiereDateWorld']
                                 if 'premiereDateWorld' in f else 0))

        self.response.write(
            json.dumps(
                a  # ModelSearch.query_film(text)
            )
        )


class CronFilmTableUpdateView(webapp2.RedirectHandler):
    def get(self, *args, **kwargs):
        deferred.defer(update_film_table, )


app = webapp2.WSGIApplication([
    # ('/update_film', UpdateBFilmView),
    # ('/update_cinema', UpdateBCinemaView),
    # ('/delete_all_cinema_docs', DeleteAllSearchCinemaDocumentsView),
    # ('/delete_all_film_docs', DeleteAllSearchFilmDocumentsView),
    # ('/search_cinema', CinemaSearchIndexView),
    # ('/search_film', FilmSearchIndexView),
    # ('/count_cinemas', CountCinemasView),
    # ('/test_genre_film', FilmGenreTestView),
    # ('/count_films', CountFilmsView),
    # ('/test_cinema', CinemaSearchIndexTestView),
    # ('/test_film', FilmSearchIndexTestView),
    ('/film_update', CronFilmTableUpdateView),
    # should be exchanged to /botAPI_KINOHOD like unique link
    ('/bot{}'.format(settings.KINOHOD_API_KEY), CommandReceiveView),
], debug=True)
