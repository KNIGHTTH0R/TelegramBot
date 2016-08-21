#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from views import CommandReceiveView
import StringIO
import json
import logging
import random
import urllib
import requests
import urllib2

# for sending images
from PIL import Image

import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import webapp2

import settings


class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(
            json.dumps(
                json.loads(
                    requests.get(settings.BASE_URL + 'getMe').content
                )
            )
        )


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(
            json.dumps(
                json.loads(
                    requests.get(
                        '{}{}'.format(settings.BASE_URL, 'getUpdates')
                    ).content
                )
            )
        )


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(
                    json.load(
                        urllib2.urlopen(
                            '{}{}'.format(settings.BASE_URL, 'setWebhook'),
                            urllib.urlencode({'url': ''})
                        )
                    )
                )
            )


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)

        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']

        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(
                    settings.BASE_URL + 'sendMessage',
                    urllib.urlencode(
                        {'chat_id': str(chat_id),
                         'text': msg.encode('utf-8'),
                         'disable_web_page_preview': 'true',
                         'reply_to_message_id': str(message_id),
                         }
                    )
                ).read()
            elif img:
                resp = multipart.post_multipart(
                    '{}{}'.format(settings.BASE_URL + 'sendPhoto'),
                    [('chat_id', str(chat_id)),
                     ('reply_to_message_id', str(message_id)), ],
                    [('photo', 'image.jpg', img), ]
                )
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base + i * j for i in range(512) for j in range(512)]
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        elif 'who are you' in text:
            reply('{}{}'.format('telebot starter kit, created by yukuku:',
                                ' https://github.com/yukuku/telebot'))
        elif 'what time' in text:
            reply('look at the corner of your screen!')
        else:
            if getEnabled(chat_id):
                reply('I got your message! (but I do not know how to answer)')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bot', CommandReceiveView), # /(.*)/
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)