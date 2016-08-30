# coding: utf-8

import contextlib
import gzip
import urllib2
import json

from StringIO import StringIO

import pymorphy2


from mapping import categories, stop_words
from maching import damerau_levenshtein_distance
import settings


morph = pymorphy2.MorphAnalyzer()

MIN_VERB_LEN = 5


def _substr_sentence(text, ignore):
    return [w for w in text if w not in ignore]


def detect_category(spltd):
    conf_n = {k: [morph.parse(w.decode('utf-8'))[0].normal_form for w in v]
              for k, v in categories.iteritems()}

    determ_category = {k: [0, []] for k, v in conf_n.iteritems()}

    for cat, value in conf_n.iteritems():
        for verb in value:
            for w in spltd:
                if (len(w) >= (MIN_VERB_LEN - 1) and
                        damerau_levenshtein_distance(w, verb) < 2):
                    determ_category[cat][0] += 1
                    determ_category[cat][1].append(w)

    cat = max((v, k) for k, v in determ_category.iteritems())
    if cat[0][0] > 0:
        spltd = [w for w in spltd if w not in cat[0][1]]
        return cat[1], spltd
    return None, None


def parser(text):
    category = {
        'buy': parse_film,
        'info': parse_info
    }

    cmds = {'category': None, 'place': None, 'what': None}

    splitted = [morph.parse(w.decode('utf-8'))[0].normal_form
                for w in text.split(' ') if text]

    sw_decode = [w.decode('utf-8') for w in stop_words]
    splitted = [w for w in splitted if w not in sw_decode]

    if splitted:
        cat, splitted = detect_category(splitted)
        cmds['category'] = cat

    film_names, places = get_films()
    if splitted:
        f_names, splitted = category[cat](splitted, film_names.keys())
        cmds['what'] = [film_names[f] for f in f_names] if f_names else None

    if splitted:
        candidate = determine_place(splitted, places.keys())
        cmds['place'] = [places[p] for p in candidate]
    return cmds


def parse_film(spltd, film_names):

    def film_similarity(f, s):
        return True if f.find(s) > -1 else False

    splitted = [w for w in spltd if len(w) > 2]
    candidate = {i: 0 for i, f_name in enumerate(film_names)}
    new_spltd = set()
    for i, f_name in enumerate(film_names):
        f_name = morph.parse(f_name.lower())[0].normal_form
        for w in splitted:
            if film_similarity(f_name, w):
                candidate[i] += 1
                new_spltd.add(w)

    new_spltd = list(new_spltd)

    return ([film_names[k] for k, v in candidate.iteritems() if v > 0],
            [w for w in spltd if w not in new_spltd])


def determine_place(spltd, places):
    candidate = set()
    for w in spltd:
        for place_name in places:
            ps = place_name.lower().split(' ')
            for p in ps:
                # print p, w
                if (len(w) > 2 and len(p) > 2 and
                        damerau_levenshtein_distance(p, w) < 3):
                    candidate.add(place_name)
                    break
    return candidate


def parse_info(spltd):
    return None


def get_films():
    url_movies = settings.URL_RUNNING_MOVIES.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url_movies)) as jf:
        m_stream = gzip.GzipFile(fileobj=StringIO(jf.read()), mode='rb')
        data = json.loads(m_stream.read())

    film_names = {}
    for film in data:
        film_names[film['title']] = film

    url_cinema = settings.URL_CINEMAS.format(settings.KINOHOD_API_KEY)
    with contextlib.closing(urllib2.urlopen(url_cinema)) as jf:
        data_places = json.loads(jf.read())

    places = {}
    for cinema in data_places:
        places[cinema['shortTitle']] = cinema

    return film_names, places

# request = 'хочу купить билет в кино на механик на новокузнецкой'
# from pprint import pprint
# pprint(parser(request))
