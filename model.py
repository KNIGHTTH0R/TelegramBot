# coding: utf-8

import json

from google.appengine.ext import ndb


class UserProfile(ndb.Model):
    location = ndb.JsonProperty()


def set_user(chat_id, location):
    u = UserProfile.get_or_insert(str(chat_id))
    u.location = json.dumps(location)
    u.put()


def get_user(chat_id):
    return UserProfile.get_by_id(str(chat_id))


class ReturnTicket(ndb.Model):
    number = ndb.IntegerProperty()
    email = ndb.StringProperty()


def get_return_ticket(chat_id):
    return ReturnTicket.get_by_id(str(chat_id))


def set_return_ticket(chat_id, number=None, email=None):
    t = ReturnTicket.get_or_insert(str(chat_id))

    if number:
        t.number = number

    if email:
        t.email = email

    t.put()


class PrevCmd(ndb.Model):
    cmd = ndb.TextProperty()


def set_prev_cmd(chat_id, text):
    c = PrevCmd.get_or_insert(str(chat_id))
    c.cmd = text
    c.put()


def get_prev_cmd(chat_id):
    return PrevCmd.get_by_id(str(chat_id))
