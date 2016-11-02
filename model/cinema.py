# coding: utf-8

from google.appengine.ext import ndb

from distance import distance
from model.base import set_model
from base import _t


class SubwayStation(ndb.Model):
    name = ndb.TextProperty()
    id = ndb.IntegerProperty()
    subway_station_d = ndb.IntegerProperty()


class Location(ndb.Model):
    longitude = ndb.FloatProperty()
    latitude = ndb.FloatProperty()


class Phone(ndb.Model):
    number = ndb.TextProperty()
    description = ndb.TextProperty()


class Cinema(ndb.Model):
    shortTitle = ndb.TextProperty()
    website = ndb.TextProperty()
    network = ndb.IntegerProperty()
    distance = ndb.IntegerProperty()
    mall = ndb.TextProperty()
    photo = ndb.StringProperty(repeated=True)
    isSale = ndb.BooleanProperty()
    city = ndb.IntegerProperty()  # integer of city from table
    address = ndb.TextProperty()
    kinohod_id = ndb.TextProperty()
    location = ndb.StructuredProperty(Location, repeated=False)
    phones = ndb.StructuredProperty(Phone, repeated=True)
    description = ndb.TextProperty()
    goodies = ndb.StringProperty(repeated=True)
    subway_stations = ndb.StructuredProperty(SubwayStation, repeated=True)
    title = ndb.TextProperty()

    @classmethod
    def query_nearest(cls, curr):
        return Cinema.query().order(
            -distance(curr.latitude, curr.longitude,
                      Cinema.location.latitude, Cinema.location.longitude)
        )


def set_cinema_model(p):

    location = p.get('location')
    phones = p.get('phones')
    subway_stations = p.get('subway_stations')

    set_model(
        cls=Cinema,

        # primary key is id that cannot be None
        pk=p['id'],

        shortTitle=p.get('shortTitle'),
        website=p.get('website'),
        network=_t(p, 'network', int),
        distance=_t(p, 'distance', int),
        mall=p.get('mall'),

        photo=([hash_photo for hash_photo in p.get('photo')]
               if p.get('photo') else None),

        isSale=_t(p, 'isSale', bool),
        city=_t(p, 'city', int),
        address=p.get('address'),
        kinohod_id=p.get('id'),

        location=(Location(
            longitude=location.get('longitude'),
            latitude=location.get('latitude')
        ) if location else []),

        phones=([
            Phone(
                number=phone.get('number'),
                description=phone.get('description')
            ) for phone in phones] if phones else []),

        description=p.get('description'),

        goodies=([g for g in p.get('goodies')]
                 if p.get('goodies') else None),

        subway_stations=(
            [SubwayStation(
                name=s.get('name'),
                id=s.get('id'),
                subway_station_d=s.get('subway_station_distance')
            ) for s in subway_stations] if subway_stations else []
        ),

        title=p.get('title')
    )
