# -*- coding: utf8 -*-
import gzip
import json
import logging
import ssl

import datetime
from rexec import FileWrapper

import numpy as np
import scipy.misc as smp
import telepot
from PIL import ImageDraw
from StringIO import StringIO
from django.http import (HttpResponseForbidden, HttpResponseBadRequest,
                         JsonResponse)
import time
from django.conf import settings

from telepot.namedtuple import InlineKeyboardMarkup

import urllib2

import tempfile

KINOHOD_API_KEY='f056d104-abcd-3ab7-9132-cfcf3a098bc4'
TELEGRAM_BOT_TOKEN='220697123:AAEBdacDOFAIIWUASAzCCfMStBcMmGz7PO0'

TelegramBot = telepot.Bot(TELEGRAM_BOT_TOKEN)
logger = logging.getLogger('telegram.bot')




def _display_help():
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text='Telegram URL', url='https://core.telegram.org/'),
             dict(text='Yandex URL', url='https://yandex.ru/')],
        ])

    return markup


def _display_running_movies():
    url = ('https://api.kinohod.ru/api/data/2/{}/running.json.gz'.
           format(KINOHOD_API_KEY))
    context = ssl._create_unverified_context()
    json_data = urllib2.urlopen(url, context=context).read()
    m_stream = gzip.GzipFile(fileobj=StringIO(json_data), mode='rb')
    data = json.loads(m_stream.read())
    m_stream.close()
    premiers = '\xF0\x9F\x8E\xAC Премьеры этой недели: \n'
    response = '\xF0\x9F\x8E\xA5 Фильмы в прокате: \n'
    looper = 0
    have_premiers = False
    while looper < 10:
        movie = data[looper]
        info_row = '{} (/info{})'.format(movie['title'].encode('utf-8'),
                                         str(movie['id']))
        if (datetime.datetime.strptime(movie['premiereDateRussia'],
                                       "%Y-%m-%d") >
                datetime.datetime.now()):
            premiers += '\xE2\x9C\x94' + info_row + '\n'
            have_premiers = True
        else:
            response += '\xE2\x9C\x94' + info_row + '\n'
        looper += 1
    if have_premiers:
        response += premiers
    return response


def _display_movie_info(movie_id):
    url = ('https://kinohod.ru/api/rest/partner/v1/movies/{}?apikey={}'.
           format(str(movie_id), KINOHOD_API_KEY))
    context = ssl._create_unverified_context()
    html_data = json.loads(urllib2.urlopen(url, context=context).read())

    movie_id = str(html_data['id'])

    actors = html_data['actors']
    actors_str = '\xF0\x9F\x91\xA4 *Актёры*: '
    for actor in actors:
        actors_str += actor.encode('utf-8') + ', '
    actors_str = actors_str[: -2]
    actors_str += '\n'

    duration = ('*Продолжительность:* ' +
                str(html_data['duration']) +
                'мин.' '\n')

    genres = html_data['genres']
    genres_str = '*Жанры*: '
    for genre in genres:
        genres_str += genre.encode('utf-8') + ', '
    genres_str = genres_str[: -2]
    genres_str += '\n'

    producers = html_data['producers']
    producers_str = '*Продюсеры:* '
    for producer in producers:
        producers_str += producer.encode('utf-8') + ', '
    producers_str = producers_str[: -2]
    producers_str += '\n'

    directors = html_data['directors']
    directors_str = '*Режисёры:* '
    for director in directors:
        directors_str += director.encode('utf-8') + ', '
    directors_str = directors_str[: -2]
    directors_str += '\n'

    title = '*' + html_data['title'].encode('utf-8') + '*' + '\n'
    imdb_id = str(html_data['imdb_id'])

    annotation = html_data['annotationFull'].encode('utf-8') + '\n'

    message = (title + annotation + duration +
               genres_str + actors_str +
               producers_str + directors_str)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [dict(text='IMDB', url='http://www.imdb.com/title/tt' + str(imdb_id)),
         dict(text='Выбрать сеанс', callback_data = ('/seance' + movie_id))]
    ])

    return message, markup


def _display_seances(movie_id):
    url = ('https://kinohod.ru/api/rest/partner/v1/movies/{}/schedules?'
           'apikey={}&limit=30'.format(str(movie_id), KINOHOD_API_KEY))
    context = ssl._create_unverified_context()
    html_data = json.loads(urllib2.urlopen(url, context=context).read())
    response = '*Кинотеатры* \n'
    have_seances = False
    for info in html_data:
        have_seances = True
        cinema = info['cinema']
        movie_id = info['movie']['id']
        row = ('{} (/c{}m{})\n'.format(cinema['shortTitle'].encode('utf-8'),
                                       str(cinema['id']), str(movie_id)))

        response += row
    if not have_seances:
        response += 'Сегодня фильма ещё нет в прокате.'
    return response


