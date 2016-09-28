# coding: utf-8

import requests
import json

from google.appengine.ext import deferred

import settings


TRACK_URL = 'https://api.botan.io/track'
SHORTENER_URL = 'https://api.botan.io/s/'


def _track(token, uid, message, name='Message'):
    try:
        r = requests.post(
            TRACK_URL,
            params={'token': token, 'uid': uid, 'name': name},
            data=json.dumps(message),
            headers={'Content-type': 'application/json'},
        )
        return r.json()
    except requests.exceptions.Timeout:
        # set up for a retry, or continue in a retry loop
        return False
    except (requests.exceptions.RequestException, ValueError) as e:
        # catastrophic error
        print(e)
        return False


def track(tuid, message, name='message'):
    deferred.defer(_track, settings.BOTAN_TOKEN, tuid, message, name)


def wrap_track(fn):
    def wrapped(*args, **kwargs):
        import logging
        logging.debug(args)
        track(
            tuid=kwargs['tuid'] if 'tuid' in kwargs else 0,
            message=kwargs['text'] if 'text' in kwargs else '{}'.format(
                fn.__name__
            ), name='{}'.format(fn.__name__))
    return wrapped


def shorten_url(url, botan_token, user_id):
    """
    Shorten URL for specified user of a bot
    """
    try:
        return requests.get(SHORTENER_URL, params={
            'token': botan_token,
            'url': url,
            'user_ids': str(user_id),
        }).text
    except:
        return

