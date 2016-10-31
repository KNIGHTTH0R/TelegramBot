# coding: utf-8
import json
import urllib
from google.appengine.api import mail

from google.appengine.ext import deferred

import settings

from fb_bot.cinema_seances import display_cinema_seances_short
from fb_bot.cinema_seances import display_cinema_seances
from fb_bot.display_premieres import display_premieres

from fb_bot.helper_methods import get_data, get_by_recipient_id

from fb_bot.movie_info import display_movie_info, display_full_movie_info

from fb_bot.nearest_cinemas import construct_cinema_generic, contruct_cinemas
from fb_bot.nearest_cinemas import display_nearest_cinemas
from fb_bot.nearest_cinemas import display_cinema_schedule

from fb_bot.running_movies import construct_final_payload, construct_film_info
from fb_bot.running_movies import display_running_movies

from fb_bot.support_script import support_message_generator,  support_dict
from fb_bot.support_words import NO_AGAIN_CALLBACK
from fb_bot.support_words import NO_MAIL_SENDED_CALLBACK
from fb_bot.support_words import ANOTHER_PAY_ER_CALLBACK, support_a

from fb_bot.welcome_buttons import display_welcome_buttons

from validate_email import validate_email

from processing.parser import Parser

from datetime import datetime


def _construct_payload(message, recipient_id):
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message
        }
    }
    payload = json.dumps(payload)
    return payload


def _construct_button_payload(recipient_id, text, buttons):

    discount_payload = {
      'recipient': {
        'id': recipient_id
      },
      'message': {
        'attachment': {
          'type': 'template',
          'payload': {
            'template_type': 'button',
            'text': text,
            'buttons': buttons
          }
        }
      }
    }
    return json.dumps(discount_payload)


def _construct_picture_link_payload(recepient_id, image_link):

    payload = {
        'recipient': {
            'id': recepient_id
        },
        'message': {
            'attachment': {
                'type': 'image',
                'payload': {
                    'url': image_link
                }
            }
        }
    }
    return json.dumps(payload)


def _construct_get_geo_payload(recipient_id):

    message = settings.SHARE_YOUR_GEO

    payload = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message,
            'quick_replies': [
                {
                    'content_type': 'location'
                }

            ]
        }
    }

    payload = json.dumps(payload)
    return payload


def _construct_cinema_movie_generic(cinema, movie_id):
    my_id = 'kinohod_id' if 'kinohod_id' in cinema else 'id'

    stations_str = ', '.join(
        map(lambda x: x.get('name', ''), cinema.get('subway_stations'))
    ) if 'subway_stations' in cinema else ''

    button = {
        'type': 'postback',
        'title': 'Сеансы',
        'payload': '/c{}m{}d{}'.format(cinema[my_id], movie_id,
                                       settings.TODAY)
    }
    c_info = {
        'title': cinema['shortTitle'],
        'subtitle': u'{}\n{}'.format(settings.uncd(cinema
                                                   ['address']),
                                     settings.uncd(stations_str)),
        'buttons': [button]
    }
    return c_info


def send_email(user_email, last_callback):
    if last_callback in support_a:
        stack_trace = support_a[last_callback]
        send_to = 'support@kinohod.ru'
    else:
        stack_trace = last_callback
        send_to = 'bottelegram@kinohod.ru'
    try:
        text = settings.de_uncd('Email: {} \n {}').format(
            user_email, stack_trace
        )
    except:
        text = 'Email: {} \n {}'.decode('utf-8').format(
            user_email, stack_trace
        )
    mail.send_mail(sender='michaelborisovha@gmail.com',
                   to=send_to,
                   # to='myuborisov@gmail.com',
                   subject='Need support, Info from Facebook bot',
                   body=text)


def update_last_callback(recipient_id):
    u_info = get_by_recipient_id(recipient_id)
    u_info.last_callback = ''
    u_info.put()


def construct_movies_list(html):
    movies = []
    for f in html:
        (description, poster, trailer_url) = display_movie_info(f['id'])
        f_info = construct_film_info(poster, description, trailer_url, f)
        movies.append(f_info)
    return movies


