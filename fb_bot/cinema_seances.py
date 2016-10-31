# coding: utf-8
import contextlib
import json
import urllib
import urllib2

from datetime import timedelta, datetime

import settings
from fb_bot.fb_api_wrapper import construct_message_with_attachment
from fb_bot.fb_api_wrapper import construct_message_with_text


def _days_for_buttons(day):
    if day == settings.TODAY:
        b_first, b_second = settings.TOMORROW, settings.A_TOMORROW

    elif day == settings.TOMORROW:
        b_first, b_second = settings.TODAY, settings.A_TOMORROW

    elif day == settings.A_TOMORROW:
        b_first, b_second = settings.TODAY, settings.TOMORROW

    else:
        b_first, b_second = settings.TOMORROW, settings.A_TOMORROW

    return b_first, b_second


def _titles_for_buttons(day):
    if day == settings.TODAY:
        t_first, t_second = 'Завтра', 'Послезавтра'

    elif day == settings.TOMORROW:
        t_first, t_second = 'Сегодня', 'Послезавтра'

    elif day == settings.A_TOMORROW:
        t_first, t_second = 'Сегодня', 'Завтра'

    else:
        t_first, t_second = 'Завтра', 'Послезавтра'

    return t_first, t_second


def _url_encode(city_name):
    city_name_dict = {'cityName': city_name.encode('utf-8')}
    url_encoded_dict = urllib.urlencode(city_name_dict)
    return url_encoded_dict


def get_data(url):
    with contextlib.closing(urllib2.urlopen(url)) as jf:
        return json.loads(jf.read())


def _day_of_seance(day):

    def _r_day(digit):
        return '0{}'.format(digit) if int(digit) < 10 else digit

    def day_func(d):
        return '{}{}{}'.format(_r_day(d.day), _r_day(d.month), _r_day(d.year))

    v = {
        settings.TODAY: datetime.now() + timedelta(hours=3),
        settings.TOMORROW:
            (datetime.now() + timedelta(hours=3) +
             timedelta(days=settings.TOMORROW)),
        settings.A_TOMORROW:
            (datetime.now() + timedelta(hours=3) +
             2 * timedelta(days=settings.TOMORROW))
    }
    if isinstance(day, datetime):
        return day_func(day)
    return day_func(v[day]) if day in v else day_func(datetime.now() +
                                                      timedelta(hours=3) +
                                                      timedelta(days=day))


def _calculate_is_onsale(t_str):
    start_time = datetime.strptime(t_str[0:16], '%Y-%m-%dT%H:%M')

    def t_f(s):
        return timedelta(hours=int(s[20:22]), seconds=int(s[22:]))

    start_time += (- t_f(t_str)) if t_str[19] == '+' else t_f(t_str)

    if (start_time - datetime.utcnow()) < timedelta(minutes=30):
        return False
    return True


def _construct_time_button(seance):

    format_name = seance.get('formatName')
    min_price = seance.get('minPrice')
    title = seance['time']
    if format_name and min_price:
        title = '{} {} от {}р.'.decode('utf-8').format(
            seance['time'], format_name, min_price
        )

    elif format_name:
        title = '{} {}'.format(
            seance['time'], format_name
        )

    elif min_price:
        title = '{} от {}р.'.decode('utf-8').format(
            seance['time'], min_price
        )

    button = {
        'type': 'web_url',
        'url': (settings.KINOHOD_WIDGET_WITH_UTM_SOURCE.format(
            _url_encode(u'Москва'), seance['id']
            )
        ),
        'title': title
    }
    return button


def _construct_seances_generic_short(info, buttons, date=None):

    stations_str = ', '.join([a['name']
                              for a in info['cinema']['subway_stations']])

    if info['cinema'] and info['cinema']['mall']:
        subtitle = u'Адрес: {}\n{}\nМетро: {}'.format(
            settings.uncd(info['cinema']['address']),
            settings.uncd(info['cinema']['mall']),
            settings.uncd(stations_str)
        )
    else:
        subtitle = u'Адрес: {}\nМетро: {}'.format(
            settings.uncd(info['cinema']['address']),
            settings.uncd(stations_str)
        )

    if date:
        my_date = datetime(
            year=date.year, month=date.month, day=date.day
        ).date()
        days_shift = (my_date - datetime.now().date()).days
    else:
        days_shift = settings.TODAY
    last_button = {
        'type': 'postback',
        'title': 'Больше сеансов',
        'payload': '/c{}m{}d{}'.format(info['cinema']['id'],
                                       info['movie']['id'],
                                       days_shift)
    }
    buttons.append(last_button)
    f_info = {
        'title': info['cinema']['shortTitle'],
        'subtitle': subtitle,
        'buttons': buttons
    }
    return f_info


