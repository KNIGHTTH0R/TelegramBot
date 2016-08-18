# -*- coding: utf8 -*-

import contextlib
import gzip
import json
import logging
import ssl
import urllib
import urllib2

from collections import namedtuple
from datetime import datetime
from StringIO import StringIO

import telepot

from django.http import (JsonResponse, HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from telepot.namedtuple import InlineKeyboardMarkup

from draw import draw_cinemahall

import botan
import settings

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)
logger = logging.getLogger('telegram.bot')
Row = namedtuple('Row', ['title', 'link'])


def _display_help():
    return render_to_string('help.md', {'help': settings.SIGN_SMILE_HELP})


def _display_running_movies():
    url = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)

    context = ssl._create_unverified_context()  # need to fix it

    with contextlib.closing(urllib2.urlopen(url, context=context)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    videos, premiers = [], []
    for film_counter in xrange(settings.FILMS_TO_DISPLAY):
        movie = data[film_counter]
        f_info = Row(movie['title'].encode('utf-8'), movie['id'])

        prem_date = datetime.strptime(movie['premiereDateRussia'], "%Y-%m-%d")
        if prem_date > datetime.now():
            premiers.append(f_info)
        else:
            videos.append(f_info)

    return render_to_string('running_movies.md',
                            {'videos': videos, 'premiers': premiers,
                             'sign_video': settings.SIGN_VIDEO,
                             'sign_tip': settings.SIGN_TIP,
                             'sign_premier': settings.SIGN_PREMIER})


def _display_movie_info(movie_id):

    def get_data(name):
        return ', '.join([a.encode('utf-8') for a in html_data[name]])

    url = settings.URL_MOVIES_INFO.format(movie_id, settings.KINOHOD_API_KEY)

    context = ssl._create_unverified_context()

    with contextlib.closing(urllib2.urlopen(url, context=context)) as jf:
        html_data = json.loads(jf.read())

    markup = InlineKeyboardMarkup(inline_keyboard=[[
        dict(text='IMDB', url=settings.URL_IMDB.format(html_data['imdb_id'])),
        dict(text=settings.CHOOSE_SEANCE,
             callback_data=('/seance{}'.format(html_data['id'])))
    ]])

    return render_to_string('movies_info.md', {
        'title': html_data['title'].encode('utf-8'),
        'description': html_data['annotationFull'].encode('utf-8'),
        'duration': '{} {}'.format(html_data['duration'], settings.SIGN_MIN),
        'genres': get_data('genres'),
        'sign_actor': settings.SIGN_ACTOR,
        'actors': get_data('actors'),
        'producers': get_data('producers'),
        'directors': get_data('directors')
    }), markup


def _display_seances(movie_id):
    url = settings.URL_SEANCES.format(movie_id, settings.KINOHOD_API_KEY)

    context = ssl._create_unverified_context()

    with contextlib.closing(urllib2.urlopen(url, context=context)) as jf:
        html_data = json.loads(jf.read())

    for info in html_data:
        Row(info['cinema']['shortTitle'].encode('utf-8'),
            '(/c{}m{})'.format(info['cinema']['id'], info['movie']['id']))

    if not html_data:
        render_to_string('no_seances.md')
    return render_to_string('seances.md', {})


def _display_cinema_seances(cinema_id, movie_id):
    url = settings.URL_CINEMA_SEANCES.format(
        cinema_id, settings.KINOHOD_API_KEY
    )

    context = ssl._create_unverified_context()

    with contextlib.closing(urllib2.urlopen(url, context=context)) as hd:
        html_data = json.loads(hd.read())

    f = namedtuple('f', ['tip', 'time', 'minPrice', 'id'])
    for info in html_data:
        if int(movie_id) != int(info['movie']['id']):
            continue

        seances = [f(settings.SIGN_TIP, s['time'], s['minPrice'], s['id'])
                   for s in info['schedules']]

        return render_to_string(
            'cinema_seances.md',
            {'title': info['movie']['title'], 'seances': seances}
        )


class CommandReceiveView(View):

    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': _display_help,
            '/movies': _display_running_movies,
            '/info': _display_movie_info,
        }

        raw = request.body.decode('utf-8')
        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:

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
                    hall_image = draw_cinemahall(schedule_id)
                    TelegramBot.sendChatAction(chat_id, 'upload_photo')
                    TelegramBot.sendPhoto(
                        chat_id,
                        ('hall.bmp', hall_image)
                    )
                    city_name_dict = {'cityName': u'Москва'.encode('utf-8')}
                    url_encoded_dict = urllib.urlencode(city_name_dict)
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [dict(text='Купить билеты',
                              url=('https://kinohod.ru/widget/?{}'
                                   '#scheme_{}'.format(url_encoded_dict,
                                                       schedule_id)))]
                    ])
                    TelegramBot.sendMessage(
                        chat_id,
                        'Серые - занято. Синие - свободно.',
                        reply_markup=markup, )
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

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args,
                                                        **kwargs)
