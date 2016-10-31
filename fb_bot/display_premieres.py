# coding: utf-8
import contextlib
import json
import urllib2

import settings
from fb_bot.fb_api_wrapper import construct_message_with_attachment, \
    construct_message_with_text
from fb_bot.movie_info import get_movie_poster, get_movie_trailer_link


def get_data(url):
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        return json.loads(jf.read())


def _construct_final_payload(recipient_id, movies, n_movies):
    quick_replies = [
        {
            'content_type': 'text',
            'title': 'Ещё фильмы',
            'payload': '/premiere{}'.format(n_movies)
        }
    ]
    payload = construct_message_with_attachment(
        recipient_id, movies, quick_replies
    )
    return payload


def _construct_film_info(poster, description, trailer_url, movie):
    if 'kinohod_id' in movie:
        my_id = 'kinohod_id'
    else:
        my_id = 'id'
    if not trailer_url or not poster:
        f_info = {
            'title': settings.uncd(movie['title']),
            'subtitle': description,
            'buttons': [
                {
                    'type': 'postback',
                    'title': 'Сеансы',
                    'payload': 'seances{}'.format(movie[my_id])
                }
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


def _construct_out_of_films_payload(recipient_id, movies):
    if len(movies) > 0:

        quick_replies = [
            {
                'content_type': 'text',
                'title': 'В начало',
                'payload': '/premiere{}'.format(
                    settings.FB_FILMS_TO_DISPLAY
                )
            }
        ]
        payload = construct_message_with_attachment(
            recipient_id, movies, quick_replies
        )
    else:
        text = settings.NO_MORE_FILMS
        quick_replies = [
            {
                'content_type': 'text',
                'title': 'В начало',
                'payload': '/premiere{}'.format(
                    settings.FB_FILMS_TO_DISPLAY
                )
            }
        ]
        payload = construct_message_with_text(
            recipient_id, text, quick_replies
        )
    return payload


def display_premieres(recipient_id, number_of_movies):

    url = settings.URL_PREMIERES.format(
        settings.KINOHOD_API_KEY
    )
    html_data = get_data(url)
    videos = []
    for film_counter in xrange(number_of_movies - settings.FB_FILMS_TO_DISPLAY,
                               number_of_movies):
        if film_counter < len(html_data):
            movie = html_data[film_counter]
            genres_str = poster = trailer_url = ''
            if 'genres' in movie:
                genres_str = ', '.join([g for g in movie['genres']])
            description = 'Жанр: {}'.decode('utf-8').format(genres_str)
            if 'poster' in movie:
                poster = get_movie_poster(movie['poster'])
            if ('trailers' in movie and
                    isinstance(movie['trailers'], list) and
                    len(html_data) > 0 and 'mobile_mp4' in
                    movie['trailers'][0]):
                trailer_url = (movie['trailers'][0]
                                    ['mobile_mp4']['filename'])
            trailer_url = get_movie_trailer_link(trailer_url)
            f_info = _construct_film_info(
                poster, description, trailer_url, movie
            )

            videos.append(f_info)

        else:
            movies = videos
            payload = json.dumps(
                _construct_out_of_films_payload(
                    recipient_id, movies
                )
            )
            return payload

    movies = videos[0:10]
    payload = json.dumps(
        _construct_final_payload(
            recipient_id, movies, number_of_movies +
            settings.FB_FILMS_TO_DISPLAY
        )
    )
    return payload
