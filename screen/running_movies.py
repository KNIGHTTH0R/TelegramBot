# coding: utf-8

import contextlib
import urllib2
import gzip
import json

from collections import namedtuple

from datetime import datetime, timedelta
from StringIO import StringIO

from telepot.namedtuple import InlineKeyboardMarkup
from google.appengine.ext import ndb

from model.film import Film
from data import get_schedule

import settings


IMovieCinema = namedtuple('IMovieCinema', ['title', 'link', 'link_info'])


def _process_movies_markup(text_more, callback_url,
                           number_of_movies, more_date,
                           markup_tomorrow_text, markup_tomorrow_date):
    return InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=text_more,
              callback_data=(callback_url.format(
                  number_of_movies + settings.FILMS_TO_DISPLAY,
                  more_date
              ))),
         dict(text=markup_tomorrow_text,
              callback_data=(callback_url.format(
                  number_of_movies + settings.FILMS_TO_DISPLAY,
                  markup_tomorrow_date
              )))
         ]
    ])


def process_movies(data, number_of_movies, callback_url, date, city_id,
                   next_url='/info', **kwargs):

    cinema_id = kwargs.get('cinema_id')
    separator = kwargs.get('separator')
    next_info_url = kwargs.get('info_url')
    title = kwargs.get('title')

    now = datetime.now()

    videos, premiers = [], []

    to_show = settings.FILMS_TO_DISPLAY
    if len(data) == 0:
        to_show = 0

    elif len(data) < settings.FILMS_TO_DISPLAY:
        to_show = len(data)

    dformat = '%d%m%Y'
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime(dformat)
    now_str = now.strftime(dformat)

    markup_tomorrow_text = (settings.ON_TOMORROW if now.date() == date.date()
                            else settings.ON_TODAY)

    markup_tomorrow_date = (tomorrow_str if now.date() == date.date()
                            else now_str)

    more_date = now_str if now.date() == date.date() else tomorrow_str

    expanded_info = False
    if number_of_movies - to_show > len(data):
        left_border = 0
        right_border = len(data)
    else:
        left_border = number_of_movies - to_show
        right_border = number_of_movies

    for film_counter in xrange(left_border,
                               right_border):

        if film_counter < len(data):
            movie = data[film_counter]

        else:

            return (settings.NO_FILMS,
                    _process_movies_markup(settings.FIRST_TEN, callback_url, 0,
                                           more_date, markup_tomorrow_text,
                                           markup_tomorrow_date))

        # TODO: DO SOMETHING WITH THIS STUFF, DOUBLE DATA GETTER
        film = ndb.Key('Film', str(movie['id'])).get()
        # film = Film.get_by_id(movie['id'])
        two_weeks = timedelta(days=14)

        film_cinemas = get_schedule(movie['id'], date, city_id)

        if (film and
            (len(film_cinemas) < 1 and not
             ((film.premiereDateRussia and
               (now < film.premiereDateRussia < (now + two_weeks))) or
              (film.premiereDateWorld and
               (now < film.premiereDateWorld < (now + two_weeks)))))):
            continue
        # END OF STUFF

        if cinema_id and separator and next_info_url:
            expanded_info = True

            link = '{}{}{}{}'.format(next_url, cinema_id,
                                     separator, movie['id'])
            f_info = IMovieCinema(
                movie['title'], link,
                '{}{}'.format(next_info_url, movie['id'])
            )

        else:
            link = '{}{}'.format(next_url, movie['id'])
            f_info = settings.Row(settings.uncd(movie['title']), link)

        if movie['premiereDateRussia']:
            t_str = movie['premiereDateRussia']
            if 'T' in t_str:
                t_str = t_str.split('T')[0]

            prem_date = datetime.strptime(t_str, '%Y-%m-%d')
            now = datetime.utcnow()
            if prem_date > now:
                premiers.append(f_info)
            else:
                videos.append(f_info)
        else:
            premiers.append(f_info)

    mark_up = _process_movies_markup(settings.MORE,
                                     callback_url,
                                     number_of_movies,
                                     more_date,
                                     markup_tomorrow_text,
                                     markup_tomorrow_date)
    if expanded_info:
        template = (settings.JINJA_ENVIRONMENT.
                    get_template('running_movies_ext.md'))

        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'title': title,
                               'sign_point': settings.SIGN_POINT,
                               'sign_calendar': settings.SIGN_CALENDAR,
                               'sign_newspaper': settings.SIGN_NEWSPAPER,
                               'sign_premier': settings.SIGN_PREMIER})
    else:
        template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_point': settings.SIGN_POINT,
                               'title': title,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_premier': settings.SIGN_PREMIER})

    return msg, mark_up


