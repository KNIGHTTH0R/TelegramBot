# coding: utf-8

import contextlib
import urllib2
import json

from telepot.namedtuple import InlineKeyboardMarkup

from model import get_user

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
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        return json.loads(jf.read())


def get_seances(chat_id, movie_id, number_of_seances):

    u = get_user(chat_id)

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

        for info in html_data['data']:
            seances.append(
                settings.RowDist(
                    settings.uncd(info['shortTitle']),
                    info['distance'],
                    '(/c{}m{})'.format(info['id'], movie_id)
                )
            )

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

        for info in html_data:
            seances.append(
                settings.Row(settings.uncd(info['cinema']['shortTitle']),
                             '(/c{}m{})'.format(info['cinema']['id'],
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
    html_data = get_data(url)
    for info in html_data:
        if (('shortTitle' in info['cinema'] and
                info['cinema']['shortTitle'].find(text) > -1) or
            ('address' in info['cinema'] and
                info['cinema']['address'].find(text) > -1) or
            ('subway_stations' in info['cinema'] and
                'name' in info['cinema']['subway_stations'] and
                info['cinema']['subway_stations']['name'].find(text) > -1)):

            seances.append(
                settings.Row(info['cinema']['shortTitle'],
                             '(/c{}m{})'.format(info['cinema']['id'],
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