def handle_text_message(recipient_id, message):
    search_dict = {
        'search': message.encode('utf-8')
    }
    url_encoded_dict = urllib.urlencode(search_dict)
    query_url = settings.QUERY_SEARCH_URL.format(
        settings.KINOHOD_API_KEY, url_encoded_dict
    )

    film_kinohod_api = get_data(query_url)

    query_url_soon = query_url + '&filter=soon'
    film_kinohod_api_soon = get_data(query_url_soon)

    if film_kinohod_api:
        movies = construct_movies_list(film_kinohod_api)
        payload = json.dumps(
            construct_final_payload(
                recipient_id, movies, settings.FB_FILMS_TO_DISPLAY
            )
        )

        return payload

    elif film_kinohod_api_soon:
        movies = construct_movies_list(film_kinohod_api_soon)
        payload = json.dumps(
            construct_final_payload(
                recipient_id, movies, settings.FB_FILMS_TO_DISPLAY
            )
        )
        return payload

    else:

        parser = Parser(message.encode('utf-8'), 'base')
        parser.parse()
        film = parser.data.what
        if not film:
            parser.parser_special()
            film = parser.data.genre
        place = parser.data.place
        if film:
            movies = []

            for f in film:
                if not isinstance(f, dict):
                    f = f.to_dict()
                my_id = 'kinohod_id' if 'kinohod_id' in f else 'id'

                # if f.get('cinemas'):
                (description, poster, trailer_url) = display_movie_info(
                    f[my_id]
                )
                f_info = construct_film_info(
                    poster, description, trailer_url, f
                )
                movies.append(f_info)
                # else:
                #     continue

            if len(movies) == 0:
                res = _construct_payload(
                    settings.SORRY_FOUND_NOTHING, recipient_id
                )
                return res
            payload = json.dumps(
                construct_final_payload(
                    recipient_id, movies, settings.FB_FILMS_TO_DISPLAY
                )
            )
            return payload

        elif place:

            place = parser.data.place
            cinemas = []
            for c in place:
                c_info = construct_cinema_generic(
                    c.to_dict(), recipient_id
                )
                cinemas.append(c_info)
            payload = contruct_cinemas(
                recipient_id, cinemas, 10
            )
            payload = json.dumps(payload)
            return payload

        else:
            payload = _construct_payload(
                settings.SORRY_I_DONT_UNDERSTAND, recipient_id
            )
            return payload


def handle_text_with_payload(u_info, recipient_id, payload, message):
    if payload.startswith('/c'):
        seance_date = Parser.detect_time(
            message.encode('utf-8')
        )
        index_of_m, index_of_d = (payload.index('m'), payload.index('d'))
        cinema_id = payload[2:index_of_m]
        movie_id = (payload[index_of_m + 1:index_of_d])
        payloads = display_cinema_seances(
            recipient_id, cinema_id, movie_id, seance_date
        )

        text = _construct_payload(settings.DISCOUNT, recipient_id)
        update_last_callback(recipient_id)
        return [text] + payloads

    elif payload.startswith('seances'):
        if 'num' in payload:
            i_n = payload.index('num')
        else:
            return
        movie_id = payload[len('seances'):i_n]
        parser = Parser(message.encode('utf-8'), 'cinema')
        parser.parse()
        data = parser.data.place
        cinemas = []
        if not data:
            res = _construct_payload(
                'К сожалению, мы ничего не нашли',
                recipient_id
            )
            return res
        for c in data:
            if not isinstance(c, dict):
                c = c.to_dict()

            c_info = _construct_cinema_movie_generic(
                c, movie_id
            )
            cinemas.append(c_info)
        payload = contruct_cinemas(
            recipient_id, cinemas, 10
        )
        payload = json.dumps(payload)
        update_last_callback(recipient_id)
        return payload

    elif payload.startswith('s_short'):
        seance_date = Parser.detect_time(
            message.encode('utf-8')
        )
        i_d = payload.index('d')
        movie_id = payload[len('s_short'):i_d]

        if u_info and u_info.cur_lat and u_info.cur_lng:
            payload = display_cinema_seances_short(
                recipient_id, movie_id, lat=u_info.cur_lat,
                lng=u_info.cur_lng, date=seance_date.date()
            )
        else:
            payload = display_cinema_seances_short(
                recipient_id, movie_id, date=seance_date.date()
            )
        return payload

    elif payload == 'bug':
        if len(message) > 2:
            u_info.bug_description = message
            u_info.last_callback = 'bug_email'
            u_info.put()

            resp = _construct_payload(
                'Введите ваш email', recipient_id
            )
            return resp

        else:
            resp = _construct_payload(
                'Опишите проблему', recipient_id
            )
            return resp

    elif validate_email(settings.uncd(message)):
        email = settings.uncd(message)
        u_info = get_by_recipient_id(recipient_id)

        if (u_info.last_callback == NO_AGAIN_CALLBACK or
           u_info.last_callback == NO_MAIL_SENDED_CALLBACK or
           u_info.last_callback == ANOTHER_PAY_ER_CALLBACK):
            last_callback = u_info.last_callback
            deferred.deffer(send_email, email, last_callback)
            our_spec = 'Наш специалист скоро свяжется с Вами'
            payload = _construct_payload(
                our_spec, recipient_id
            )

            return payload

        elif u_info.last_callback == 'bug_email':
            deferred.defer(send_email, email, u_info.bug_description)
            our_spec = 'Спасибо :)'
            payload = _construct_payload(
                our_spec, recipient_id
            )
            return payload

        else:
            payload = _construct_payload(
                settings.SORRY_I_DONT_UNDERSTAND,
                recipient_id)
            return payload

    else:
        payload = handle_text_message(recipient_id, message)
        return payload


