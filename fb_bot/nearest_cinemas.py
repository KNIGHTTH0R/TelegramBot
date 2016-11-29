# coding: utf-8
import json
from datetime import datetime, timedelta
import settings
from data import detect_city_id_by_location
from fb_bot.cinema_seances import get_data
from fb_bot.fb_api_wrapper import construct_message_with_attachment
from fb_bot.fb_api_wrapper import construct_message_with_text
from fb_bot.helper_methods import get_movie_poster, get_movie_trailer_link
from model.base import UserProfile


def _construct_film_info(poster, description, trailer_url,
                         movie, cinema_id, day):

    if not trailer_url or not poster:
        f_info = {
            "title": settings.uncd(movie['title']),
            "subtitle": description,
            "buttons": [
                {
                    "type": "postback",
                    "title": "Сеансы",
                    "payload": "/c{}m{}d{}".format(
                        cinema_id, movie['id'], day
                    )
                }
            ]
        }
    else:
        f_info = {
            "title": settings.uncd(movie['title']),
            "image_url": poster,
            "subtitle": description,
            "buttons": [
                {
                    "type": "web_url",
                    "url": trailer_url,
                    "title": "Трейлер"
                },
                {
                    "type": "postback",
                    "title": "Сеансы",
                    "payload": "/c{}m{}d{}".format(cinema_id, movie['id'],
                                                   day)
                },
                {
                    "type": "postback",
                    "title": "Подробнее",
                    "payload": "info{}cinema{}".format(movie['id'], cinema_id)
                },
            ]
        }

    return f_info


def _construct_final_payload(cinema_id, recipient_id, movies, n_movies, day):
    quick_replies = [
        {
            "content_type": "text",
            "title": "Ещё фильмы",
            "payload": "cinema{}num{}d{}".format(
                cinema_id, n_movies, day
            )
        }
    ]
    payload = construct_message_with_attachment(
        recipient_id, movies, quick_replies
    )
    return payload


def construct_cinema_generic(cinema, recipient_id=None):
    if 'kinohod_id' in cinema:
        my_key = 'kinohod_id'
    else:
        my_key = 'id'
    if recipient_id:
        u_info = (UserProfile.query(UserProfile.facebook_id ==
                                    recipient_id).get())
        if u_info and u_info.cur_movie_id:
            button = {
                'type': 'postback',
                'title': 'Сеансы',
                'payload': '/c{}m{}d{}'.format(cinema[my_key],
                                               u_info.cur_movie_id,
                                               settings.TODAY)
                }
        else:
            button = {
                'type': 'postback',
                'title': 'Расписание',
                'payload': 'cinema{}'.format(cinema[my_key])
            }
    else:
        button = {
            'type': 'postback',
            'title': 'Расписание',
            'payload': 'cinema{}'.format(cinema[my_key])
        }

    stations_str = ', '.join(
        map(lambda x: x.get('name', ''), cinema.get('subway_stations'))
    ) if 'subway_stations' in cinema else ''

    if cinema.get('mall'):
        subtitle = u'Адрес: {}\n{}\nМетро: {}'.format(
            settings.uncd(cinema['address']),
            settings.uncd(cinema['mall']),
            settings.uncd(stations_str)
        )

    else:
        subtitle = u'Адрес: {}\nМетро: {}'.format(
            settings.uncd(cinema['address']),
            settings.uncd(stations_str)
        )

    c_info = {
        'title': cinema['shortTitle'],
        'subtitle': subtitle,
        'buttons': [button]
    }
    return c_info


def contruct_cinemas(recipient_id, cinemas, number):
    quick_replies = [
        {
            'content_type': 'text',
            'title': 'Другие кинотеатры',
            'payload': 'nearest{}'.format(number)
        },
    ]
    payload = construct_message_with_attachment(
        recipient_id, cinemas, quick_replies
    )

    return payload


