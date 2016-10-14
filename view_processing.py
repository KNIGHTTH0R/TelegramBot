# coding: utf8

from datetime import datetime, timedelta
from collections import namedtuple

from screen.cinema_seances import detect_cinema_seances
from screen.movie_info import display_movie_info
from screen.running_movies import get_cinema_movies
from screen.cinemas import cinemas_from_data
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
        two_weeks = timedelta(days=14)

        if category:
            now = datetime.now()
            new_category = []
            for f in category:
                if len(f.cinemas) > 0:
                    new_category.append(f)

                elif (f.premiereDateRussia and
                      now < f.premiereDateRussia < (now + two_weeks)):
                    new_category.append(f)

                elif (f.premiereDateWorld and
                      now < f.premiereDateWorld < (now + two_weeks)):
                    new_category.append(f)

            category = new_category

        if category and data.place:

            no_display = {}

            now = datetime.now()
            time = data.when if data.when else now

            for p in data.place:
                for w in category:

                    if w.premiereDateRussia and w.premiereDateRussia > time:
                        continue

                    if p.key not in w.cinemas and w.premiereDateRussia < now:
                        if p.shortTitle not in no_display:
                            no_display[p.shortTitle] = [(w, p)]
                        else:
                            no_display[p.shortTitle].append((w, p))
                        continue

                    if send_reply(bot, chat_id, detect_cinema_seances,
                                  int(p.kinohod_id), int(w.kinohod_id), time):
                        flag = True

            display_film_no_any_seances(bot, chat_id, no_display)

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
        return False

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


RowDisplay = namedtuple('RowDisplay', ['title', 'films'])


def display_film_no_any_seances(bot, chat_id, no_display):

    cinemas = []
    for short_name, l in no_display.iteritems():
        cinemas.append(
            RowDisplay(
                short_name,
                [settings.Row(t[0].title, t[0].kinohod_id) for t in l]
            )
        )

    if cinemas:
        bot.sendMessage(
            chat_id,
            settings.JINJA_ENVIRONMENT.get_template(
                'cinema_film_no_display.md'
            ).render({'cinemas': cinemas, 'sign_point': settings.SIGN_POINT}),
            parse_mode='Markdown'
        )
