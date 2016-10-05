# coding utf-8

from math import sin, cos, pi, sqrt, atan2


def distance(latitude_f, longitude_f, latitude_s, longitude_s):
    radius = 6371008.7714150598

    dLat = (latitude_s - latitude_f) * pi / 180
    dLng = (longitude_s - longitude_f) * pi / 180

    latitude_f = latitude_f * pi / 180
    latitude_s = latitude_s * pi / 180

    value = (sin(dLat/2) * sin(dLat/2) + sin(dLng/2) *
             sin(dLng/2) * cos(latitude_f) * cos(latitude_s))

    angle = 2 * atan2(sqrt(value), sqrt(1 - value))

    return radius * angle
