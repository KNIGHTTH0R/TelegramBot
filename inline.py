# coding: utf-8

from datetime import datetime, timedelta

import telebot

from telebot import types

from screen.movie_info import display_movie_info
from processing.parser import Parser

import settings


bot_inline = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
CASHE_TIME = 86400


class InlineMode(object):
    def __init__(self, is_inline=False):
        self.is_inline = is_inline


@bot_inline.inline_handler(lambda query: len(query.query) is 0)
def empty_query(query):

    try:
        r = types.InlineQueryResultArticle(
                id='1',
                title=settings.KINOHODBOT_NAME,
                description=settings.FILM_PREVIEW_SHORT,
                input_message_content=types.InputTextMessageContent(
                    message_text=settings.TEXT_INLINE_EMPTY,
                    parse_mode='Markdown'
                )
        )
        bot_inline.answer_inline_query(query.id, [r], cache_time=CASHE_TIME)
    except Exception as e:
        print(e)


@bot_inline.inline_handler(lambda query: len(query.query) > 0)
def query_text(query):

    def process_what(whats, next_url='/seance'):
        whats = (whats[:settings.FILMS_DISPLAY_INFO]
                 if len(whats) > settings.FILMS_DISPLAY_INFO else whats)

        inline_display_films = []
        for w in whats:

            message, mark_up, poster = display_movie_info(
                w.kinohod_id, next_url=next_url
            )

            message = message if message else w.annotationShort
            message = telebot.types.InputTextMessageContent(
                message_text=message,
                parse_mode='Markdown'
            )

            inline_display_films.append(
                types.InlineQueryResultArticle(
                    id=w.kinohod_id,
                    title=w.title,
                    description=w.title,
                    input_message_content=message,
                    thumb_url=poster if poster else None,
                    thumb_width=48 if poster else None,
                    thumb_height=48 if poster else None
                )
            )

        return inline_display_films

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

        if category and not flag:
            inline_display_films = process_what(category)
            bot_inline.answer_inline_query(
                query.id, inline_display_films, cache_time=CASHE_TIME
            )

            return True

        return False

    text = query.query.lower()

    try:
        parser = Parser(request=text, state='base')
        parser.parse()

        if film_iteraction('what', parser.data):
            return True

    except Exception as e:
        print("{!s}\n{!s}".format(type(e), str(e)))