def handle_attachments(event):

    recipient_id = int(event['sender']['id'])
    try:
        lat = (event['message']['attachments'][0]
               ['payload']['coordinates']['lat'])
        lng = (event['message']['attachments'][0]
               ['payload']['coordinates']['long'])
        u_info = get_by_recipient_id(recipient_id)
        u_info.cur_lat = float(lat)
        u_info.cur_lng = float(lng)
        u_info.put()
        back_payload = u_info.last_callback
        if back_payload and back_payload.startswith('seances'):
            if back_payload.find('num') != -1:
                i_n, l_n = back_payload.index('num'), len('num')
                movie_id = back_payload[len('seances'):i_n]
                starting_n = (back_payload[i_n + l_n:
                                           len(back_payload)])
            else:
                movie_id = back_payload[len('seances'):]
                starting_n = 0
            u_info = get_by_recipient_id(recipient_id)
            payload = display_cinema_seances_short(recipient_id,
                                                   movie_id,
                                                   starting_n,
                                                   u_info.cur_lat,
                                                   u_info.cur_lng)
            return payload
        else:
            message = 'Ваши геоданные были успешно изменены'
            payload = _construct_payload(message, recipient_id)
            return payload
    except Exception:
        message = settings.SORRY_DONT_PROCEED
        payload = _construct_payload(message, recipient_id)
        return payload


