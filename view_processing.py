# coding: utf8

from datetime import datetime

from screen.cinema_seances import detect_cinema_seances
from screen.movie_info import display_movie_info
from screen.running_movies import get_cinema_movies
from screen.cinemas import cinemas_from_data
from model.film import Film
from processing.parser import Parser

from commands import send_reply

import settings


def process_what(bot, chat_id, tuid, whats, next_url='/seance'):
    whats = (whats[:settings.FILMS_DISPLAY_INFO]
             if len(whats) > settings.FILMS_DISPLAY_INFO else whats)

    for w in whats:

        message, mark_up, poster = display_movie_info(
            w.kinohod_id, tuid, next_url=next_url
        )

        if not message:
            bot.sendMessage(chat_id, settings.SERVER_NOT_VALID)

        if poster:
            bot.sendChatAction(chat_id, 'upload_photo')
            bot.sendPhoto(chat_id, ('poster.jpg', poster))

        bot.sendMessage(chat_id, message,
                        reply_markup=mark_up,
                        parse_mode='Markdown')


def display_afisha(request, bot, chat_id, tuid):

    def film_iteraction(category_name, data):
        flag = False

        category = getattr(data, category_name)
        if category:
            category = filter(lambda f: len(f.cinemas) > 0, category)

        if category and data.place:

            time = data.when if data.when else settings.TODAY
            for p in data.place:
                for w in category:
                    if send_reply(bot, chat_id, detect_cinema_seances,
                                  int(p.kinohod_id), int(w.kinohod_id), time):
                        flag = True
            if flag:
                return True
            else:
                bot.sendMessage(chat_id, settings.CINEMA_IS_NOT_SHOWN)

        if category and not flag:
            process_what(bot, chat_id, tuid, category, next_url='/location')
            return True

        if data.place and not flag:
            if len(data.place) > 1:
                send_reply(bot, chat_id, cinemas_from_data, data.place)
            else:
                send_reply(bot, chat_id, get_cinema_movies,
                           int(data.place[0].kinohod_id),
                           settings.CINEMA_TO_SHOW,
                           datetime.now().strftime('%d%m%Y'),
                           data.place[0].shortTitle)
            return True

    bot.sendChatAction(chat_id, action='typing')
    parser = Parser(request=request, state='base')
    parser.parse()

    if film_iteraction('what', parser.data):
        return True

    parser.parser_special()
    for c in ['genre', 'actors']:
        if film_iteraction(c, parser.data):
            return True
    return False


# def display_films(request, bot, chat_id, tuid):
#
#     def film_iteraction(category_name, data):
#         category = getattr(data, category_name)
#         if category:
#             process_what(bot, chat_id, tuid, category, next_url='/location')
#             return True
#
#     bot.sendChatAction(chat_id, action='typing')
#     parser = Parser(request=request, state='film')
#     parser.parse()
#
#     if film_iteraction('what', parser.data):
#         return True
#
#     parser.parser_special()
#     for c in ['genre', 'actors']:
#         if film_iteraction(c, parser.data):
#             return True
#     return False

#
# def display_cinemas(request, bot, chat_id, tuid):
#
#     parser = Parser(request=request, state='cinema')
#     parser.parse()
#
#     bot.sendChatAction(chat_id, action='typing')
#     if not parser.data.place:
#         bot.sendMessage(chat_id, settings.CINEMA_NOT_FOUND)
#     else:
#         for p in parser.data.place:
#             if not p:
#                 bot.sendMessage(chat_id, settings.DONT_UNDERSTAND)
#                 return True
#
#             bot.sendMessage(
#                 chat_id,
#                 settings.CINEMA_NAME.format(
#                     p.shortTitle.encode('utf-8')
#                 ),
#                 parse_mode='Markdown'
#             )
#
#             date = datetime.now().strftime('%d%m%Y')
#             send_reply(bot, chat_id, get_cinema_movies,
#                        p.kinohod_id, settings.CINEMA_TO_SHOW, date)
#     return True
