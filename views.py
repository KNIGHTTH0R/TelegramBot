# -*- coding: utf8 -*-

import endpoints
import json
import webapp2
import requests

from collections import OrderedDict

import telepot
import botan
from validate_email import validate_email

from google.appengine.api import urlfetch
from google.appengine.ext import deferred

from screen.cinema_seances import display_cinema_seances
from screen.movie_info import display_movie_info
from screen.running_movies import get_cinema_movies
from screen.seances import display_seances_part
from screen.support import (support_dict, send_mail_story,
                            start_markup, support_generation)
from screen.cinemas import get_nearest_cinemas

from processing.parser import parser
from commands import (display_nearest, display_seance, send_reply,
                      display_cinema, display_seances_cinema,
                      display_schedule, display_info_full, display_movies,
                      display_info, display_help, display_return)
from model import (set_user, get_user, get_prev_cmd, set_return_ticket,
                   get_return_ticket, set_prev_cmd)

import settings


def parse(request, bot, chat_id, tuid):
    def process_what(whats):
        for w in whats:
            message, mark_up, poster = display_movie_info(w['id'], tuid)
            if not message or not mark_up or not poster:
                bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
            bot.sendChatAction(chat_id, 'upload_photo')
            bot.sendPhoto(chat_id, ('poster.jpg', poster))
            bot.sendMessage(chat_id, message, reply_markup=mark_up,
                            parse_mode='Markdown', )

    cmds = parser(request)

    flag = False
    if cmds['what'] and cmds['place']:
        time = cmds['when'] if cmds['when'] else settings.TODAY
        for p in cmds['place']:
            for w in cmds['what']:
                if send_reply(bot, chat_id, display_cinema_seances,
                              int(p['id']), int(w['id']), time):
                    flag = True
        if flag:
            return True
        else:
            bot.sendMessage(chat_id, settings.CINEMA_IS_NOT_SHOWN)

    if cmds['what'] and not flag:
        process_what(cmds['what'])
        return True

    if cmds['place'] and not flag:
        send_reply(bot, chat_id, get_cinema_movies,
                   int(cmds['place'][0]['id']), settings.CINEMA_TO_SHOW)
        return True


def detect_instruction(instructions, cmd):
    for f, v in instructions.iteritems():
        for w in v:
            if cmd.startswith(w):
                return f


def make_instruction():
    return OrderedDict({
        display_help: ['/start', '/help'],
        display_nearest: ['/nearest', 'рядом'.decode('utf-8'),
                          'ближайшие'.decode('utf-8')],
        display_cinema: ['/show'],
        display_seance: ['/seance'],
        display_movies: ['/movies', 'фильмы'.decode('utf-8')],
        display_seances_cinema: ['/c'],
        display_schedule: ['/schedule'],
        display_info_full: ['/info_full'],
        display_info: ['/info'],
        display_return: ['/return', 'возврат'.decode('utf-8')]
    })


def track(tuid, message, name='message'):
    deferred.defer(botan.track, settings.BOTAN_TOKEN, tuid, message, name)


