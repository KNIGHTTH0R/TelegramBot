# coding: utf-8

import contextlib
import urllib2
import json

from datetime import datetime
from collections import namedtuple

from telepot.namedtuple import InlineKeyboardMarkup

from model.film import Film

import botan
import settings


def _get_movie_trailer_link(trailer_hash):
    ab, cd = trailer_hash[0:2], trailer_hash[2:4]
    url = '{}{}/{}/{}'.format(settings.URL_BASE_O, ab, cd, trailer_hash)
    return url


def _get_movie_poster(poster_hash):
    if not poster_hash or len(poster_hash) < 4:
        return
    ab, cd = poster_hash[0:2], poster_hash[2:4]
    url = '{}{}/{}/{}'.format(settings.URL_BASE_P, ab, cd, poster_hash)
    try:
        poster = urllib2.urlopen(url)
        return poster
    except:
        return


def display_movie_info(movie_id, telegram_user_id,
                       next_url='/seance', full=False):
    now = datetime.now()

    film = Film.get_by_id(str(movie_id))
    if not film:
        display_movie_info_api(movie_id, telegram_user_id, next_url='/seance')

    if film.poster:
        movie_poster = _get_movie_poster(film.poster.name)
    else:
        movie_poster = None

    if film.trailers and len(film.trailers) > 0:

        trailer = film.trailers[0].get()
        video_hash = trailer.videos[0].filename

        trailer_url = _get_movie_trailer_link(video_hash)
        shorten_url = botan.shorten_url(trailer_url, settings.BOTAN_TOKEN,
                                        telegram_user_id)

        if film.premiereDateRussia and film.premiereDateRussia > now:
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                dict(text=settings.TREILER, url=shorten_url),
                dict(text=settings.NEAREST_SEANCES,
                     callback_data='/future{}'.format(movie_id))
            ]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                dict(text=settings.TREILER, url=shorten_url),
                dict(text=settings.CHOOSE_SEANCE,
                     callback_data=('{}{}num{}'.format(
                         next_url, film.kinohod_id,
                         settings.CINEMAS_TO_DISPLAY)
                     )),
            ]])

    else:
        if film.premiereDateRussia and film.premiereDateRussia > now:
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                dict(text=settings.NEAREST_SEANCES,
                     callback_data='/future{}'.format(movie_id))
            ]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                dict(text=settings.CHOOSE_SEANCE,
                     callback_data=('{}{}num{}'.format(
                         next_url, film.kinohod_id, 20)
                     ))
            ]])

    Annotation = namedtuple('Annotation', ['title', 'link'])

    if full:
        template = settings.JINJA_ENVIRONMENT.get_template(
            'movies_info_full.md'
        )

        actors = film.actors
        ann_o = Annotation(film.annotationFull, '')

        return template.render({
            'title': film.title,
            'description': ann_o,
            'duration': film.duration if film.duration else None,
            'premier': (film.premiereDateRussia.strftime('%d.%m.%Y')
                        if film.premiereDateRussia else None),
            'sign_calendar': settings.SIGN_CALENDAR,
            'age': film.ageRestriction if film.ageRestriction else None,
            'sign_genre': settings.SIGN_GENRE,
            'kinder': settings.SIGN_CHILD_AGE,
            'sign_time': settings.SIGN_ALARM,
            'genres': ', '.join(
                [a.get().name.encode('utf-8') for a in film.genres]
            ).decode('utf-8'),
            'sign_actor': settings.SIGN_ACTOR,
            'actors': ', '.join(
                [a.name.encode('utf-8') for a in actors]
            ).decode('utf-8') if actors else None,

            'directors': ', '.join(
                [a.name.encode('utf-8') for a in film.directors]
            ).decode('utf-8') if film.directors else None,
            'sign_producer': settings.SIGN_PRODUCER,
        }), markup, movie_poster

    else:
        template = settings.JINJA_ENVIRONMENT.get_template('movies_info.md')
        actors = (film.actors[:3] if film.actors and len(film.actors) > 3
                  else film.actors)

        ann_o = Annotation(
            film.annotationShort,
            'Подробнее: /fullinfo{}'.decode('utf-8').format(movie_id)
        )

        return template.render({
            'title': film.title,
            'description': ann_o,
            'sign_genre': settings.SIGN_GENRE,
            'genres': ', '.join(
                [a.get().name.encode('utf-8') for a in film.genres]
            ).decode('utf-8'),
            'sign_actor': settings.SIGN_ACTOR,
            'actors': ', '.join(
                [a.name.encode('utf-8') for a in actors]
            ).decode('utf-8'),

            'directors': ', '.join(
                [a.name.encode('utf-8') for a in film.directors]
            ).decode('utf-8'),
            'sign_producer': settings.SIGN_PRODUCER,
        }), markup, movie_poster


def display_movie_info_api(movie_id, telegram_user_id, next_url='/seance'):

    def get_data(name):
        return ', '.join([a.encode('utf-8') for a in html_data[name]])

    url = settings.URL_MOVIES_INFO.format(movie_id, settings.KINOHOD_API_KEY)

    try:
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            html_data = json.loads(jf.read())
    except Exception as e:
        import logging
        logging.info(e.message)
        return None, None, None

    if isinstance(html_data, list):
        html_data = html_data[-1]

    if not html_data:
        return None, None, None

    movie_poster = _get_movie_poster(html_data['poster'])

    if ('trailers' in html_data and isinstance(html_data['trailers'], list) and
            len(html_data) > 0 and 'mobile_mp4' in html_data['trailers'][0]):
        kinohod_trailer_hash = (html_data['trailers'][0]
                                ['mobile_mp4']['filename'])
        trailer_url = _get_movie_trailer_link(kinohod_trailer_hash)
        shorten_url = botan.shorten_url(trailer_url, settings.BOTAN_TOKEN,
                                        telegram_user_id)
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text=settings.TREILER, url=shorten_url),
            dict(text=settings.CHOOSE_SEANCE,
                 callback_data=('{}{}num{}'.format(
                     next_url, html_data['id'],
                     settings.CINEMAS_TO_DISPLAY)
                 )),
        ]])
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text=settings.CHOOSE_SEANCE,
                 callback_data=('{}{}num{}'.format(
                     next_url, html_data['id'], 20)
                 ))
        ]])

    template = settings.JINJA_ENVIRONMENT.get_template('movies_info.md')
    return (template.render({
        'title': html_data['title'],
        'description': html_data['annotationFull'],
        'duration': '{}'.format(html_data['duration']),
        'genres': get_data('genres').decode('utf-8'),
        'sign_actor': settings.SIGN_ACTOR,
        'actors': get_data('actors').decode('utf-8'),
        'producers': get_data('producers').decode('utf-8'),
        'directors': get_data('directors').decode('utf-8')}),
        markup, movie_poster)
