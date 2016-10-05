# coding: utf-8

import contextlib
import urllib2
import json

from telepot.namedtuple import InlineKeyboardMarkup

from model.base import get_model
from model.base import UserProfile
from model.film import Film

import settings


def empty_data(html_data):
    if not html_data:
        template = settings.JINJA_ENVIRONMENT.get_template('no_seances.md')
        return template.render({})


def gen_markup(movie_id, number_of_seances):
    return InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data=(
                  '/seance{}num{}'.format(
                      movie_id,
                      (number_of_seances + settings.SEANCES_TO_DISPLAY)
                  )
              ))
         ]]
    )


def get_data(url):
    try:
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            return json.loads(jf.read())
    except Exception:
        return None


def get_seances(chat_id, movie_id, number_of_seances):

    u = get_model(UserProfile, chat_id)

    f = Film.get_by_id(str(movie_id))
    if f and not f.cinemas:
        return settings.NO_FILM_SEANCE

    cinemas = [k.get() for k in f.cinemas]
    cinema_ids = [c.kinohod_id for c in cinemas]

    if u:
        l = json.loads(u.location)
        latitude, longitude = l['latitude'], l['longitude']

        url = '{}?lat={}&long={}&sort=distance&cityId=1'.format(
            settings.URL_WIDGET_CINEMAS,
            latitude,
            longitude,
        )

        seances = []

        html_data = get_data(url)

        if not html_data:
            return settings.DONT_UNDERSTAND, None

        if 'data' not in html_data:
            return settings.CANNOT_FIND_SEANCE, None

        for info in html_data['data']:

            cinema_id = info.get('id')

            if str(cinema_id) not in cinema_ids:
                continue

            seances.append(
                settings.RowDist(
                    settings.uncd(info['shortTitle']),
                    info['distance'],
                    '(/c{}m{})'.format(cinema_id, movie_id)
                )
            )

        if len(seances) < 1:
            return settings.NO_FILM_SEANCE, None

        correct, n = False, settings.SEANCES_TO_DISPLAY
        while not correct:
            if len(seances) > number_of_seances:
                n = settings.SEANCES_TO_DISPLAY
                seances = seances[number_of_seances - n: number_of_seances]
                correct = True
            elif len(seances) > (number_of_seances - n):
                seances = seances[number_of_seances - n:]
                correct = True
            else:
                number_of_seances = n

        empty_data(html_data=html_data)
        mark_up = gen_markup(movie_id, number_of_seances)
        template = settings.JINJA_ENVIRONMENT.get_template(
            'seances_distance.md'
        )

    else:

        url = settings.URL_SEANCES.format(
            str(movie_id), settings.KINOHOD_API_KEY,
            (number_of_seances - settings.SEANCES_TO_DISPLAY),
            number_of_seances
        )

        seances = []
        html_data = get_data(url)

        if not html_data:
            return settings.DONT_UNDERSTAND, None

        for info in html_data:

            cinema_json = info.get('cinema')
            cinema_id = cinema_json.get('id')
            if str(cinema_id) not in cinema_ids:
                continue

            seances.append(
                settings.Row(settings.uncd(cinema_json['shortTitle']),
                             '(/c{}m{})'.format(cinema_id,
                                                info['movie']['id']))
            )

        empty_data(html_data=html_data)
        mark_up = gen_markup(movie_id, number_of_seances)
        template = settings.JINJA_ENVIRONMENT.get_template('seances.md')

    return template.render({
        'sign_tip': settings.SIGN_TIP,
        'seances': seances
    }), mark_up


def display_seances_part(text, movie_id, number_of_seances):

    url = settings.URL_FULL_SEANCES.format(
        str(movie_id), settings.KINOHOD_API_KEY,
    )

    seances = []

    f = Film.get_by_id(str(movie_id))
    if f and not f.cinemas:
        return settings.NO_FILM_SEANCE

    cinemas = [k.get() for k in f.cinemas]
    cinema_ids = [c.kinohod_id for c in cinemas]

    html_data = get_data(url)

    if not html_data:
        return settings.DONT_UNDERSTAND

    for info in html_data:

        cinema_json = info.get('cinema')
        cinema_id = cinema_json.get('id')

        if cinema_id not in cinema_ids:
            continue

        if (('shortTitle' in cinema_json and
                cinema_json['shortTitle'].find(text) > -1) or
            ('address' in info['cinema'] and
                cinema_json['address'].find(text) > -1) or
            ('subway_stations' in cinema_json and
                'name' in cinema_json['subway_stations'] and
                cinema_json['subway_stations']['name'].find(text) > -1)):

            seances.append(
                settings.Row(cinema_json['shortTitle'],
                             '(/c{}m{})'.format(cinema_json['id'],
                                                info['movie']['id']))
            )

    empty_data(html_data=html_data)
    if len(seances) < 1:
        template = settings.JINJA_ENVIRONMENT.get_template('no_seances.md')
        return template.render({})

    correct, n = False, settings.SEANCES_TO_DISPLAY
    while not correct:
        if len(seances) > number_of_seances:
            n = settings.SEANCES_TO_DISPLAY
            seances = seances[number_of_seances - n: number_of_seances]
            correct = True
        elif len(seances) > (number_of_seances - n):
            seances = seances[number_of_seances - n:]
            correct = True
        else:
            number_of_seances = n

    template = settings.JINJA_ENVIRONMENT.get_template('seances.md')

    return template.render({
        'sign_tip': settings.SIGN_TIP,
        'seances': seances
    })
