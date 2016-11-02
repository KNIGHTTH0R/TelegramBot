# coding: utf-8

import json
import webapp2

import settings

from fb_bot.chat_handling import handle_text_message, handle_attachments
from fb_bot.chat_handling import handle_quick_reply, handle_back_payload
from fb_bot.chat_handling import handle_text_with_payload

from fb_bot.configure_bot import configure
from fb_bot.display_premieres import display_premieres
from fb_bot.helper_methods import get_by_recipient_id
from fb_bot.running_movies import display_running_movies
from fb_bot.special_words import all_types_of_films, on_screens, premieres
from google.appengine.api import urlfetch
from processing.maching import damerau_levenshtein_distance


def update_last_callback(recipient_id):
    u_info = get_by_recipient_id(recipient_id)
    u_info.last_callback = ''
    u_info.put()


def _construct_payload(message, recipient_id):
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message
        }
    }
    payload = json.dumps(payload)
    return payload


def _construct_button_payload(recipient_id, text, buttons):

    discount_payload = {
      'recipient': {
        'id': recipient_id
      },
      'message': {
        'attachment': {
          'type': 'template',
          'payload': {
            'template_type': 'button',
            'text': text,
            'buttons': buttons
          }
        }
      }
    }
    return json.dumps(discount_payload)


def _send_payload(payload):
    request_endpoint = ('https://graph.facebook.com/v2.6/me/messages?'
                        'access_token={}'.format(settings.PAGE_ACCESS_TOKEN))
    response = urlfetch.fetch(
        url=request_endpoint,
        payload=payload,
        method=urlfetch.POST,
        headers={u'Content-Type': u'application/json'}
        )
    return response.content


def _typing_payload(recipient_id):
    payload = {
        'recipient': {
                    'id': recipient_id
                },
        'sender_action': 'typing_on'
    }
    return json.dumps(payload)


def construct_cinema_movie_generic(cinema, movie_id):
    my_id = 'kinohod_id' if 'kinohod_id' in cinema else 'id'

    stations_str = ', '.join(
        map(lambda x: x.get('name', ''), cinema.get('subway_stations'))
    ) if 'subway_stations' in cinema else ''

    button = {
        'type': 'postback',
        'title': 'Сеансы',
        'payload': '/c{}m{}d{}'.format(cinema[my_id], movie_id,
                                       settings.TODAY)
    }
    c_info = {
        'title': cinema['shortTitle'],
        'subtitle': u'{}\n{}'.format(settings.uncd(cinema
                                                   ['address']),
                                     settings.uncd(stations_str)),
        'buttons': [button]
    }
    return c_info


def handle_special_words(recipient_id, message):
    for word in all_types_of_films:
        if (damerau_levenshtein_distance(
                word, settings.uncd(message).lower()) < 3):
            payload = display_running_movies(
                recipient_id, settings.FB_FILMS_TO_DISPLAY)
            return payload

    for word in on_screens:
        if (damerau_levenshtein_distance(
                word, settings.uncd(message).lower()) < 3):
            payload = display_running_movies(
                recipient_id, settings.FB_FILMS_TO_DISPLAY,
                only_on_scr=True
            )
            return payload

    for word in premieres:
        if (damerau_levenshtein_distance(
                word, settings.uncd(message).lower()) < 3):
            payload = display_premieres(
                recipient_id, settings.FB_FILMS_TO_DISPLAY,
            )
            return payload

    return None


class FBWebHookHandler(webapp2.RequestHandler):

    def get(self):

        if self.request.get('hub.verify_token') == 'to_be_or_not_to_be':
            return self.response.write(self.request.get('hub.challenge'))
        else:
            configure()
            return self.response.write('Success')

    def post(self):
        income_json = json.loads(self.request.body)
        events = income_json['entry'][0]['messaging']
        for event in events:
            recipient_id = int(event['sender']['id'])
            if event.get('message') and event['message'].get('attachments'):
                typing = _typing_payload(recipient_id)
                _send_payload(typing)
                payloads = handle_attachments(event)
                if isinstance(payloads, list):
                    for payload in payloads:
                        resp = _send_payload(payload)
                else:
                    resp = _send_payload(payloads)
                self.response.write(resp)
                return

            if event.get('message') and event['message'].get('quick_reply'):
                update_last_callback(recipient_id)
                payload = event['message']['quick_reply']['payload']
                recipient_id = int(event['sender']['id'])
                typing = _typing_payload(recipient_id)
                _send_payload(typing)

                payloads = handle_quick_reply(payload, recipient_id)
                if isinstance(payloads, list):
                    for payload in payloads:
                        resp = _send_payload(payload)
                else:
                    resp = _send_payload(payloads)
                self.response.write(resp)
                return

            if event.get('postback') and event['postback'].get('payload'):
                typing = _typing_payload(recipient_id)
                _send_payload(typing)
                update_last_callback(recipient_id)
                back_payload = event['postback']['payload']
                recipient_id = int(event['sender']['id'])
                payloads = handle_back_payload(back_payload, recipient_id)
                if isinstance(payloads, list):
                    for payload in payloads:
                        resp = _send_payload(payload)
                else:
                    resp = _send_payload(payloads)
                self.response.write(resp)
                return

            if event.get('message') and event['message'].get('text'):
                message = event['message']['text']
                typing = _typing_payload(recipient_id)
                _send_payload(typing)

                payload = handle_special_words(recipient_id, message)
                if payload:
                    self.response.write(_send_payload(payload))
                    return

                if settings.uncd(message).find(u'В прокате') != -1:
                    update_last_callback(recipient_id)

                    payload = display_running_movies(
                        recipient_id, settings.FB_FILMS_TO_DISPLAY
                    )
                    self.response.write(_send_payload(payload))
                    return

                u_info = get_by_recipient_id(recipient_id)
                if u_info and u_info.last_callback:
                    payload = u_info.last_callback

                    payloads = handle_text_with_payload(
                        u_info, recipient_id, payload,  message
                    )
                    if isinstance(payloads, list):
                        for payload in payloads:
                            resp = _send_payload(payload)
                    else:
                        resp = _send_payload(payloads)
                    self.response.write(resp)
                    return
                else:
                    typing = _typing_payload(recipient_id)
                    _send_payload(typing)
                    payload = handle_text_message(recipient_id, message)
                    self.response.write(
                        _send_payload(payload)
                    )
                    return
