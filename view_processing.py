# coding: utf8

from screen.cinema_seances import display_cinema_seances
from screen.movie_info import display_movie_info
from screen.running_movies import get_cinema_movies

from processing.parser import parser

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