def _contruct_payload_seances_short(recipient_id, seances,
                                    movie_id, starting_n,
                                    date=datetime.now().date()):
    quick_replies = [
        {
            'content_type': 'text',
            'title': 'Ещё',
            'payload': 'seances{}num{}d{}'.format(
                movie_id, starting_n, date
            )
        },
        {
            'content_type': 'text',
            'title': 'Другой день',
            'payload': 's_short{}d{}'.format(
                movie_id, (datetime.now() + timedelta(days=1)).date()
            )
        }
    ]
    payload = construct_message_with_attachment(
        recipient_id, seances, quick_replies
    )
    return payload


def _construct_generic_seance(movie_title, seance, cinema_title):
    format_name = seance.get('formatName')
    min_price = seance.get('minPrice')
    time = seance['time']
    month = seance['startTime'][5:7]
    day = seance['startTime'][8:10]
    date = '{}.{}'.format(day, month)
    if format_name and min_price:
        subtitle = ('Фильм: {}\nКинотеатр: {}\n'
                    'Формат: {}\nЦена от: {}р.').decode('utf-8').format(
            movie_title, cinema_title, format_name, min_price
        )

    elif format_name:
        subtitle = 'Фильм: {}\nКинотеатр: {}\nФормат: {}'.format(
            movie_title, cinema_title, format_name
        )

    elif min_price:
        subtitle = ('Фильм: {}\nКинотеатр: {}\n'
                    'Цена от: {}р.').decode('utf-8').format(
            movie_title, cinema_title, min_price
        )
    else:
        subtitle = 'Фильм: {}\nКинотеатр: {}'.decode('utf-8').format(
            movie_title, cinema_title
        )

    sc_info = {
        'title': '{} в {}'.decode('utf-8').format(date, time),
        'subtitle': subtitle,
        'buttons': [
            {
                'type': 'web_url',
                'url': (
                    settings.KINOHOD_WIDGET_WITH_UTM_SOURCE.format(
                        _url_encode(u'Москва'), seance['id']
                    )
                ),
                'title': 'Купить билет'
            }
        ]
    }
    return sc_info


def _construct_final_generic_seance_payload(recipient_id, seances, cinema_id,
                                            movie_id, t_first, b_first,
                                            t_second, b_second):
    quick_replies = [
        {
            'content_type': 'text',
            'title': t_first,
            'payload': '/c{}m{}d{}'.format(cinema_id,
                                           movie_id,
                                           b_first)
        },
        {
            'content_type': 'text',
            'title': t_second,
            'payload': '/c{}m{}d{}'.format(cinema_id,
                                           movie_id,
                                           b_second)
        },
        {
            'content_type': 'text',
            'title': 'Другой день',
            'payload': '/c{}m{}d{}'.format(cinema_id,
                                           movie_id,
                                           settings.ANOTHER_FB_DAY)
        },
        {
            'content_type': 'text',
            'title': 'Другой кинотеатр',
            'payload': 'nearest0'
        }

    ]
    payload = construct_message_with_attachment(
        recipient_id, seances, quick_replies
    )
    return payload


def _construct_final_generic_no_seances(recipient_id, cinema_id,
                                        movie_id, t_first, b_first,
                                        t_second, b_second):
    quick_replies = [
        {
            'content_type': 'text',
            'title': t_first,
            'payload': '/c{}m{}d{}'.format(cinema_id,
                                           movie_id,
                                           b_first)
        },
        {
            'content_type': 'text',
            'title': t_second,
            'payload': '/c{}m{}d{}'.format(cinema_id,
                                           movie_id,
                                           b_second)
        },
        {
            'content_type': 'text',
            'title': 'Другой день',
            'payload': '/c{}m{}d{}'.format(cinema_id,
                                           movie_id,
                                           settings.ANOTHER_FB_DAY)
        },
        {
            'content_type': 'text',
            'title': 'Другой кинотеатр',
            'payload': 'nearest0'
        }

    ]
    text = settings.NO_SEANCES_FOR_DAY
    payload = construct_message_with_text(recipient_id, text, quick_replies)
    return payload


