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


class PrevCmd(ndb.Model):
    cmd = ndb.TextProperty()
    update_id = ndb.IntegerProperty()


def set_prev_cmd(chat_id, text, update_id):
    c = PrevCmd.get_or_insert(str(chat_id))
    c.cmd = text
    c.update_id = update_id
    c.put()


def get_prev_cmd(chat_id):
    return PrevCmd.get_by_id(str(chat_id))
