# coding: utf-8

import contextlib
import urllib2
import json

from collections import namedtuple, OrderedDict
from datetime import timedelta, datetime

from telepot.namedtuple import InlineKeyboardMarkup

from model.film import Film
from model.cinema import Cinema

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

    day_id_m = OrderedDict({settings.ON_TODAY: 0,
                            settings.ON_TOMORROW: 1,
                            settings.ON_A_TOMORROW: 2})

    def display_other(d):
        days_reverse = {v: k for k, v in day_id_m.iteritems()}
        ds = day_id_m.keys()
        if d in days_reverse:
            ds.remove(days_reverse[d])
            return make_markup(ds)
        # this mean another day (not today, tomorrow and not after tomorrow)
        return make_markup([settings.ON_TODAY, settings.ON_TOMORROW])

    def make_markup(a):
        first, second = a
        return InlineKeyboardMarkup(inline_keyboard=[[
            dict(text=second,
                 callback_data=(
                     '/c{}m{}d{}'.format(cinema_id, movie_id, day_id_m[second])
                 )),
            dict(text=first,
                 callback_data=(
                     '/c{}m{}d{}'.format(cinema_id, movie_id, day_id_m[first])
                 )),
            dict(text=settings.ANOTHER_DAY,
                 callback_data=(
                     '/anytimec{}m{}d'.format(cinema_id, movie_id)
                 )),
        ]])

    return display_other(day)


def _day_of_seance(day):

    def _r_day(digit):
        return '0{}'.format(digit) if int(digit) < 10 else digit

    def day_func(d):
        return '{}{}{}'.format(_r_day(d.day), _r_day(d.month), _r_day(d.year))

    now = datetime.utcnow()
    v = {
        settings.TODAY: now,
        settings.TOMORROW: now + timedelta(days=settings.TOMORROW),
        settings.A_TOMORROW: now + 2 * timedelta(days=settings.TOMORROW)
    }

    return day_func(v[day]) if day in v else ''


def detect_cinema_seances(cinema_id, movie_id, day):

    if not isinstance(day, datetime):
        day = int(day)
        day_str = _day_of_seance(day)
    else:
        day_str = day.strftime('%d%m%Y')

    url = settings.URL_CINEMA_SEANCES.format(
        cinema_id, settings.KINOHOD_API_KEY, day_str
    )

    try:
        with contextlib.closing(urllib2.urlopen(url)) as hd:
            html_data = json.loads(hd.read())
    except Exception as ex:
        import logging
        logging.debug(ex.message)
        return None, None

    CinemaSeances = namedtuple('CinemaSeances',
                               ['tip', 'time', 'minPrice', 'id', 'format'])

    if html_data is None:
        return settings.NO_SEANCE, None

    place = ''.decode('utf-8')
    if isinstance(html_data, list) and len(html_data) > 0:
        place = html_data[0]['cinema']['title']

    for info in html_data:

        if int(movie_id) != int(info['movie']['id']):
            continue

        seances = []
        for s in info['schedules']:
            m_p = s['minPrice'] if s['minPrice'] else None

            s_f = None
            if s['formatName'] and len(s['formatName']) < 10:
                s_f = s['formatName']

            if _calculate_is_onsale(s['startTime']):
                seances.append(
                    CinemaSeances(
                        settings.SIGN_TIP,
                        s['time'],
                        m_p,
                        int(s['id']),
                        s_f
                    )
                )
            else:
                seances.append(
                    CinemaSeances(settings.SIGN_TIP, s['time'], m_p, 0, s_f)
                )

        markup = _construct_markup(cinema_id, movie_id, day)
        template = settings.JINJA_ENVIRONMENT.get_template('cinema_seances.md')

        if day_str:
            day_str = day_str.decode('utf-8')
            day_str = '{}.{}.{}'.format(day_str[:2], day_str[2:4], day_str[4:])
        else:
            day_str = ''

        return template.render({
            'title': info['movie']['title'],
            'seances': seances,
            'place': place,
            'date': day_str
        }), markup

    cinema = Cinema.get_by_id(str(cinema_id))
    film = Film.get_by_id(str(movie_id))
    markup = _construct_markup(cinema_id, movie_id, day)

    day = day.strftime('%d.%m') if isinstance(day, datetime) else ''
    return settings.NO_FILM_SCHEDULE.format(
        film.title if film else '',
        day,
        cinema.title if cinema else ''
    ), markup