def handle_quick_reply(payload, recipient_id):
    if payload.startswith('/running'):
        n_movies = int(payload[len('/running'):len(payload)])
        return display_running_movies(recipient_id, n_movies)

    elif payload.startswith('/premiere'):
        n_movies = int(payload[len('/premiere'):len(payload)])
        return display_premieres(recipient_id, n_movies)

    elif payload.startswith('/c'):
        index_of_m, index_of_d = (payload.index('m'), payload.index('d'))
        cinema_id = payload[2:index_of_m]
        movie_id, d = (
            payload[index_of_m + 1:index_of_d], payload[-1]
        )
        if not d.isdigit():
            return

        if int(d) == settings.ANOTHER_FB_DAY:
            u_info = get_by_recipient_id(recipient_id)
            u_info.last_callback = payload
            u_info.put()

            message = settings.TELL_DATE
            return _construct_payload(message, recipient_id)
        else:
            payloads = display_cinema_seances(
                recipient_id, cinema_id, movie_id, d
            )
            text = _construct_payload(settings.DISCOUNT, recipient_id)
            return [text] + payloads

    elif payload.startswith('seances'):
        i_d = payload.index('d')
        i_n, l_n = payload.index('num'), len('num')
        movie_id = payload[len('seances'):i_n]
        starting_n = payload[i_n + l_n:i_d]
        date = datetime.strptime(payload[i_d + 1: len(payload)], '%Y-%m-%d')

        u_info = get_by_recipient_id(recipient_id)

        if not u_info or not u_info.cur_lat or not u_info.cur_lng:
            payload = display_cinema_seances_short(
                recipient_id, movie_id, starting_n, date=date
            )
        elif u_info.cur_lat and u_info.cur_lat:
            payload = display_cinema_seances_short(
                recipient_id, movie_id, starting_n, u_info.cur_lat,
                u_info.cur_lng, date=date
            )
        return payload

    elif payload == 'refuse_geo':
        update_last_callback(recipient_id)
        u_info = get_by_recipient_id(recipient_id)
        movie_id = u_info.cur_movie_id

        payload = display_cinema_seances_short(
            recipient_id, movie_id, 0
        )
        return payload

    elif payload.startswith('nearest'):
        number = int(payload[len('nearest'): len(payload)])
        u_info = get_by_recipient_id(recipient_id)
        u_info.last_callback = payload
        # movie_id = u_info.cur_movie_id dg
        if not u_info or not u_info.cur_lat or not u_info.cur_lng:
            payload = display_nearest_cinemas(
                recipient_id, number
            )
        elif u_info.cur_lat and u_info.cur_lng:
            payload = display_nearest_cinemas(
                recipient_id, number, lat=u_info.cur_lat, lng=u_info.cur_lng
            )
        text = _construct_payload(
            settings.CINEMA_LIST, recipient_id
        )
        u_info.put()
        return [text] + [payload]

    elif payload.startswith('cinema'):
        i_d = payload.index('d')
        i_n, l_n = payload.index('num'), len('num')
        cinema_id = payload[len('cinema'): i_n]
        starting_n = payload[i_n + l_n:i_d]
        day = payload[i_d + 1: len(payload)]
        payload = display_cinema_schedule(
            recipient_id, cinema_id, int(starting_n), day
        )

        return payload

    elif payload.startswith('s_short'):
        i_d = payload.index('d')
        u_info = get_by_recipient_id(recipient_id)
        u_info.last_callback = payload
        u_info.put()

        message = settings.TELL_DATE
        return _construct_payload(message, recipient_id)


def construct_full_movie_info(movie_id, recipient_id):
    (poster, trailer_url, title, annotation,
     duration, genres, actors,
     producers, directors, age_restriction) = display_full_movie_info(
        movie_id
    )
    payload = _construct_picture_link_payload(
        recipient_id, poster
    )
    if genres:
        genres_str = ', '.join([g for g in genres])
    else:
        genres_str = ''

    if actors:
        actors_str = ', '.join([a for a in actors])
    else:
        actors_str = ''

    if producers:
        producers_str = ', '.join([p for p in producers])
    else:
        producers_str = ''

    if directors:
        directors_str = ', '.join([d for d in directors])
    else:
        directors_str = ''

    title_annotation_full = u'{}\n\n{}'.format(title, annotation)
    title_annotation_full = title_annotation_full[0:320]
    first_message = _construct_payload(title_annotation_full, recipient_id)
    full_info = (u'Продолжительность: {}мин.\n'
                 u'Возраст: {}\n'
                 u'Жанры: {}\n'
                 u'Актёры: {}\n'
                 u'Продюсеры: {}\n'
                 u'Режисёры: {}').format(
        duration, age_restriction, genres_str,
        actors_str, producers_str, directors_str
    )
    full_info = full_info[0:320]
    return payload, first_message, full_info, trailer_url


