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
        if self.key not in film.genres:
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
    ageRestriction = ndb.StringProperty()
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
    _genres = f.get('genres')
    _images = f.get('images')
    actors = f.get('actors')
    _rating = f.get('rating')
    _poster = f.get('poster')
    directors = f.get('directors')
    companies = f.get('companies')
    premiere_date_world = f.get('premiereDateWorld')
    premiere_date_russia = f.get('premiereDateRussia')
    trailers = f.get('trailers')

    trailer_keys = []

    def _process_rbg_name(_list, cls):
        if _list and isinstance(_list, list):
            _prepared = []
            for im in _list:
                if isinstance(im, dict):
                    _prepared.append(cls(rgb=im.get('rgb'),
                                         name=im.get('name')))
                elif isinstance(im, (str, unicode)):
                    _prepared.append(cls(rgb='0c0c0b', name=im))
            return _prepared
        elif _list and isinstance(_list, (str, unicode)):
            if cls == Poster:
                return cls(rgb='0c0c0b', name=_list)
            return [cls(rgb='0c0c0b', name=_list)]
        else:
            return None

    images = _process_rbg_name(_images, cls=Image)
    poster = _process_rbg_name(_poster, cls=Poster)

    if _rating and isinstance(_rating, dict):
        rating = _t(_rating, 'rating', float)
    else:
        rating = _t(f, 'rating', float)

    if premiere_date_russia:
        if 'T' in premiere_date_russia:
            premiere_date_russia = premiere_date_russia.split('T')[0]

        premiereDateRussia = (
            datetime.strptime(premiere_date_russia, '%Y-%m-%d')
            if premiere_date_russia else None
        )
    else:
        _premiere = f.get('firstSeanceStime')
        if _premiere:
            _premiere = _premiere.split('T')[0]
            premiereDateRussia = datetime.strptime(_premiere, '%Y-%m-%d')
        else:
            premiereDateRussia = None

    genres = []
    if _genres:
        for g in _genres:
            if isinstance(g, dict):

                genre_id = g.get('id')
                if genre_id is None:
                    continue

                g = set_model(
                    Genre,
                    pk=genre_id, name=g.get('name'), kinohod_id=genre_id
                )

                genres.append(g.key)
                # genres.append(g.key)

    if trailers and isinstance(trailers, list):
        for trailer in trailers:
            source = trailer.get('source')
            preview = trailer.get('preview')
            videos = trailer.get('videos')

            if not videos:
                videos = [trailer.get('mobile_mp4')]

            o = Trailer(
                source=Source(
                    filename=source.get('filename'),
                    duration=_t(source, 'duration', float),
                    contentType=source.get('contentType')
                ) if source else None,

                videos=[
                    Video(
                        filename=v.get('filename'),
                        duration=_t(v, 'duration', float),
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

    curr_f = set_model(
        cls=Film,

        # it is only kinohod_id
        pk=f['id'],

        originalTitle=f.get('originalTitle'),
        title=f.get('title'),

        posterLandscape=PosterLandscape(
            rgb=poster_landscape.get('rgb'),
            name=poster_landscape.get('name')
        ) if poster_landscape else None,

        ageRestriction=f.get('ageRestriction'),
        annotationFull=f.get('annotationFull'),

        producers=[
            Producer(name=p.get('name'), kinohod_id=p.get('id'))
            for p in producers if isinstance(p, dict)
        ] if producers else None,

        genres=genres,

        weight=_t(f, 'weight', int),
        kinohod_id=_t(f, 'id', int),
        is4dx=_t(f, 'is4dx', bool),

        trailers=trailer_keys if len(trailer_keys) > 0 else None,

        countries=([c for c in f.get('countries')]
                   if f.get('countries') else None),

        images=images,

        countVotes=_t(f, 'countVotes', int),
        productionYear=_t(f, 'productionYear', int),

        premiereDateWorld=datetime.strptime(
            (premiere_date_world.split('T')[0]
             if 'T' in premiere_date_world else premiere_date_world),
            '%Y-%m-%d'
        ) if premiere_date_world else None,

        duration=_t(f, 'duration', int),
        grossRevenueWorld=_t(f, 'grossRevenueWorld', int),
        budget=_t(f, 'budget', int),
        rating=rating,
        annotationShort=f.get('annotationShort'),

        actors=[
            Actor(name=a.get('name'), kinohod_id=a.get('id'))
            for a in actors if isinstance(a, dict)
        ] if actors else None,

        poster=poster,

        imdbId=_t(f, 'imdbId', int),
        isPresale=_t(f, 'isPresale', bool),

        directors=[
            Director(name=d.get('name'), kinohod_id=d.get('id'))
            for d in directors if isinstance(d, dict)
        ] if directors else None,

        isDolbyAtmos=_t(f, 'isDolbyAtmos', bool),

        companies=[
            Company(name=c.get('name'), kinohod_id=c.get('id'))
            for c in companies if isinstance(c, dict)
        ] if companies else None,

        premiereDateRussia=premiereDateRussia,

        countComments=_t(f, 'countComments', int),
        distributorId=_t(f, 'distributorId', int),
        cinemas=cinemas
    )

    return curr_f