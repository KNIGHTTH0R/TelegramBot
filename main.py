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


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bot', CommandReceiveView), # /(.*)/
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
], debug=True)
