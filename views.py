# -*- coding: utf8 -*-

import json

from collections import OrderedDict, namedtuple

import endpoints
import webapp2
import telepot

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from botan import track
from commands import (display_nearest, display_seance, send_reply,
                      display_cinema, display_seances_cinema, callback_seance,
                      display_schedule, display_movies, display_future_seances,
                      display_info, display_help, display_movie_time_selection,
                      display_return, callback_return, display_location_seance,
                      callback_movie_time_selection, callback_seance_text,
                      display_movie_nearest_cinemas, display_full_info,
                      display_cinemas_where_film)

from view_processing import detect_premiers
from screen.support import send_mail_story, start_markup, support_generation
from screen.cinemas import get_nearest_cinemas
from model.base import UserProfile
from model.base import set_model, get_model
from view_processing import display_afisha


import settings


def detect_instruction(instructions, cmd):
    for f, v in instructions.iteritems():
        for w in v:
            if cmd.startswith(w):
                return f


def detect_cb(instructions, profile):
    if not profile.cmd:
        return

    for k, v in instructions.iteritems():
        if profile.cmd.startswith(k.decode('utf-8').lower()):
            return v


def make_instruction():
    return OrderedDict({
        display_help: ['/start', '/help'],
        display_nearest: ['/nearest'],
        display_cinema: ['/show'],
        display_seance: ['/seance'],
        display_future_seances: ['/future'],
        display_movies: ['/movies'],
        display_cinemas_where_film: ['/where_film'],
        display_movie_time_selection: ['/anytime'],
        display_location_seance: ['/location'],
        display_seances_cinema: ['/c'],
        display_schedule: ['/schedule'],
        display_full_info: ['/fullinfo'],
        display_info: ['/info'],
        display_return: ['/return']
    })


def callback_instruction():
    return OrderedDict({
        settings.NO_AGAIN: send_mail_story,
        settings.NO_MAIL_SENDED: send_mail_story,
        settings.ANOTHER_PAY_ER: send_mail_story,
        '/location': callback_seance_text,
        '/seance': callback_seance,
        '/return': callback_return,
        '/anytime': callback_movie_time_selection,
    })


def update_location(l, bot, chat_id, instructions):
    profile = set_model(UserProfile, chat_id, location=l)
    if not profile.cmd:
        bot.sendMessage(chat_id, settings.THANK_FOR_INFORMATION)
    else:
        bot.sendMessage(chat_id, settings.THANK_FOR_INFORMATION_AGAIN)

    if detect_instruction(instructions, profile.cmd) == display_nearest:
        send_reply(bot, chat_id, get_nearest_cinemas,
                   bot, chat_id, settings.CINEMA_TO_SHOW)

    if (detect_instruction(instructions, profile.cmd) ==
            display_location_seance):
        send_reply(bot, chat_id, display_movie_nearest_cinemas,
                   0, bot, chat_id, settings.CINEMA_TO_SHOW, '', profile)
        deferred.defer(set_model, UserProfile, chat_id, cmd='update_location')


class CommandReceiveView(webapp2.RequestHandler):

    def post(self):

        bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
        urlfetch.set_default_fetch_deadline(30)
        instructions = make_instruction()
        raw = self.request.body.decode('utf-8')

        try:
            payload = json.loads(raw)
        except ValueError:
            raise endpoints.BadRequestException(message='Invalid request body')

        cmd, is_group, profile, chat_id = None, False, None, None
        tuid, message_id = 0, 0

        if 'message' in payload:
            tuid = payload['message']['from']['id']
            chat_id = payload['message']['chat']['id']

            if payload['message']['chat']['type'] == 'group':
                is_group = True
                cmd = payload['message'].get('text')
                if cmd:
                    if '@' in cmd:
                        p = cmd.split('@')
                        if p[-1].find(settings.bot_username) > -1:
                            cmd = p[0]
                        else:
                            return
                else:
                    return
            else:
                cmd = payload['message'].get('text')

            message_id = payload['message']['message_id']
            if 'location' in payload['message']:
                update_location(payload['message']['location'],
                                bot, chat_id, instructions)

        if 'callback_query' in payload:
            cmd = payload['callback_query']['data']
            chat_id = payload['callback_query']['message']['chat']['id']
            tuid = payload['callback_query']['message']['from']['id']

        elif cmd is None:
            return

        # try:
        profile = get_model(UserProfile, chat_id)
        cmd = cmd.lower()
        func_detected_flag = False

        support_send = [
            settings.NO_AGAIN.decode('utf-8').lower(),
            settings.NO_MAIL_SENDED.decode('utf-8').lower(),
            settings.ANOTHER_PAY_ER.decode('utf-8').lower()
        ]

        if (cmd.startswith('/') or
                (profile and profile.cmd and
                 (profile.cmd.startswith('/') or
                  (profile.cmd in support_send)))):

            func = detect_instruction(instructions, cmd)
            if func:
                func(bot, payload, cmd, chat_id)
                func_detected_flag = True
                track(tuid, '{} called'.format(func.__name__), func.__name__)

            else:
                cb_fn = detect_cb(callback_instruction(), profile)
                if cb_fn:
                    func_detected_flag = True
                    cb_fn(tuid, bot, chat_id, profile.cmd, cmd, profile)

        if not func_detected_flag:
            Schema = namedtuple('Schema', ['reply', 'markup'])

            s = {
                'base': Schema(display_afisha, start_markup),
                # 'films': Schema(display_films, start_markup),
                # 'cinema': Schema(display_cinemas, start_markup)
            }

            if support_generation(cmd, bot, chat_id, message_id):
                track(tuid=tuid,
                      message=format(s[profile.state].reply.__name__),
                      name='support')

            elif detect_premiers(cmd.encode('utf-8'), bot, payload, chat_id):
                track(tuid=tuid,
                      message=cmd.encode('utf-8'),
                      name=detect_premiers.__name__)

            elif s[profile.state].reply(cmd.encode('utf-8'),
                                        bot, chat_id, tuid):
                track(tuid=tuid,
                      message=format(s[profile.state].reply.__name__),
                      name='parsing')

            else:
                if not is_group:
                    bot.sendMessage(
                        chat_id, settings.DONT_UNDERSTAND,
                        parse_mode='Markdown',
                        reply_markup=s[profile.state].markup())
                    track(tuid, 'miss understanding', 'invalid')

        deferred.defer(set_model, UserProfile, chat_id,
                       cmd=cmd, chat_id=int(chat_id))

        # except Exception as ex:
        #     return
        # raise endpoints.BadRequestException(ex.message)
