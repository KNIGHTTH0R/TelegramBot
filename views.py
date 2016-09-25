# -*- coding: utf8 -*-

import json

import endpoints
import webapp2

from collections import OrderedDict

import telepot

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from botan import track

from commands import (display_nearest, display_seance, send_reply,
                      display_cinema, display_seances_cinema, callback_seance,
                      display_schedule, display_info_full, display_movies,
                      display_info, display_help,
                      display_return, callback_return)

from screen.support import send_mail_story, start_markup, support_generation

from screen.cinemas import get_nearest_cinemas

from model import UserProfile
from model import set_model, get_model

from view_processing import parse_afisha, parse_cinemas, parse_films

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
        if profile.cmd.startswith(k.decode('utf-8')):
            return v


def make_instruction():
    return OrderedDict({
        display_help: ['/start', '/help'],
        display_nearest: ['/nearest'],
        display_cinema: ['/show'],
        display_seance: ['/seance'],
        display_movies: ['/movies'],
        display_seances_cinema: ['/c'],
        display_schedule: ['/schedule'],
        display_info_full: ['/info_full'],
        display_info: ['/info'],
        display_return: ['/return']
    })


def callback_instruction():
    return OrderedDict({
        settings.NO_AGAIN: send_mail_story,
        settings.NO_MAIL_SENDED: send_mail_story,
        settings.ANOTHER_PAY_ER: send_mail_story,
        '/seance': callback_seance,
        '/return': callback_return
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

        # try:
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

        profile = get_model(UserProfile, chat_id)
        cmd = cmd.lower()

        if cmd.startswith('/'):
            func = detect_instruction(instructions, cmd)
            if func:
                func(bot, payload, cmd, chat_id)
                track(tuid, '{} called'.format(func.__name__), func.__name__)

            else:
                cb_fn = detect_cb(callback_instruction(), profile)
                if cb_fn:
                    cb_fn(tuid, bot, chat_id, profile.cmd, cmd, profile)

        else:

            s = {
                'base': parse_afisha,
                'films': parse_films,
                'cinema': parse_cinemas
            }

            if support_generation(cmd, bot,
                                  chat_id, message_id):
                deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)
                return

            elif s[profile.state](cmd.encode('utf-8'), bot, chat_id, tuid):
                track(tuid, format(s[profile.state].__name__), 'parsing')
                pass

            # elif parse(cmd.encode('utf-8'), bot, chat_id, tuid):
            #     deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)
            #     track(tuid, 'parse called', 'parse')
            #     return

            else:
                if not is_group:
                    bot.sendMessage(
                        chat_id, settings.DONT_UNDERSTAND,
                        parse_mode='Markdown',
                        reply_markup=start_markup())
                    track(tuid, 'miss understanding', 'invalid')

        deferred.defer(set_model, UserProfile, chat_id, cmd=cmd)

        # except Exception as ex:
        #    raise endpoints.BadRequestException(ex.message)
