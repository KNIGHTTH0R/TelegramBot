# coding: utf-8

import contextlib
import urllib2
import json

from collections import namedtuple
from datetime import timedelta, datetime

from telepot.namedtuple import InlineKeyboardMarkup

import settings


def _calculate_is_onsale(t_str):
    start_time = datetime.strptime(t_str[0:16], '%Y-%m-%dT%H:%M')

    def t_f(s):
        return timedelta(hours=int(s[20:22]), seconds=int(s[22:]))

    start_time += (- t_f(t_str)) if t_str[19] == '+' else t_f(t_str)

    if (start_time - datetime.utcnow()) < timedelta(minutes=30):
        return False
    return True


def _construct_markup(cinema_id, movie_id, day):

    day_id_m = {settings.ON_TODAY: 0,
                settings.ON_TOMORROW: 1,
                settings.ON_A_TOMORROW: 2}

    def display_other(d):
        days_reverse = {v: k for k, v in day_id_m.iteritems()}
        ds = day_id_m.keys()
        if d in days_reverse:
            ds.remove(days_reverse[d])
            return make_markup(ds)

    def make_markup(a):
        first, second = a
        return InlineKeyboardMarkup(inline_keyboard=[[
            dict(text=first,
                 callback_data=(
                     '/c{}m{}d{}'.format(cinema_id, movie_id, day_id_m[first])
                 )),
            dict(text=second,
                 callback_data=(
                     '/c{}m{}d{}'.format(cinema_id, movie_id, day_id_m[second])
                 ))
        ]])

    return display_other(day)


def _day_of_seance(day):

    def _r_day(digit):
        return '0{}'.format(digit) if int(digit) < 10 else digit

    def day_func(d):
        return '{}{}{}'.format(_r_day(d.day), _r_day(d.month), _r_day(d.year))

    v = {
        settings.TODAY: datetime.now(),
        settings.TOMORROW: datetime.now() + timedelta(days=settings.TOMORROW),
        settings.A_TOMORROW:
            datetime.now() + 2 * timedelta(days=settings.TOMORROW)
    }

    return day_func(v[day]) if day in v else ''


def display_cinema_seances(cinema_id, movie_id, day):
    day = int(day)
    day_str = _day_of_seance(day)

    url = settings.URL_CINEMA_SEANCES.format(
        cinema_id, settings.KINOHOD_API_KEY, day_str
    )

    with contextlib.closing(urllib2.urlopen(url)) as hd:
        html_data = json.loads(hd.read())

    f = namedtuple('f', ['tip', 'time', 'minPrice', 'id'])

    if html_data is None:
        return None, None

    for info in html_data:
        if int(movie_id) != int(info['movie']['id']):
            continue
        seances = []
        for s in info['schedules']:
            if _calculate_is_onsale(s['startTime']):
                seances.append(f(settings.SIGN_TIP, s['time'],
                                 s['minPrice'], int(s['id'])))

            else:
                seances.append(f(settings.SIGN_TIP, s['time'],
                                 s['minPrice'], 0))

        markup = _construct_markup(cinema_id, movie_id, day)
        template = settings.JINJA_ENVIRONMENT.get_template('cinema_seances.md')
        return template.render(
            {'title': info['movie']['title'], 'seances': seances}
        ), markup