def display_running_movies_api(number_of_movies, city_id):
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    callback_url = '/movies{}'
    date = datetime.now()
    return process_movies(data, number_of_movies, callback_url, date, city_id)


def display_soon_films(number_of_movies, city_id):
    return display_films(
        number_of_movies,
        url=settings.URL_SOON_MOVIES.format(settings.KINOHOD_API_KEY),
        callback_url='/movies{}ts',
        city_id=city_id
    )


def display_running_now_films(number_of_movies, city_id):
    return display_running_movies_api(number_of_movies, city_id)
    # display_films(
    #     number_of_movies,
    #     url=settings.URL_RUNNING_NOW_MOVIES.format(settings.KINOHOD_API_KEY),
    #     callback_url='/movies{}tr}'
    # )


def display_films(number_of_movies, url, callback_url, city_id):
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        data = json.loads(jf.read())

    callback_url = callback_url
    date = datetime.now()
    return process_movies(data, number_of_movies, callback_url, date, city_id)


def process_movies_db(number_of_movies, callback_url,
                      next_url='/info', **kwargs):

    data = Film.query().order(-Film.rating).fetch(
        offset=(number_of_movies - settings.FILMS_TO_DISPLAY
                if number_of_movies > settings.FILMS_TO_DISPLAY
                else number_of_movies),
        limit=settings.FILMS_TO_DISPLAY
    )

    cinema_id = kwargs.get('cinema_id')
    separator = kwargs.get('separator')
    next_info_url = kwargs.get('info_url')

    videos, premiers = [], []

    expanded_info = False
    for f in data:

        if cinema_id and separator and next_info_url:
            expanded_info = True

            link = '{}{}{}{}'.format(next_url, cinema_id,
                                     separator, f.kinohod_id)
            f_info = IMovieCinema(
                f.title, link,
                '{}{}'.format(next_info_url, f.kinohod_id)
            )

        else:
            link = '{}{}'.format(next_url, f.kinohod_id)
            f_info = settings.Row(settings.uncd(f.title), link)

        if f.premiereDateRussia:
            now = datetime.utcnow()
            if f.premiereDateRussia > now:
                premiers.append(f_info)
            else:
                videos.append(f_info)
        else:
            premiers.append(f_info)

    mark_up = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text=settings.MORE,
              callback_data=(callback_url.format(
                  number_of_movies + 2 * settings.FILMS_TO_DISPLAY)
              ))]
    ])

    if expanded_info:
        template = (settings.JINJA_ENVIRONMENT.
                    get_template('running_movies_ext.md'))

        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_calendar': settings.SIGN_CALENDAR,
                               'sign_newspaper': settings.SIGN_NEWSPAPER,
                               'sign_premier': settings.SIGN_PREMIER})
    else:
        template = settings.JINJA_ENVIRONMENT.get_template('running_movies.md')
        msg = template.render({'videos': videos, 'premiers': premiers,
                               'sign_video': settings.SIGN_VIDEO,
                               'sign_tip': settings.SIGN_TIP,
                               'sign_premier': settings.SIGN_PREMIER})

    return msg, mark_up


def display_running_movies(number_of_movies):
    callback_url = '/movies{}'
    return process_movies_db(number_of_movies, callback_url)


def get_cinema_movies(cinema_id, number_of_movies, date,
                      title=None, city_id=1):

    url = settings.URL_CINEMA_MOVIE_DATE.format(
        cinema_id,
        date,
        settings.KINOHOD_API_KEY,
    )

    try:
        with contextlib.closing(urllib2.urlopen(url)) as jf:
            data = json.loads(jf.read())
    except Exception:
        return settings.DONT_UNDERSTAND

    data = [d['movie'] for d in data]

    callback_url = '/show' + str(cinema_id) + 'v{}' + 'in{}'

    return process_movies(data, number_of_movies, callback_url,
                          datetime.strptime(date, '%d%m%Y'),
                          city_id,
                          next_url='/c', info_url='/info',
                          title=title,
                          cinema_id=cinema_id, separator='m')
