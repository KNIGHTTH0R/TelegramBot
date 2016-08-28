# coding: utf-8

import contextlib
import math
import gzip
import urllib2
import json

from cStringIO import StringIO

import pymorphy2

import settings


morph = pymorphy2.MorphAnalyzer()

categories = {
    'buy': ['купить', 'покупка', 'приобретение', 'приобрести', 'перекупить',
            'накупить', 'заплатить', 'подкупать', 'отовариться', 'взять',
            'достать', 'достань', 'затовариться', 'прикупить',
            'покупать', 'нарыть', 'закупить', 'закупать'],

    'info': ['расскажи', 'покажи', 'поведуй', 'поведай']
}

cinemas = ['ночные стражи', 'механик', 'дыши', 'пит дракон', 'служанка']

request = 'хочу купить билет в кино на механик на новокузнецкой'


def similarity(f, s):
    n = min(len(f), len(s))
    counter = 0
    for i in xrange(n):
        counter += 1 if f[i] != s[i] else 0
    return counter


def film_similarity(f, s):
    return True if f.find(s) > 0 else False


def parser(text):

    category = {
        'buy': parse_film,
        'info': parse_info
    }

    spltd = [morph.parse(w.decode('utf-8'))[0].normal_form
             for w in text.split(' ') if text]

    conf_n = {k: [morph.parse(w.decode('utf-8'))[0].normal_form for w in v]
              for k, v in categories.iteritems()}

    determ_category = {k: 0 for k, v in conf_n.iteritems()}
    for k, value in conf_n.iteritems():
        for verb in value:
            for w in spltd:
                if (math.fabs(len(w) - len(verb)) < 2 and
                        similarity(w, verb) < 2):
                    print w, verb
                    determ_category[k] += 1

    c = max((v, k) for k, v in determ_category.iteritems())[1]
    if c[0] > 0:
        category[c[1]](spltd.remove())


def parse_film(spltd):
    film_names = get_films()

    candidate = {f_name: 0 for f_name in film_names}
    for f_name in film_names:
        for w in spltd:
            if film_similarity(f_name, w):
                candidate[f_name] += 1

    f_name = max((v, k) for k, v in candidate.iteritems())[1]
    if f_name[0] > 0:
        determine_place(f_name)
    determine_place()


def determine_place(f_name=None):
    pass


def parse_info(spltd):
    print 'info'


def get_films():
    url_movies = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url_movies)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())
    return [film['title'] for film in data]

parser(request)
