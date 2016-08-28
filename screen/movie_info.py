# coding: utf-8

import contextlib
import urllib2
import json

from telepot.namedtuple import InlineKeyboardMarkup, KeyboardButton

import botan
import settings


def _get_movie_trailer_link(trailer_hash):
    ab, cd = trailer_hash[0:2], trailer_hash[2:4]
    url = '{}{}/{}/{}'.format(settings.URL_BASE_O, ab, cd, trailer_hash)
    return url


def _get_movie_poster(poster_hash):
    ab, cd = poster_hash[0:2], poster_hash[2:4]
    url = '{}{}/{}/{}'.format(settings.URL_BASE_O, ab, cd, poster_hash)
    poster = urllib2.urlopen(url)
    return poster


def display_movie_info(movie_id, telegram_user_id):

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

    movie_poster = _get_movie_poster(html_data['poster'])
    if 'trailers' in html_data and 'mobile_mp4' in html_data['trailers'][0]:
        kinohod_trailer_hash = (html_data['trailers'][0]
                                ['mobile_mp4']['filename'])
        trailer_url = _get_movie_trailer_link(kinohod_trailer_hash)
        shorten_url = botan.shorten_url(trailer_url, settings.BOTAN_TOKEN,
                                        telegram_user_id)
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text=settings.TREILER, url=shorten_url),
            dict(text=settings.CHOOSE_SEANCE,
                 callback_data=('/seance{}num{}'.format(
                     html_data['id'], settings.CINEMAS_TO_DISPLAY))),
        ]])
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            dict(text=settings.CHOOSE_SEANCE,
                 callback_data=('/seance{}num{}'.format(html_data['id'], 20)))
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
            markup, movie_poster
    )
