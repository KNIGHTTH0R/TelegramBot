# coding: utf8

from screen.cinema_seances import detect_cinema_seances
from screen.movie_info import display_movie_info
from screen.running_movies import get_cinema_movies

from processing.parser import Parser

from commands import send_reply

import settings


def process_what(bot, chat_id, tuid, whats):
    whats = (whats[:settings.FILMS_DISPLAY_INFO]
             if len(whats) > settings.FILMS_DISPLAY_INFO else whats)
    for w in whats:
        message, mark_up, poster = display_movie_info(w['id'], tuid)
        if not message or not mark_up or not poster:
            bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)
        bot.sendChatAction(chat_id, 'upload_photo')
        bot.sendPhoto(chat_id, ('poster.jpg', poster))
        bot.sendMessage(chat_id, message,
                        reply_markup=mark_up,
                        parse_mode='Markdown', )


def display_afisha(request, bot, chat_id, tuid):

    def film_iteraction(category_name, data):
        flag = False

        category = getattr(data, category_name)
        if category and data.place:

            time = (data.when if isinstance(data.when, list) and
                    len(data.when) > 0 else settings.TODAY)

            for p in data.place:
                for w in category:
                    if send_reply(bot, chat_id, detect_cinema_seances,
                                  int(p['id']), int(w['id']), time):
                        flag = True
            if flag:
                return True
            else:
                bot.sendMessage(chat_id, settings.CINEMA_IS_NOT_SHOWN)

        if category and not flag:
            process_what(bot, chat_id, tuid, category)
            return True

        if data.place and not flag:
            send_reply(bot, chat_id, get_cinema_movies,
                       int(data.place[0]['id']), settings.CINEMA_TO_SHOW)
            return True

    bot.sendChatAction(chat_id, action='typing')
    parser = Parser(request=request, state='base')
    parser.parse()

    for c in ['what', 'genre', 'actors']:
        if film_iteraction(c, parser.data):
            return True
    return False


def display_films(request, bot, chat_id, tuid):

    def film_iteraction(category_name, data):
        category = getattr(data, category_name)
        if category:
            process_what(bot, chat_id, tuid, category)
            return True

    bot.sendChatAction(chat_id, action='typing')
    parser = Parser(request=request, state='film')
    parser.parse()

    for c in ['what', 'genre', 'actors']:
        if film_iteraction(c, parser.data):
            return True
    return False


def display_cinemas(request, bot, chat_id, tuid):

    parser = Parser(request=request, state='cinema')
    parser.parse()

    bot.sendChatAction(chat_id, action='typing')
    if not parser.data.place:
        bot.sendMessage(chat_id, settings.CINEMA_NOT_FOUND)
    else:
        for p in parser.data.place:
            bot.sendMessage(
                chat_id,
                settings.CINEMA_NAME.format(p['shortTitle'].encode('utf-8')),
                parse_mode='Markdown'
            )

            send_reply(bot, chat_id, get_cinema_movies,
                       p['id'], settings.CINEMA_TO_SHOW)
    return True
