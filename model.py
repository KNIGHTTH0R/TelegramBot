# coding: utf-8

import json

from google.appengine.ext import ndb


def set_o(o, kwargs):
    for k, v in kwargs.iteritems():
        if hasattr(o, k):
            if isinstance(v, dict):
                v = json.dumps(v)
            setattr(o, k, v)
    return o


def set_model(cls, pk, **kwargs):
    o = cls.get_or_insert(str(pk))
    o = set_o(o, kwargs)
    o.put()
    return o


def get_model(cls, pk):
    o = cls.get_by_id(str(pk))
    return o


class UserProfile(ndb.Model):
    location = ndb.JsonProperty()
    cmd = ndb.TextProperty()
    state = ndb.TextProperty(default='base')


class ReturnTicket(ndb.Model):
    number = ndb.IntegerProperty()
    email = ndb.StringProperty()
