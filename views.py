# -*- coding: utf8 -*-

import endpoints
import json
import urllib
import webapp2

import telepot

from telepot.namedtuple import (InlineKeyboardMarkup,
                                ReplyKeyboardMarkup, KeyboardButton)
from google.appengine.api import urlfetch

from draw import draw_cinemahall
from screen.cinema_seances import display_cinema_seances
from screen.help import display_help
from screen.movie_info import display_movie_info
from screen.running_movies import display_running_movies
from screen.seances import display_seances, display_seances_part
from screen.support import support_dict, mail_markup
from processing.parser import parser
from model import (set_user, get_user, get_prev_cmd,
                   set_prev_cmd)

import botan
import settings


def _send_running_movies(telegram_bot, chat_id, films_to_display):
    response, markup = display_running_movies(
        films_to_display
    )

    telegram_bot.sendMessage(chat_id, response,
                             reply_markup=markup)


def parse(request, bot, chat_id, tuid):
    def process_what(whats):
        for w in whats:
            message, mark_up, poster = display_movie_info(w['id'], tuid)
            if not message or not mark_up or not poster:
                bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
            bot.sendChatAction(chat_id, 'upload_photo')
            bot.sendPhoto(chat_id, ('poster.jpg', poster))
            bot.sendMessage(chat_id, message, reply_markup=mark_up,
                            parse_mode='Markdown')

    cmds = parser(request)

    if cmds['what'] and not cmds['category']:
        process_what(cmds['what'])
        return True

    flag = False
    if cmds['what'] and cmds['place']:
        for p in cmds['place']:
            for w in cmds['what']:
                if send_cinema(bot, chat_id, int(p['id']),
                               int(w['id']), settings.TODAY):
                    flag = True
        if flag:
            return True
        else:
            bot.sendMessage(chat_id, settings.CINEMA_IS_NOT_SHOWN)

    if cmds['what'] and not flag:
        process_what(cmds['what'])
        return True


def _send_seances(telegram_bot, chat_id, movie_id, number_of_seances,
                  payload):

    response, mark_up = display_seances(
        chat_id, movie_id, int(number_of_seances)
    )

    callback_msg = payload['callback_query']['message']
    chat_id = callback_msg['chat']['id']

    if int(number_of_seances) == settings.SEANCES_TO_DISPLAY:
        telegram_bot.sendMessage(chat_id, settings.FIND_CINEMA)

    if mark_up:
        telegram_bot.sendMessage(chat_id, response,
                                 parse_mode='Markdown', reply_markup=mark_up)
    else:
        telegram_bot.sendMessage(chat_id, response, parse_mode='Markdown')


def send_cinema(telegram_bot, chat_id, cinema_id, movie_id, d):
    response, markup = display_cinema_seances(cinema_id, movie_id, d)
    if response is not None and markup is not None:
        telegram_bot.sendMessage(chat_id, response,
                                 parse_mode='Markdown',
                                 reply_markup=markup)
        return True
    return False


def _send_success(telegram_bot, callback_query_id):
    telegram_bot.answerCallbackQuery(
        callback_query_id=callback_query_id,
        text=':)')


def _send_mail_story(telegram_bot, chat_id, text, cmd):
    markup = mail_markup('{} my email: {}'.format(
        settings.support_a[text],
        cmd.encode('utf-8')
    ))

    telegram_bot.sendMessage(
        chat_id, settings.NEED_CONTACT, markup
    )


def keyboard_generator(texts):
    keyboard = []
    for text in texts:
        keyboard.append([KeyboardButton(text=text)])
    return ReplyKeyboardMarkup(keyboard=keyboard)


def msg_generator(telegram_bot, chat_id, msg, texts=None,
                  message_id=None, markup=None):
    if markup is None:
        markup = keyboard_generator(texts) if texts else None

    telegram_bot.sendMessage(
        chat_id, msg,
        reply_to_message_id=message_id,
        reply_markup=markup
    )


def start_markup():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=settings.SUPPORT_INFO)],
    ])


def support_generation(cmd, d, bot, chat_id, message_id):
    for k, v in d.iteritems():
        if cmd.startswith(k.decode('utf-8')):
            msg_generator(bot, chat_id, v.msg, message_id=message_id,
                          texts=v.texts, markup=v.markup)
            return True
    return False


