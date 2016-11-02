# coding: utf-8
import contextlib
import gzip
import json
import urllib2
from StringIO import StringIO
from datetime import datetime
import settings
from fb_bot.fb_api_wrapper import construct_message_with_attachment
from fb_bot.fb_api_wrapper import construct_message_with_text
from fb_bot.movie_info import get_movie_poster, get_movie_trailer_link


def construct_film_info(poster, description, trailer_url, movie):
    my_id = 'kinohod_id' if 'kinohod_id' in movie else 'id'
    if not trailer_url and not poster:
        f_info = {
            'title': settings.uncd(movie['title']),
            'subtitle': description,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Сеансы',
                    'payload': 'seances{}'.format(movie[my_id])
                },
                {
                    'type': 'postback',
                    'title': 'Подробнее',
                    'payload': 'info{}'.format(movie[my_id])
                }
            ]
        }
    elif not trailer_url and poster:
        f_info = {
            'title': settings.uncd(movie['title']),
            'image_url': poster,
            'subtitle': description,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Сеансы',
                    'payload': 'seances{}num{}'.format(movie[my_id], 0)
                },
                {
                    'type': 'postback',
                    'title': 'Подробнее',
                    'payload': 'info{}'.format(movie[my_id])
                },

            ]
        }
    else:
        f_info = {
            'title': settings.uncd(movie['title']),
            'image_url': poster,
            'subtitle': description,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Сеансы',
                    'payload': 'seances{}num{}'.format(movie[my_id], 0)
                },
                {
                    'type': 'web_url',
                    'url': trailer_url,
                    'title': 'Трейлер'
                },
                {
                    'type': 'postback',
                    'title': 'Подробнее',
                    'payload': 'info{}'.format(movie[my_id])
                },

            ]
        }

    return f_info


def _construct_premiere_info(poster, description, trailer_url, movie):
    my_id = 'kinohod_id' if 'kinohod_id' in movie else 'id'
    if not trailer_url or not poster:
        p_info = {
            'title': settings.uncd('Премьера: {}'.decode('utf-8').
                                   format(movie['title'])),
            'subtitle': description,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Подробнее',
                    'payload': 'info{}'.format(movie[my_id])
                }
            ]

        }
    else:
        p_info = {
            'title': settings.uncd('Премьера: {}'.decode('utf-8')
                                   .format(movie['title'])),
            'image_url': poster,
            'subtitle': description,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Сеансы',
                    'payload': 'seances{}num{}'.format(movie[my_id], 0)
                },
                {
                    'type': 'web_url',
                    'url': trailer_url,
                    'title': 'Трейлер'
                },
                {
                    'type': 'postback',
                    'title': 'Подробнее',
                    'payload': 'info{}'.format(movie[my_id])
                }
            ]
        }

    return p_info


def construct_final_payload(recipient_id, movies, n_movies):
    quick_replies = [
        {
            'content_type': 'text',
            'title': 'Ещё фильмы',
            'payload': '/running{}'.format(n_movies)
        }
    ]
    payload = construct_message_with_attachment(
        recipient_id, movies, quick_replies
    )
    return payload


def _construct_out_of_films_payload(recipient_id, movies):
    if len(movies) > 0:
        quick_replies = [
            {
                'content_type': 'text',
                'title': 'В начало',
                'payload': '/running{}'.format(
                    settings.FB_FILMS_TO_DISPLAY
                )
            }
        ]
        payload = construct_message_with_attachment(
            recipient_id, movies, quick_replies
        )
    else:
        text = 'Фильмов больше нет.',
        quick_replies = [
            {
                'content_type': 'text',
                'title': 'В начало',
                'payload': '/running{}'.format(
                    settings.FB_FILMS_TO_DISPLAY)
            }
        ]
        payload = construct_message_with_text(
            recipient_id, text, quick_replies
        )
    return payload


def display_running_movies(recipient_id, number_of_movies, only_on_scr=False):
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    videos, premiers = [], []
    for film_counter in xrange(number_of_movies - settings.FB_FILMS_TO_DISPLAY,
                               number_of_movies):
        if film_counter < len(data):
            movie = data[film_counter]
            # description, poster,
            # trailer_url = display_movie_info(movie['id'])
            description = poster = trailer_url = ''
            if 'annotationShort' in movie:
                description = movie['annotationShort']

            if ('posterLandscape' in movie and
                    'name' in movie['posterLandscape']):
                poster = get_movie_poster(movie['posterLandscape']['name'])

            if ('trailers' in movie and
                    isinstance(movie['trailers'], list) and
                    len(movie['trailers']) > 0 and
                    'source' in movie['trailers'][0] and
                    'filename' in movie['trailers'][0]['source']):
                trailer_url = get_movie_trailer_link(
                    movie['trailers'][0]['source']['filename']
                )
            if movie['premiereDateRussia']:
                prem_date = datetime.strptime(movie['premiereDateRussia'],
                                              '%Y-%m-%d')
                if prem_date > datetime.now():
                    if only_on_scr:
                        continue
                    p_info = _construct_premiere_info(poster, description,
                                                      trailer_url, movie)
                    premiers.append(p_info)
                else:
                    f_info = construct_film_info(poster, description,
                                                 trailer_url, movie)
                    videos.append(f_info)
            else:
                if only_on_scr:
                    continue
                p_info = _construct_premiere_info(poster, description,
                                                  trailer_url, movie)
                premiers.append(p_info)

        else:
            movies = premiers + videos
            payload = json.dumps(
                _construct_out_of_films_payload(
                    recipient_id, movies
                )
            )
            return payload

    movies = premiers + videos
    payload = json.dumps(
        construct_final_payload(
            recipient_id, movies, number_of_movies +
            settings.FB_FILMS_TO_DISPLAY
        )
    )
    return payload