def _draw_cinemahall(schedule_id):
    url = ('https://kinohod.ru/api/rest/partner/v1/schedules/{}/'
           'hallscheme?apikey=f056d104-abcd-3ab7-9132-cfcf3a098bc4&'
           'limit=20'.format(schedule_id))

    context = ssl._create_unverified_context()
    html_data = json.loads(urllib2.urlopen(url, context=context).read())
    shift = 10
    for info in html_data:
        for section in info['sections']:
            picture_width = section['width']
            picture_height = section['height']
            data = np.zeros((picture_height,
                             picture_width,
                             3),
                            dtype=np.uint8)
            data[:, :] = [242, 242, 242]
            for seat in section['seats']:
                x = int(seat['x']) + shift/2
                y = int(seat['y'])
                seat_height = seat['height']
                seat_width = seat['width']
                if seat['status'] == 'vacant':
                    if seat['class'] == 'color1':
                        data[y - seat_height/2:
                             y+seat_height/2,
                             x - seat_width/2:
                             x+seat_width/2] = [1, 137, 243]
                    if seat['class'] == 'color2':
                        data[y - seat_height / 2:
                             y + seat_height / 2,
                             x - seat_width / 2:
                             x + seat_width / 2] = [255, 180, 0]

                else:
                    data[y - seat_height/2:
                         y + seat_height/2,
                         x - seat_width/2:
                         x + seat_width/2] = [221, 221, 221]

            img = smp.toimage(data)
            # Нумерация мест
            # draw = ImageDraw.Draw(img)
            # for seat in section['seats']:
            #     x = int(seat['x'])
            #     seat_width = int(seat['width'])
            #     seat_height = int(seat['height'])
            #     if int(seat['row']) == 1:
            #         draw.text((x,
            #                    int(seat['y']) - seat_height*1.5),
            #                   str(seat['number']),
            #                   fill=(0, 0, 0, 64))
            #     if int(seat['number']) == 1:
            #         draw.text(
            #             (x - seat_width , int(seat['y']) - seat_height/3),
            #             str(seat['row']),
            #             fill=(0, 0, 0, 64))

    tmpfile = tempfile.TemporaryFile()
    img.save(tmpfile, format='bmp', quality=80)
    tmpfile.seek(0)
    wrapper = FileWrapper(tmpfile)
    return wrapper


def _display_cinema_seances(cinema_id, movie_id):
    url = ('https://kinohod.ru/api/rest/partner/v1/cinemas/{}/schedules?'
           'apikey={}&limit=10'.format(str(cinema_id), KINOHOD_API_KEY))
    context = ssl._create_unverified_context()
    html_data = json.loads(urllib2.urlopen(url, context=context).read())
    for info in html_data:
        schedule_movie_id = info['movie']['id']
        movie_name = info['movie']['title']
        if int(movie_id) != int(schedule_movie_id):
            continue
        schedules = info['schedules']
        response = '*Сеансы: *' + movie_name.encode('utf-8') + '\n'
        for seance in schedules:
            row = ('\xE2\x8C\x9A {} от {}руб. (/schedule{})\n'.
                   format(str(seance['time']),
                          str(seance['minPrice']),
                          str(seance['id'])))
            response += row
    return response


def post():
    LAST_UPDATE = 188027601
    while True:
        time.sleep(1)
        updates = TelegramBot.getUpdates(offset=LAST_UPDATE)
        for payload in updates:
            LAST_UPDATE += 1
            commands = {
                '/start': _display_help,
                '/movies': _display_running_movies,
                '/info': _display_movie_info,
                'help': _display_help,
            }

            if 'message' in payload:
                chat_id = payload['message']['chat']['id']
                cmd = payload['message'].get('text')  # command

            if 'callback_query' in payload:
                cmd = payload['callback_query']['data']
                callback_query_id = int(payload['callback_query']['id'])
                movie_id = cmd[7: len(cmd)]
                response = _display_seances(movie_id)
                chat_id = payload['callback_query']['message']['chat']['id']
                TelegramBot.sendMessage(
                    chat_id,
                    response,
                    parse_mode='Markdown')
                TelegramBot.answerCallbackQuery(
                    callback_query_id=callback_query_id,
                    text=':)')
            elif cmd.startswith('/schedule'):
                schedule_id = cmd[9:len(cmd)]
                try:
                    hall_image = _draw_cinemahall(schedule_id)
                    TelegramBot.sendChatAction(chat_id, 'upload_photo')
                    TelegramBot.sendPhoto(
                        chat_id,
                        ('hall.bmp', hall_image)
                    )
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Купить билеты',
                              url=('https://kinohod.ru/widget/?cityName={}'
                                   '#scheme_{}'.format(u'Москва'.
                                                       encode('utf-8'),
                                                       schedule_id))),
                         ],
                    ])
                    TelegramBot.sendMessage(
                        chat_id,
                        'Серые - занято. Синие - свободно.',
                        reply_markup=markup,)
                except:
                    TelegramBot.sendMessage(
                        chat_id,
                        'Увы, сервер недоступен.')

            elif cmd.startswith('/info'):
                movie_id = cmd[5:len(cmd)]
                message, mark_up = _display_movie_info(movie_id)
                TelegramBot.sendMessage(
                    chat_id,
                    message,
                    reply_markup=mark_up,
                    parse_mode='Markdown')

            elif cmd.startswith('/c'):
                index_of_m = cmd.index('m')
                cinema_id = cmd[2:index_of_m]
                movie_id = cmd[index_of_m+1:len(cmd)]
                response = _display_cinema_seances(cinema_id, movie_id)
                TelegramBot.sendMessage(
                    chat_id,
                    response,
                    parse_mode='Markdown')
            else:
                func = commands.get(cmd.split()[0].lower())
                if func:
                    text = func()
                    TelegramBot.sendMessage(chat_id, text)
                else:
                    TelegramBot.sendMessage(chat_id,
                                            'I do not understand you, Sir!')

    return JsonResponse({}, status=200)


post()