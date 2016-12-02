# coding: utf-8

import json

from model.base import get_model
from model.base import UserProfile
from data import get_schedule, get_url_json

import settings


def detect_city_id_by_location(location):
    url = settings.URL_CITY_ID_BY_LOC.format(
        settings.URL_CITIES,
        settings.KINOHOD_API_KEY,
        location.get('latitude'), location.get('longitude')
    )

    data = get_url_json(url)
    if data and 'id' in data[0]:
        return int(data[0]['id'])

    return 1  # Id for Moscow


def detect_city_by_chat(chat_id):
    city_id = 1

    if chat_id:
        u = get_model(UserProfile, chat_id)
        if u and u.location:
            l = json.loads(u.location)
            city_id = detect_city_id_by_location(l)
    return city_id


def detect_film_cinemas(chat_id, movie_id, date=None):
    city_id = detect_city_by_chat(chat_id)
    return get_schedule(movie_id, date=date, city_id=city_id), city_id

