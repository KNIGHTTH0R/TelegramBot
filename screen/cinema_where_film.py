# coding: utf-8

import json

from telepot.namedtuple import InlineKeyboardMarkup

from model.cinema import Cinema
from personolized_data import detect_film_cinemas


import settings


def cinemas_where_film(film, number_to_display=None,
                       to_show=settings.CINEMAS_TO_DISPLAY,
                       chat_id=None):

    film_cinemas, city_id = detect_film_cinemas(
        chat_id=chat_id,
        movie_id=film.kinohod_id,
        date=None
    )

    cinemas = []
    for i, p in enumerate(film_cinemas):

        if number_to_display and to_show and i < (number_to_display - to_show):
            continue

        cinema = p['cinema']
        if cinema.get('city') != city_id:
            continue

        cinemas.append(
            settings.RowCinema(
                cinema.get('shortTitle'),
                cinema.get('address'),
                cinema.get('mall'),
                '/c{}m{}'.format(cinema.get('id'), film.kinohod_id)
            )
        )

        if number_to_display and to_show and len(cinemas) == to_show:
            return cinemas

    return cinemas


def get_cinemas_where_film(film,
                           number_to_display=settings.CINEMAS_TO_DISPLAY,
                           chat_id=None):

    cinemas = cinemas_where_film(
        film, number_to_display=number_to_display, chat_id=chat_id
    )

    if len(cinemas) < 1:
        return settings.FILM_NO_CINEMA, None

    template = settings.JINJA_ENVIRONMENT.get_template(
        'cinema_where_film.md'
    )

    msg = template.render({
        'film_name': film.title,
        'seances': cinemas
    })

    if not number_to_display:
        number_to_display = 0

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data='/where_film{}num{}'.format(
                  film.kinohod_id,
                  number_to_display + settings.CINEMAS_TO_DISPLAY
              ))]
    ])

    return msg, mark_up