def handle_back_payload(back_payload, recipient_id):
    if back_payload.startswith('seances'):
        payload = _construct_get_geo_payload(recipient_id)

        u_info = get_by_recipient_id(recipient_id)
        u_info.last_callback = back_payload
        u_info.put()

        return payload

    elif back_payload.startswith('/c'):
        index_of_m, index_of_d = (back_payload.index('m'),
                                  back_payload.index('d'))
        cinema_id = back_payload[2:index_of_m]
        movie_id, d = (
            back_payload[index_of_m + 1:index_of_d], back_payload[-1]
        )

        payloads = display_cinema_seances(
            recipient_id, cinema_id, movie_id, d)
        u_info = get_by_recipient_id(recipient_id)

        u_info.cur_movie_id = int(movie_id)
        u_info.cur_cinema_id = int(cinema_id)
        u_info.last_callback = 'nearest'
        u_info.put()
        text = _construct_payload(settings.DISCOUNT, recipient_id)
        return [text] + payloads

    elif (back_payload.startswith('info') and
            back_payload.find('cinema') != -1):
        movie_id = int(
            back_payload[len('info'): back_payload.find('cinema')]
        )
        cinema_id = int(
            back_payload[back_payload.find('cinema') + len('cinema'):]
        )
        (payload, first_message,
         full_info, trailer_url) = construct_full_movie_info(
            movie_id, recipient_id
        )
        if trailer_url:
            buttons = [
                {
                    'type': 'web_url',
                    'url': trailer_url,
                    'title': 'Трейлер'
                },
                {
                    "type": "postback",
                    "title": "Сеансы",
                    "payload": "/c{}m{}d{}".format(
                        cinema_id, movie_id, settings.TODAY
                    )
                },
            ]
        else:
            buttons = [
                {
                    "type": "postback",
                    "title": "Сеансы",
                    "payload": "/c{}m{}d{}".format(
                        cinema_id, movie_id, settings.TODAY
                    )
                }
            ]
        buttons = _construct_button_payload(
            recipient_id, full_info, buttons
        )

        return [payload] + [first_message] + [buttons]

    elif back_payload.startswith('info'):
        movie_id = int(back_payload[len('info'):])
        (payload, first_message,
         full_info, trailer_url) = construct_full_movie_info(
            movie_id, recipient_id
        )

        if trailer_url:
            buttons = [
                {
                    'type': 'web_url',
                    'url': trailer_url,
                    'title': 'Трейлер'
                },
                {
                    "type": "postback",
                    "title": "Сеансы",
                    "payload": "seances{}num{}".format(movie_id, 0)
                },
            ]
        else:
            buttons = [
                {
                    "type": "postback",
                    "title": "Сеансы",
                    "payload": "seances{}num{}".format(movie_id, 0)
                }
            ]
        buttons = _construct_button_payload(
            recipient_id, full_info, buttons
        )
        return [payload] + [first_message] + [buttons]

    elif back_payload == 'start':
        u_info = get_by_recipient_id(recipient_id)
        u_info.put()
        payload = display_welcome_buttons(recipient_id)
        return payload

    elif back_payload.startswith('/running'):
        u_info = get_by_recipient_id(recipient_id)
        u_info.last_callback = back_payload

        u_info.cur_movie_id = None
        u_info.last_searched_movie = None
        u_info.put()
        n_movies = int(back_payload[len('/running'):])
        payload = display_running_movies(recipient_id, n_movies)
        return payload

    elif back_payload.startswith('cinema'):
        cinema_id = back_payload[len('cinema'): len(back_payload)]
        payload = display_cinema_schedule(
            recipient_id, cinema_id,
            settings.FB_FILMS_TO_DISPLAY, settings.TODAY)
        return payload

    elif back_payload.startswith('nearest'):
        number = int(
            back_payload[len('nearest'):len(back_payload)]
        )
        u_info = get_by_recipient_id(recipient_id)
        u_info.last_callback = back_payload
        u_info.cur_movie_id = None
        if not u_info or not u_info.cur_lat or not u_info.cur_lng:
            payload = display_nearest_cinemas(
                recipient_id, number
            )
        elif u_info.cur_lat and u_info.cur_lng:
            payload = display_nearest_cinemas(
                recipient_id, number, lat=u_info.cur_lat, lng=u_info.cur_lng
            )
        text = _construct_payload(settings.WE_OFFER_LIST, recipient_id)

        u_info.put()
        return [text] + [payload]

    elif back_payload == 'bug':
        u_info = get_by_recipient_id(recipient_id)
        u_info.last_callback = back_payload
        u_info.put()

        return _construct_payload(
            settings.DESCRIBE_YOUR_PROBLEM, recipient_id
        )

    else:
        payload = support_message_generator(
            int(recipient_id), back_payload, support_dict
        )
        if not payload:
            return
        else:
            return payload