class CommandReceiveView(webapp2.RequestHandler):

    def post(self):

        telegram_bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
        urlfetch.set_default_fetch_deadline(30)

        commands = {
            '/start': display_help,
            '/help': display_help,
        }

        raw = self.request.body.decode('utf-8')
        try:
            payload = json.loads(raw)
        except ValueError:
            raise endpoints.BadRequestException(message='Invalid request body')

        try:
            if 'message' in payload:
                telegram_user_id = payload['message']['from']['id']
                chat_id = payload['message']['chat']['id']
                is_group = False

                prev_cmd = get_prev_cmd(chat_id)
                update_id = int(payload['update_id'])
                if prev_cmd and (update_id < prev_cmd.update_id):
                    return

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
                if not cmd:
                    return
                message_id = payload['message']['message_id']
                if 'location' in payload['message']:
                    if not get_user(chat_id):
                        l = payload['message']['location']
                        set_user(chat_id=chat_id, location=l)
                        telegram_bot.sendMessage(
                            chat_id, settings.THANK_FOR_INFORMATION)
                    else:
                        l = payload['message']['location']
                        set_user(chat_id=chat_id, location=l)
                        telegram_bot.sendMessage(
                            chat_id, settings.THANK_FOR_INFORMATION_AGAIN)
                    # nothing else should be displayed (after location)
                    return

            if 'callback_query' in payload:
                cmd = payload['callback_query']['data']
                callback_query_id = int(payload['callback_query']['id'])
                chat_id = payload['callback_query']['message']['chat']['id']
                update_id = int(payload['callback_query']['update_id'])

                if not cmd:
                    return
                elif cmd.startswith('/seance'):
                    i_n = cmd.index('num')
                    movie_id = cmd[len('/seance'): i_n]
                    number_of_seances = cmd[i_n + len('num'): len(cmd)]
                    _send_seances(telegram_bot, chat_id, movie_id,
                                  number_of_seances, payload)
                    _send_success(telegram_bot, callback_query_id)
                elif cmd.startswith('/movies'):
                    number_to_display = int(cmd[7:len(cmd)])
                    _send_running_movies(telegram_bot, chat_id,
                                         number_to_display)
                    _send_success(telegram_bot, callback_query_id)
                elif cmd.startswith('/c'):
                    index_of_m, index_of_d = cmd.index('m'), cmd.index('d')
                    cinema_id = cmd[2:index_of_m]
                    movie_id, d = cmd[index_of_m + 1:index_of_d], cmd[-1]
                    send_cinema(telegram_bot, chat_id, cinema_id, movie_id, d)
            elif cmd.startswith('/schedule'):
                schedule_id = cmd[9: len(cmd)]
                try:
                    hall_image = draw_cinemahall(schedule_id)
                    city_name_dict = {'cityName': u'Москва'.encode('utf-8')}
                    url_encoded_dict = urllib.urlencode(city_name_dict)
                    shorten_url = botan.shorten_url(
                        'https://kinohod.ru/widget/?{}#scheme_{}'.format(
                            url_encoded_dict, schedule_id
                        ), settings.BOTAN_TOKEN, telegram_user_id
                    )
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text=settings.BUY_TICKET, url=shorten_url)]
                    ])
                    telegram_bot.sendChatAction(chat_id, 'upload_photo')
                    telegram_bot.sendPhoto(chat_id, ('hall.bmp', hall_image),
                                           reply_markup=markup)
                except:
                    telegram_bot.sendMessage(chat_id,
                                             settings.SERVER_NOT_VALID)

            elif cmd.startswith('/info_full'):
                telegram_bot.sendMessage(chat_id, settings.INFO_FULL)

            elif cmd.startswith('/info'):
                movie_id = cmd[5:len(cmd)]
                message, mark_up, movie_poster = display_movie_info(
                    movie_id, telegram_user_id
                )
                if not message or not mark_up or not movie_poster:
                    telegram_bot.sendMessage(chat_id,
                                             settings.SERVER_NOT_VALID)
                telegram_bot.sendChatAction(chat_id, 'upload_photo')
                telegram_bot.sendPhoto(chat_id, ('poster.jpg', movie_poster))
                telegram_bot.sendMessage(chat_id, message,
                                         reply_markup=mark_up,
                                         parse_mode='Markdown')
            elif cmd.startswith('/c'):
                index_of_m = cmd.index('m')
                cinema_id = cmd[2:index_of_m]
                movie_id = cmd[index_of_m + 1:len(cmd)]
                send_cinema(telegram_bot, chat_id, cinema_id, movie_id,
                            settings.TODAY)

            elif cmd.startswith('/movies'):
                _send_running_movies(telegram_bot, chat_id,
                                     settings.FILMS_TO_DISPLAY)

            elif (prev_cmd and prev_cmd.cmd.startswith(
                    settings.NO_AGAIN.decode('utf-8'))):
                _send_mail_story(telegram_bot, chat_id, settings.NO_AGAIN, cmd)

            elif (prev_cmd and prev_cmd.cmd.startswith(
                    settings.NO_MAIL_SENDED.decode('utf-8'))):
                _send_mail_story(telegram_bot, chat_id,
                                 settings.NO_MAIL_SENDED, cmd)

            elif (prev_cmd and prev_cmd.cmd.startswith(
                    settings.ANOTHER_PAY_ER.decode('utf-8'))):
                _send_mail_story(telegram_bot, chat_id,
                                 settings.ANOTHER_PAY_ER, cmd)
            elif (prev_cmd and
                    prev_cmd.cmd.startswith('/seance'.decode('utf-8'))):
                i_n, l_n = prev_cmd.cmd.index('num'), len('num')
                movie_id = prev_cmd.cmd[7: i_n]
                number_of_seances = prev_cmd.cmd[i_n + l_n: len(prev_cmd.cmd)]
                response = display_seances_part(cmd, movie_id,
                                                int(number_of_seances))
                telegram_bot.sendMessage(chat_id, response)

            else:
                if support_generation(cmd, support_dict, telegram_bot,
                                      chat_id, message_id):
                    set_prev_cmd(chat_id, cmd, update_id)
                    return

                markup = start_markup()
                func = commands.get(cmd.split()[0].lower())
                if func:
                    text = func()
                    telegram_bot.sendMessage(chat_id, text,
                                             reply_markup=markup)

                elif parse(cmd.encode('utf-8'), telegram_bot,
                         chat_id, telegram_user_id):
                    set_prev_cmd(chat_id, cmd, update_id)
                    return

                else:
                    if not is_group:
                        telegram_bot.sendMessage(
                            chat_id, settings.DONT_UNDERSTAND,
                            reply_markup=markup)
            if cmd:
                prev_cmd = get_prev_cmd(chat_id)
                if prev_cmd and not (cmd[:3]).startswith(prev_cmd.cmd):
                    set_prev_cmd(chat_id, cmd, update_id)

        except Exception as ex:
            raise endpoints.BadRequestException(ex.message)
