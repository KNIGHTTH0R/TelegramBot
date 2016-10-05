# coding: utf-8

from datetime import datetime

from google.appengine.ext import ndb, deferred
from google.appengine.api import search

from settings import MORPH
from data import get_data, get_schedule
from processing.mapping import stop_words

from cinema import Cinema
from film import Film, set_film_model

import settings


class ModelSearch(object):

    @staticmethod
    def create_cinema_documents():
        for o in Cinema.query().iter():
            ModelSearch.add_document(
                ModelSearch.create_cinema_document(o.key.urlsafe(), o),
                index_name='cinemas'
            )

    @staticmethod
    def _p(text):
        if isinstance(text, unicode):
            text = text.lower().encode('utf-8')
        return ' '.join([MORPH.parse(w.decode('utf-8'))[0].normal_form
                         for w in text.split(' ')])

    @staticmethod
    def create_film_document(doc_id, film):
        """
        :param doc_id: reference to model in ndb
        :param film: film object
        :return: return search document from film object
        """

        return search.Document(
            doc_id=doc_id,

            fields=[
                search.TextField(
                    name='originalTitle',
                    value=(ModelSearch._p(film.originalTitle)
                           if film.originalTitle else 'origin_title')
                ),

                search.TextField(
                    name='title',
                    value=(ModelSearch._p(film.title)
                           if film.title else 'russian_title')
                ),
            ]
        )

    @staticmethod
    def create_cinema_document(doc_id, cinema):
        """
        if no stations use station called 'typical'
        :param doc_id: link to model in ndb
        :param cinema: obj from cinema model
        :return: document to index
        """

        if cinema.subway_stations and len(cinema.subway_stations) > 0:
            metro_s = ' '.join([ModelSearch._p(metro_station.name)
                                for metro_station in cinema.subway_stations])
        else:
            metro_s = 'typical'

        return search.Document(
            doc_id=doc_id,

            fields=[
                search.TextField(name='shortTitle',
                                 value=ModelSearch._p(cinema.shortTitle)),

                search.TextField(name='address',
                                 value=ModelSearch._p(cinema.address)),

                search.TextField(
                    name='metro',
                    value=metro_s
                )
            ]
        )

    @staticmethod
    def delete_documents(index_name):
        """
        index.get_range by returns up to 100 documents at a time, so we must
        loop until we've deleted all items.
        delete all documents from index
        :param index_name: index with docs to delete
        :return:
        """

        index = search.Index(index_name)

        while True:
            # Use ids_only to get the list of document IDs in the index without
            # the overhead of getting the entire document.
            document_ids = [
                document.doc_id for document in index.get_range(ids_only=True)
            ]

            # If no IDs were returned, we've deleted everything.
            if not document_ids:
                break

            # Delete the documents for the given IDs
            index.delete(document_ids)

    @staticmethod
    def add_document(document, index_name='cinemas'):
        index = search.Index(index_name)
        index.put(document)

    @staticmethod
    def _text_handling(text):

        def uncd(t):
            if isinstance(t, unicode):
                return t.encode('utf-8')
            return t

        s, _pre = text.lower().split(' '), []

        for w in s:
            w = w.decode('utf-8')
            if w not in stop_words and len(w) > 3:
                parse = MORPH.parse(w)[0]
                if 'VERB' not in parse.tag:
                    _pre.append(uncd(parse.normal_form))

        return _pre

    @staticmethod
    def query_cinema(text, need_pre=True, limit=settings.CINEMA_TO_SHOW):

        index = search.Index('cinemas')

        if need_pre:
            _pre = ModelSearch._text_handling(text)
        else:
            if isinstance(text, list):
                _pre = text
            else:
                _pre = text.split(' ')

        if not _pre:
            return None

        _text = '~{}'.format(' OR ~'.join(_pre))
        query_s = 'metro: ({}) OR address: ({}) OR shortTitle: ({})'.format(
            _text, _text, _text
        )

        query_options = search.QueryOptions(limit=limit)
        query = search.Query(query_string=query_s, options=query_options)

        try:
            results = index.search(query)
            r = filter(lambda x: x, [ndb.Key(urlsafe=scored_d.doc_id).get()
                                     for scored_d in results])
            return r if r else None
        except search.Error:
            return None

    @staticmethod
    def query_film(text, need_pre=True, limit=settings.FILMS_TO_DISPLAY):

        index = search.Index('films')

        _pre = None

        if need_pre:
            _pre = ModelSearch._text_handling(text)
        else:
            if isinstance(text, (str, unicode)):
                _pre = text.split(' ')
            elif isinstance(text, list):
                _pre = text

        if not _pre:
            return None

        _text = '~{}'.format(' OR ~'.join(_pre))
        _text = '({})'.format(_text) if len(_pre) > 1 else _text
        query_s = 'title: {}'.format(_text)

        local_limit = (settings.FILMS_TO_DISPLAY
                       if limit < settings.FILMS_TO_DISPLAY else limit)

        query_options = search.QueryOptions(limit=local_limit)

        try:
            query = search.Query(query_string=query_s, options=query_options)
        except search.QueryError:
            return None

        except search.Error:
            return None

        except Exception:
            return None

        try:
            results = index.search(query)
            if results:

                r = filter(lambda x: x, [ndb.Key(urlsafe=scored_d.doc_id).get()
                                         for scored_d in results])
                if r:
                    r = sorted(
                        r, key=lambda k: (k.premiereDateRussia
                                          if k.premiereDateRussia
                                          else datetime.now())
                    )

                    return r[:limit] if len(r) > limit else r
                return None

            else:
                return None

        except search.Error:
            return None


def create_film_documents():
    for o in Film.query().iter():
        ModelSearch.add_document(
            ModelSearch.create_film_document(o.key.urlsafe(), o),
            index_name='films'
        )


def async_update_film_table(films=None):
    deferred.defer(update_film_table, films)


def update_film_table(films=None, index_name='films'):

    if not films:
        films, places = get_data('film')

    for k, f in films.iteritems():

        o = Cinema.get_by_id(f.get('id'))

        if not o:
            film_id = f.get('id')

            schedules = get_schedule(film_id)
            set_film_model(f, schedules)

            o = Cinema.get_by_id(film_id)

            ModelSearch.add_document(
                ModelSearch.create_film_document(
                    doc_id=o.key.urlsafe(),
                    film=o
                ), index_name=index_name
            )
