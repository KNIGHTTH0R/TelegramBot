# coding: utf-8
import json

from google.appengine.api import urlfetch

import settings


def _configure(payload):
    request_endpoint = ('https://graph.facebook.com/v2.6/me/thread_settings?'
                        'access_token={}'.format(settings.PAGE_ACCESS_TOKEN))
    response = urlfetch.fetch(
        url=request_endpoint,
        payload=payload,
        method=urlfetch.POST,
        headers={u'Content-Type': u'application/json'}
    )

    return response.content


def configure():
    greeting = {
        'setting_type': 'greeting',
        'greeting': {
            'text': settings.HELLO_IM_BOT
        }
    }
    greeting = json.dumps(greeting)

    start_button = {
        'setting_type': 'call_to_actions',
        'thread_state': 'new_thread',
        'call_to_actions': [
            {
                'payload': 'start'
            }
        ]
    }
    start_button = json.dumps(start_button)
    menu = {
        'setting_type': 'call_to_actions',
        'thread_state': 'existing_thread',
        'call_to_actions': [
            {
                'type': 'postback',
                'title': 'В прокате',
                'payload': '/running{}'.format(settings.FB_FILMS_TO_DISPLAY)
            },
            {
                'type': 'postback',
                'title': 'Кинотеатры',
                'payload': 'nearest0'
            },
            {
                'type': 'postback',
                'title': 'Служба поддержки',
                'payload': 'support'
            },
            {
                'type': 'postback',
                'title': 'Сообщить о проблеме',
                'payload': 'bug'
            },
        ]
    }
    menu = json.dumps(menu)
    start_button = json.dumps(start_button)
    _configure(greeting)
    _configure(start_button)
    _configure(menu)
