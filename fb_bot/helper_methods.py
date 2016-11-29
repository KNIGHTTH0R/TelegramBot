# coding: utf-8
import contextlib
import json
import urllib2

import settings
from model.base import UserProfile


def get_data(url):
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        return json.loads(jf.read())


def get_by_recipient_id(recipient_id):
    if not recipient_id:
        return None
    u_info = (UserProfile.query(UserProfile.facebook_id == recipient_id).get())
    if not u_info:
        u_info = UserProfile()
        u_info.facebook_id = recipient_id
    return u_info


def get_movie_trailer_link(trailer_hash):
    ab, cd = trailer_hash[0:2], trailer_hash[2:4]
    url = '{}{}/{}/{}'.format(settings.URL_BASE_O, ab, cd, trailer_hash)
    return url


def get_movie_poster(poster_hash):
    if not poster_hash:
        return ''
    ab, cd = poster_hash[0:2], poster_hash[2:4]
    url = '{}{}/{}/{}'.format(settings.URL_BASE_O, ab, cd, poster_hash)
    return url