class CommandReceiveView(webapp2.RequestHandler):

    def post(self):

        telegram_bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
        urlfetch.set_default_fetch_deadline(30)

        instructions = make_instruction()

        raw = self.request.body.decode('utf-8')
        try:
            payload = json.loads(raw)
        except ValueError:
            raise endpoints.BadRequestException(message='Invalid request body')

        # try:
        cmd, is_group, prev_cmd, chat_id = None, False, None, None
        tuid, message_id = 0, 0
        if 'message' in payload:
            tuid = payload['message']['from']['id']
            chat_id = payload['message']['chat']['id']
            prev_cmd = get_prev_cmd(chat_id)
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
                if not get_user(chat_id):
                    l = payload['message']['location']
                    deferred.defer(set_user, chat_id, l)
                    telegram_bot.sendMessage(
                        chat_id, settings.THANK_FOR_INFORMATION)
                else:
                    l = payload['message']['location']
                    deferred.defer(set_user, chat_id, l)
                    telegram_bot.sendMessage(
                        chat_id, settings.THANK_FOR_INFORMATION_AGAIN)
                # nothing else should be displayed (after location)

                if (detect_instruction(instructions, prev_cmd.cmd) ==
                        display_nearest):
                    send_reply(telegram_bot, chat_id, get_nearest_cinemas,
                               telegram_bot, chat_id,
                               settings.CINEMA_TO_SHOW)
                return

        if 'callback_query' in payload:
            cmd = payload['callback_query']['data']
            chat_id = payload['callback_query']['message']['chat']['id']
            tuid = payload['callback_query']['message']['from']['id']

        elif cmd is None:
            return

        cmd = cmd.lower()
        func = detect_instruction(instructions, cmd)
        if func:
            func(telegram_bot, payload, cmd, chat_id)
            track(tuid, '{} called'.format(func.__name__), func.__name__)

        elif (prev_cmd and prev_cmd.cmd.startswith(
                settings.NO_AGAIN.decode('utf-8'))):
            send_mail_story(telegram_bot, chat_id, settings.NO_AGAIN, cmd)
            track(tuid, 'send email: {}'.format(settings.NO_AGAIN), 'email')

        elif (prev_cmd and prev_cmd.cmd.startswith(
                settings.NO_MAIL_SENDED.decode('utf-8'))):
            send_mail_story(telegram_bot, chat_id,
                            settings.NO_MAIL_SENDED, cmd)
            track(tuid, 'send email: {}'.format(settings.NO_AGAIN), 'email')

        elif (prev_cmd and prev_cmd.cmd.startswith(
                settings.ANOTHER_PAY_ER.decode('utf-8'))):
            send_mail_story(telegram_bot, chat_id,
                            settings.ANOTHER_PAY_ER, cmd)
            track(tuid, 'send email: {}'.format(settings.NO_AGAIN), 'email')

        elif (prev_cmd and
                prev_cmd.cmd.startswith('/seance'.decode('utf-8'))):
            track(tuid, 'callback seance called', 'seance')
            i_n, l_n = prev_cmd.cmd.index('num'), len('num')
            movie_id = prev_cmd.cmd[7: i_n]
            number_of_seances = prev_cmd.cmd[i_n + l_n: len(prev_cmd.cmd)]
            response = display_seances_part(cmd, movie_id,
                                            int(number_of_seances))
            if response is not None:
                telegram_bot.sendMessage(chat_id, response)

        elif (prev_cmd and
                prev_cmd.cmd.startswith('/return'.decode('utf-8'))):
            if prev_cmd.cmd[len('/return'):] == '1':
                track(tuid, 'return: validation + sending', 'return')
                cmd = str(cmd).strip()
                if validate_email(cmd):
                    deferred.defer(set_return_ticket, chat_id, email=cmd)
                    # set_return_ticket(chat_id, email=cmd)
                else:
                    telegram_bot.sendMessage(chat_id,
                                             settings.INVALID_EMAIL)
                    deferred.defer(set_prev_cmd, chat_id, cmd)
                    return
            else:
                try:
                    track(tuid, 'return: need email', 'return')
                    order_numb = int(cmd)

                    deferred.defer(
                        set_return_ticket,
                        chat_id,
                        number=order_numb
                    )

                    deferred.defer(set_prev_cmd, chat_id, '/return' + '1')
                    telegram_bot.sendMessage(chat_id,
                                             settings.ENTER_ORDER_EMAIL)
                except Exception:
                    telegram_bot.sendMessage(chat_id,
                                             settings.INVALID_ORDER)
                    deferred.defer(set_prev_cmd, chat_id, cmd)
                return

            rt = get_return_ticket(chat_id)
            if rt.number and rt.email:

                r = requests.post(
                    settings.URL_CANCEL_TOKEN,
                    json={'order': rt.number, 'email': rt.email}
                )

                r_json = r.json()
                if r_json['error'] != 0:
                    telegram_bot.sendMessage(chat_id,
                                             settings.CANCEL_ERROR)
                else:
                    if r_json['data']['error'] != 0:
                        track(tuid, 'error in canceling', 'return')
                        telegram_bot.sendMessage(chat_id,
                                                 settings.CANCEL_ERROR)
                    else:
                        track(tuid, 'returning correct', 'return')
                        token = r_json['data']['token']
                        url = settings.URL_CANCEL_TICKET.format(token)
                        cancel_r = requests.get(url)
                        telegram_bot.sendMessage(chat_id, cancel_r.json())
            else:
                telegram_bot.sendMessage(chat_id,
                                         settings.ERROR_SERVER_CONN)
                track(tuid, 'invalid email or any else', 'return')
        else:
            if support_generation(cmd, support_dict, telegram_bot,
                                  chat_id, message_id):
                deferred.defer(set_prev_cmd, chat_id, cmd)
                track(tuid, 'support called', 'support')
                return

            elif parse(cmd.encode('utf-8'), telegram_bot,
                       chat_id, tuid):
                deferred.defer(set_prev_cmd, chat_id, cmd)
                track(tuid, 'parse called', 'parse')
                return

            else:
                if not is_group:
                    telegram_bot.sendMessage(
                        chat_id, settings.DONT_UNDERSTAND,
                        parse_mode='Markdown',
                        reply_markup=start_markup())
                    track(tuid, 'miss understanding', 'invalid')

        if cmd:
            prev_cmd = get_prev_cmd(chat_id)
            if prev_cmd and not (cmd[:3]).startswith(prev_cmd.cmd):
                deferred.defer(set_prev_cmd, chat_id, cmd)

        # except Exception as ex:
        #     raise endpoints.BadRequestException(ex.message)
        # return