def display_cinema_seances_short(recipient_id, movie_id, starting_n=0,
                                 lat=0.0, lng=0.0, date=None):
    starting_n = int(starting_n)

    url_movies_info = settings.URL_MOVIES_INFO.format(
        movie_id, settings.KINOHOD_API_KEY
    )

    html_data = get_data(url_movies_info)
    if ('premiereDateRussia' in html_data and
       html_data['premiereDateRussia'] is not None):
        premiere_date_russia = html_data['premiereDateRussia'][0:10]
        premiere_date_fromatted = '{}{}{}'.format(
            premiere_date_russia[8:10],
            premiere_date_russia[5:7],
            premiere_date_russia[0:4]
        )
        if (datetime.now() + timedelta(hours=3) <
                datetime.strptime(premiere_date_russia, '%Y-%m-%d')):
            url = settings.URL_SEANCES_GEO_ANOTHER_DATE.format(
                str(movie_id), settings.KINOHOD_API_KEY,
                premiere_date_fromatted, starting_n,
                starting_n + 1000, lat, lng
            )
        else:
            if lat != 0.0 and lng != 0.0:
                url = settings.URL_SEANCES_GEO.format(
                    str(movie_id), settings.KINOHOD_API_KEY, starting_n,
                    starting_n + 1000, lat, lng
                )

            else:
                url = settings.URL_SEANCES.format(
                    str(movie_id), settings.KINOHOD_API_KEY, starting_n,
                    starting_n + 1000
                )
    else:
        if lat != 0.0 and lng != 0.0:
            url = settings.URL_SEANCES_GEO.format(
                str(movie_id), settings.KINOHOD_API_KEY, starting_n,
                starting_n + 1000, lat, lng
            )

        else:
            url = settings.URL_SEANCES.format(
                str(movie_id), settings.KINOHOD_API_KEY, starting_n,
                starting_n + 1000
            )
    if date:
        my_date = datetime(year=date.year, month=date.month, day=date.day)
        url += '&date={}'.format(_day_of_seance(my_date))

    seances = []
    html_data = get_data(url)
    counter = 0
    for info in html_data:
        if len(seances) == 10:
            break
        buttons = []
        for seance in info['schedules']:
            counter += 1
            if not _calculate_is_onsale(seance['startTime']):
                continue
            button = _construct_time_button(seance)
            buttons.append(button)
            if counter < starting_n:
                continue
        if counter < starting_n:
            continue
        buttons = buttons[0:2]
        f_info = _construct_seances_generic_short(info, buttons, date)
        seances.append(f_info)

    if len(seances) == 0:
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                'text': 'К сожалению, я не нашёл сеансов.'
            }
        }
        payload = json.dumps(payload)
        return payload
    if date:
        payload = _contruct_payload_seances_short(recipient_id, seances,
                                                  movie_id, counter, date=date)
    else:
        payload = _contruct_payload_seances_short(recipient_id, seances,
                                                  movie_id, counter)
    payload = json.dumps(payload)

    my_date = datetime.strptime(html_data[0]['date'][0:10], '%Y-%m-%d')
    movie_title = html_data[0]['movie']['title']

    text = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': u'Дата: {}.{}.{}\nФильм: {}'.format(
                my_date.day, my_date.month, my_date.year,
                movie_title
            )
        }
    }
    text = json.dumps(text)

    return [text] + [payload]


def display_cinema_seances(recipient_id, cinema_id, movie_id, day):
    if not isinstance(day, datetime):
        if day.isdigit():
            day = int(day)

    url_movies_info = settings.URL_MOVIES_INFO.format(
        movie_id, settings.KINOHOD_API_KEY
    )

    shift = False
    html_data = get_data(url_movies_info)
    if ('premiereDateRussia' in html_data and
       html_data['premiereDateRussia'] is not None):
        premiere_date_russia = html_data['premiereDateRussia'][0:10]
        date_time_repr = datetime.strptime(premiere_date_russia, '%Y-%m-%d')
        if isinstance(day, datetime):
            if day - datetime.now() > date_time_repr - datetime.now():
                shift = True
        if isinstance(day, int):
            if timedelta(days=day) + datetime.now() > date_time_repr:
                shift = True
        if datetime.now() + timedelta(hours=3) < date_time_repr and not shift:
            day_str = _day_of_seance(date_time_repr)
        else:
            day_str = _day_of_seance(day)
    else:
        day_str = _day_of_seance(day)

    url = settings.URL_CINEMA_SEANCES.format(
        cinema_id, settings.KINOHOD_API_KEY, day_str
    )

    seances = []
    html_data = get_data(url)

    for info in html_data:
        if len(seances) == 10:
            break
        if int(info['movie']['id']) != int(movie_id):
            continue
        cinema_title = info['cinema']['shortTitle']
        for seance in info['schedules']:
            if not _calculate_is_onsale(seance['startTime']):
                continue
            sc_info = _construct_generic_seance(
                info['movie']['title'], seance, cinema_title)
            seances.append(sc_info)

    seances_chunks = []
    chunk = []
    for i in xrange(0, len(seances)):
        if i % 10 == 0 and i != 0:
            seances_chunks.append(chunk)
            chunk = []
            chunk.append(seances[i])
        else:
            chunk.append(seances[i])
    seances_chunks.append(chunk)

    payloads = []
    if len(seances) > 0:
        for chunk in seances_chunks:

            seances = chunk
            b_first, b_second = _days_for_buttons(day)
            t_first, t_second = _titles_for_buttons(day)
            payload = _construct_final_generic_seance_payload(
                recipient_id, seances, cinema_id, movie_id, t_first, b_first,
                t_second, b_second)
            payload = json.dumps(payload)
            payloads.append(payload)
    else:
        b_first, b_second = _days_for_buttons(day)
        t_first, t_second = _titles_for_buttons(day)
        payload = _construct_final_generic_no_seances(
            recipient_id, cinema_id, movie_id, t_first, b_first,
            t_second, b_second)
        payload = json.dumps(payload)
        payloads.append(payload)
    return payloads
