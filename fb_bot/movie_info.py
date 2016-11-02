# coding: utf-8
import contextlib
import json
import urllib2

import settings
from fb_bot.helper_methods import get_movie_poster, get_movie_trailer_link


def display_movie_info(movie_id):

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

    link = 'http://kinohod.ru/widget/movies?ids={}'.format(movie_id)
    try:
        horizontal_poster = ((json.loads(urllib2.urlopen(link).read()))['data']
                             [0]['posterLandscape']['name'])
        movie_poster = get_movie_poster(horizontal_poster)
    except:
        movie_poster = get_movie_poster(html_data['poster'])

    if ('trailers' in html_data and isinstance(html_data['trailers'], list) and
            len(html_data) > 0 and 'mobile_mp4' in html_data['trailers'][0]):
        kinohod_trailer_hash = (html_data['trailers'][0]
                                ['mobile_mp4']['filename'])
        trailer_url = get_movie_trailer_link(kinohod_trailer_hash)
    else:
        trailer_url = ''

    return html_data['annotationShort'], movie_poster, trailer_url


def display_full_movie_info(movie_id):

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

    movie_poster = get_movie_poster(html_data['poster'])

    if ('trailers' in html_data and isinstance(html_data['trailers'], list) and
            len(html_data) > 0 and 'mobile_mp4' in html_data['trailers'][0]):
        kinohod_trailer_hash = (html_data['trailers'][0]
                                ['mobile_mp4']['filename'])
        trailer_url = get_movie_trailer_link(kinohod_trailer_hash)
    else:
        trailer_url = ''

    title = html_data.get('title')
    annotation = html_data.get('annotationFull')
    duration = html_data.get('duration')
    genres = html_data.get('genres')
    if 'actors' in html_data and html_data.get('actors'):
        actors = html_data.get('actors')[0:3]
    else:
        actors = html_data.get('actors')
    producers = html_data.get('producers')
    directors = html_data.get('directors')
    age_restriction = html_data.get('ageRestriction')
    return (movie_poster, trailer_url, title, annotation, duration, genres,
            actors,
            producers, directors, age_restriction)
