# coding: utf-8

from datetime import datetime

from google.appengine.ext import ndb

from cinema import Cinema
from base import set_model, _t


class PosterLandscape(ndb.Model):
    rgb = ndb.TextProperty()
    name = ndb.TextProperty()


class Producer(ndb.Model):
    name = ndb.TextProperty()
    kinohod_id = ndb.IntegerProperty()

    # @property
    # def films(self):
    #     return Film.query().filter(Film.producers == self.key)
    #
    # def add_film(self, film):
    #     film.producers.append(self.key)
    #     film.put()


class Genre(ndb.Model):
    name = ndb.TextProperty()
    kinohod_id = ndb.IntegerProperty()

    @property
    def films(self):
        return Film.query().filter(Film.genres == self.key)

    def add_film(self, film):
        film.genres.append(self.key)
        film.put()


class Source(ndb.Model):
    filename = ndb.TextProperty()
    duration = ndb.FloatProperty()
    contentType = ndb.TextProperty()


class Video(ndb.Model):
    filename = ndb.TextProperty()
    duration = ndb.FloatProperty()
    contentType = ndb.TextProperty()


class Preview(ndb.Model):
    rgb = ndb.TextProperty()
    name = ndb.TextProperty()


class Trailer(ndb.Model):
    source = ndb.StructuredProperty(Source)
    videos = ndb.StructuredProperty(Video, repeated=True)
    preview = ndb.StructuredProperty(Preview)


class Image(ndb.Model):
    rgb = ndb.TextProperty()
    name = ndb.TextProperty()


class Actor(ndb.Model):
    name = ndb.TextProperty()
    kinohod_id = ndb.IntegerProperty()

    # @property
    # def films(self):
    #     return Film.query().filter(Film.actors == self.key)
    #
    # def add_film(self, film):
    #     film.actors.append(self.key)
    #     film.put()


class Poster(ndb.Model):
    rgb = ndb.TextProperty()
    name = ndb.TextProperty()


class Director(ndb.Model):
    name = ndb.TextProperty()
    kinohod_id = ndb.IntegerProperty()


class Company(ndb.Model):
    name = ndb.TextProperty()
    kinohod_id = ndb.IntegerProperty()


class Film(ndb.Model):
    originalTitle = ndb.TextProperty()
    posterLandscape = ndb.StructuredProperty(PosterLandscape, repeated=False)
    annotationFull = ndb.TextProperty()
    producers = ndb.StructuredProperty(Producer, repeated=True)

    genres = ndb.KeyProperty(kind="Genre", repeated=True)

    weight = ndb.IntegerProperty()
    kinohod_id = ndb.IntegerProperty()
    is4dx = ndb.BooleanProperty()

    trailers = ndb.KeyProperty(kind="Trailer", repeated=True)

    countries = ndb.StringProperty(repeated=True)
    images = ndb.StructuredProperty(Image, repeated=True)
    countVotes = ndb.IntegerProperty()
    productionYear = ndb.IntegerProperty()
    title = ndb.TextProperty()
    premiereDateWorld = ndb.DateTimeProperty()  # try to be more careful
    duration = ndb.IntegerProperty()
    grossRevenueWorld = ndb.IntegerProperty()  # often None
    budget = ndb.IntegerProperty()
    rating = ndb.FloatProperty()
    annotationShort = ndb.TextProperty()
    actors = ndb.StructuredProperty(Actor, repeated=True)
    poster = ndb.StructuredProperty(Poster)
    imdbId = ndb.IntegerProperty()
    isPresale = ndb.BooleanProperty()
    directors = ndb.StructuredProperty(Director, repeated=True)
    isDolbyAtmos = ndb.BooleanProperty()
    companies = ndb.StructuredProperty(Company, repeated=True)
    premiereDateRussia = ndb.DateTimeProperty()
    countComments = ndb.IntegerProperty()
    distributorId = ndb.IntegerProperty()
    cinemas = ndb.KeyProperty(kind='Cinema', repeated=True)