def _construct_out_of_films_payload(cinema_id, recipient_id, movies, day):
    if len(movies) > 0:
        quick_replies = [
            {
                "content_type": "text",
                "title": "В начало",
                "payload": "cinema{}num{}d{}".format(
                    cinema_id, settings.FB_FILMS_TO_DISPLAY, int(day) - 1
                )
            },
            {
                "content_type": "text",
                "title": "Следующий день",
                "payload": "cinema{}num{}d{}".format(
                    cinema_id, settings.FB_FILMS_TO_DISPLAY, day
                )
            }

        ]
        payload = construct_message_with_attachment(
            recipient_id, movies, quick_replies
        )
    else:
        quick_replies = [
            {
                "content_type": "text",
                "title": "В начало",
                "payload": "cinema{}num{}d{}".format(
                    cinema_id, settings.FB_FILMS_TO_DISPLAY, int(day) - 1
                )
            },
            {
                "content_type": "text",
                "title": "Следующий день",
                "payload": "cinema{}num{}d{}".format(
                    cinema_id, settings.FB_FILMS_TO_DISPLAY, int(day)
                )
            }

        ]
        text = 'Фильмов больше нет.'
        payload = construct_message_with_text(
            recipient_id, text, quick_replies
        )
    return payload


def display_nearest_cinemas(recipient_id, number,
                            lat=0.0, lng=0.0,
                            movie_id=None):

    number = int(number)
    if lat == 0.0 and lng == 0.0:
        url = settings.URL_CINEMAS.format(
            settings.KINOHOD_API_KEY
        )
    else:
        l = {'latitude': lat, 'longitude': lng}
        city_id = detect_city_id_by_location(l)
        url = (settings.URL_CINEMAS_GEO + '&city={}').format(
            settings.KINOHOD_API_KEY, lat, lng, city_id
        )

    html_data = get_data(url)
    cinemas = []
    counter = 0
    for cinema in html_data:
        if counter < number:
            counter += 1
            continue
        if len(cinemas) == 10:
            break
        f_info = construct_cinema_generic(cinema, recipient_id)
        cinemas.append(f_info)
    payload = contruct_cinemas(recipient_id, cinemas, counter + 10)

    payload = json.dumps(payload)
    return payload


def _day_of_seance(day):

    def _r_day(digit):
        return '0{}'.format(digit) if int(digit) < 10 else digit

    def day_func(d):
        return '{}{}{}'.format(_r_day(d.day), _r_day(d.month), _r_day(d.year))

    return day_func(datetime.now() + timedelta(days=int(day))) if day else 0


def display_cinema_schedule(recipient_id, cinema_id, number_of_movies, day):

    if not day:
        day = 0

    url = settings.URL_CINEMA_SEANCES_SHORT.format(
        cinema_id, settings.KINOHOD_API_KEY, _day_of_seance(day)
    )
    html_data = get_data(url)
    videos = []
    for film_counter in xrange(number_of_movies - settings.FB_FILMS_TO_DISPLAY,
                               number_of_movies):
        if film_counter < len(html_data):
            movie = html_data[film_counter]['movie']
            genres_str = poster = trailer_url = ''
            if 'genres' in movie:
                genres_str = ', '.join([g for g in movie['genres']])
            description = 'Жанр: {}'.decode('utf-8').format(genres_str)
            if 'poster' in movie:
                poster = get_movie_poster(movie['poster'])
            if ('trailers' in movie and
                    isinstance(movie['trailers'], list) and
                    len(movie['trailers']) > 0 and 'mobile_mp4' in
                    movie['trailers'][0]):
                trailer_url = (movie['trailers'][0]
                                    ['mobile_mp4']['filename'])
            trailer_url = get_movie_trailer_link(trailer_url)
            f_info = _construct_film_info(poster, description,
                                          trailer_url, movie, cinema_id,
                                          day)

            videos.append(f_info)

        else:
            day = int(day) + 1
            movies = videos
            payload = json.dumps(
                _construct_out_of_films_payload(
                    cinema_id, recipient_id, movies, day
                )
            )
            return payload

    movies = videos[0:10]
    payload = json.dumps(
        _construct_final_payload(
            cinema_id, recipient_id, movies,
            number_of_movies + settings.FB_FILMS_TO_DISPLAY, day
        )
    )
    return payload
