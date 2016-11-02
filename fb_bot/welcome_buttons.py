# coding: utf-8
import json

import settings


def display_welcome_buttons(recipient_id):
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
          'attachment': {
            'type': 'template',
            'payload': {
              'template_type': 'button',
              'text': ('Введите название фильма и я найду его и расписание '
                       'сеансов в ближайшем кинотеатре. '
                       'Если у вас есть любимый кинотеатр, укажите его и я '
                       'вышлю вам расписание именно в этом кинотеатре.'
                       'Или нажмите кнопку «В прокате» или «Кинотеатры»'
                       ),
              'buttons': [
                {
                  'type': 'postback',
                  'payload': '/running{}'.format(settings.FB_FILMS_TO_DISPLAY),
                  'title': 'В прокате'
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
                }
              ]
            }
          }
        }
    }
    payload = json.dumps(payload)
    return payload