def set_film_model(f, schedules):
    poster_landscape = f.get('posterLandscape')
    producers = f.get('producers')
    genres = f.get('genres')
    images = f.get('images')
    actors = f.get('actors')
    poster = f.get('poster')
    directors = f.get('directors')
    companies = f.get('companies')
    premiere_date_world = f.get('premiereDateWorld')
    premiere_date_russia = f.get('premiereDateRussia')
    trailers = f.get('trailers')

    trailer_keys = []
    _upd_genres = []

    if genres:
        genres = []
        for g in genres:
            genres.append(
                set_model(
                    Genre, pk=g.get('id'),
                    name=g.get('name'),
                    kinohod_id=g.get('id')
                ).key
            )

            _upd_genres.append(Genre.get_by_id(g.get('id')))

    if trailers and isinstance(trailers, list):
        for trailer in trailers:
            source = trailer.get('source')
            preview = trailer.get('preview')
            videos = trailer.get('videos')

            o = Trailer(
                source=Source(
                    filename=source.get('filename'),
                    duration=source.get('duration'),
                    contentType=source.get('contentType')
                ) if source else None,

                videos=[
                    Video(
                        filename=v.get('filename'),
                        duration=v.get('duration'),
                        contentType=v.get('contentType')
                    ) for v in videos
                ] if videos else None,

                preview=Preview(
                    rgb=preview.get('rgb'),
                    name=preview.get('name')
                ) if preview else None
            )

            o.put()
            trailer_keys.append(o.key)

    cinemas = None
    if schedules:
        cinemas = []
        for s in schedules:
            c_json = s.get('cinema')
            if c_json:
                c_o = Cinema.get_by_id(str(c_json.get('id')))
                if c_o:
                    cinemas.append(c_o.key)

    set_model(
        cls=Film,

        # it is only kinohod_id
        pk=f['id'],

        originalTitle=f.get('originalTitle'),
        title=f.get('title'),

        posterLandscape=PosterLandscape(
            rgb=poster_landscape.get('rgb'),
            name=poster_landscape.get('name')
        ) if poster_landscape else None,

        annotationFull=f.get('annotationFull'),

        producers=[
            Producer(name=p.get('name'), kinohod_id=p.get('id'))
            for p in producers
        ] if producers else None,

        genres=genres,

        weight=_t(f, 'weight', int),
        kinohod_id=_t(f, 'id', int),
        is4dx=_t(f, 'is4dx', bool),

        trailers=trailer_keys if trailer_keys else None,

        countries=([c for c in f.get('countries')]
                   if f.get('countries') else None),

        images=[
            Image(rgb=i.get('rgb'), name=i.get('name'))
            for i in images
        ] if images else None,

        countVotes=_t(f, 'countVotes', int),
        productionYear=_t(f, 'productionYear', int),

        premiereDateWorld=datetime.strptime(
            premiere_date_world, '%Y-%m-%d'
        ) if premiere_date_world else None,

        duration=_t(f, 'duration', int),
        grossRevenueWorld=_t(f, 'grossRevenueWorld', int),
        budget=_t(f, 'budget', int),
        rating=_t(f, 'rating', float),
        annotationShort=f.get('annotationShort'),

        actors=[
            Actor(name=a.get('name'), kinohod_id=a.get('id'))
            for a in actors
        ] if actors else None,

        poster=Poster(
            rgb=poster.get('rgb'),
            name=poster.get('name')
        ) if poster else None,

        imdbId=_t(f, 'imdbId', int),
        isPresale=_t(f, 'isPresale', bool),

        directors=[
            Director(name=d.get('name'), kinohod_id=d.get('id'))
            for d in directors
        ] if directors else None,

        isDolbyAtmos=_t(f, 'isDolbyAtmos', bool),

        companies=[
            Company(name=c.get('name'), kinohod_id=c.get('id'))
            for c in companies
        ] if companies else None,

        premiereDateRussia=datetime.strptime(
            premiere_date_russia, '%Y-%m-%d'
        ) if premiere_date_russia else None,

        countComments=_t(f, 'countComments', int),
        distributorId=_t(f, 'distributorId', int),
        cinemas=cinemas
    )

    curr_f = Film.get_by_id(f['id'])
    for g in _upd_genres:
        g.add_film(curr_f)
