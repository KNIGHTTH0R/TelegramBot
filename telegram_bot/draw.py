# coding: utf-8

import ssl
import json
import tempfile
import urllib2

from rexec import FileWrapper

import numpy as np
import scipy.misc as smp

from PIL import ImageDraw

from settings import CINEMA_HALL, KINOHOD_API_KEY, SIGN_RUB

FILL_HARD_GREY = (138, 138, 138, 64)
FILL_GREY = (158, 158, 158, 64)
FILL_BLACK = (100, 100, 100, 64)
LIGHT_GREY = [221, 221, 221]
ORANGE = [255, 180, 0]
BLUE = [1, 137, 243]


def draw_seat_numbers(draw, section, x_offset, y_offset):

    import sys

    min_x, max_x = sys.maxint, -1
    for seat in section['seats']:
        seat_x = int(seat['x'])
        if seat_x < min_x:
            min_x = seat_x
        if seat_x > max_x:
            max_x = seat_x

    for seat in section['seats']:
        seat_width = int(seat['width'])
        seat_height = int(seat['height'])

        if int(seat['number']) == 1:
            draw.text((x_offset + min_x - 1. * seat_width,
                       int(seat['y']) + y_offset - seat_height / 3),
                      str(seat['row']),
                      fill=(138, 138, 138, 64))
            draw.text((x_offset + max_x + seat_width,
                       int(seat['y']) + y_offset - seat_height / 3),
                      str(seat['row']),
                      fill=FILL_HARD_GREY)


def draw_window(draw, picture_width, x_offset, y_offset):
    draw.polygon([(2 * x_offset, y_offset - x_offset / 2),
                  (picture_width - 2 * x_offset, y_offset - x_offset / 2),
                  (picture_width - 2 * x_offset, y_offset),
                  (2 * x_offset, y_offset)],
                 fill=FILL_GREY)


def draw_cinemahall(schedule_id):

    url = CINEMA_HALL.format(schedule_id, KINOHOD_API_KEY)

    x_offset = 15
    y_offset = 30
    shift = 10

    context = ssl._create_unverified_context()

    html_data = json.loads(urllib2.urlopen(url, context=context).read())

    for info in html_data:
        for section in info['sections']:
            picture_width = int(section['width']) + 2 * x_offset
            picture_height = int(section['height']) + y_offset
            data = np.zeros((picture_height, picture_width, 3),
                            dtype=np.uint8)
            data[:, :] = [242, 242, 242]

            low_price, high_price = 0, 0

            for counter, seat in enumerate(section['seats']):
                x, y = (int(seat['x']) + x_offset + shift / 2,
                        int(seat['y']) + y_offset)
                if counter == 1:
                    low_price_x = x
                elif counter == 5:
                    high_price_x = x

                seat_height, seat_width = (int(seat['height']),
                                           int(seat['width']))
                if seat['status'] == 'vacant':
                    if seat['class'] == 'color1':
                        low_price = seat['price']
                        data[y - seat_height / 2: y + seat_height / 2,
                             x - seat_width / 2:
                             x + seat_width / 2] = BLUE
                    if seat['class'] == 'color2':
                        high_price = seat['price']
                        data[y - seat_height / 2: y + seat_height / 2,
                             x - seat_width / 2:
                             x + seat_width / 2] = ORANGE

                else:
                    data[y - seat_height/2: y + seat_height/2,
                         x - seat_width/2: x + seat_width/2] = LIGHT_GREY

            # draw price icons
            data[picture_height - int(1.25 * seat_height):
                 picture_height - int(.25 * seat_height),
                 low_price_x - seat_width / 2:
                 low_price_x + seat_width / 2] = BLUE

            data[picture_height - int(1.25 * seat_height):
                 picture_height - int(.25 * seat_height),
                 high_price_x - seat_width / 2:
                 high_price_x + seat_width / 2] = ORANGE

            img = smp.toimage(data)
            draw = ImageDraw.Draw(img)
            draw_seat_numbers(draw, section, x_offset, y_offset)

            # draw price texts
            draw.text((low_price_x + seat_width,
                       picture_height - int(1. * seat_height)),
                      '{} {}'.format(low_price, SIGN_RUB),
                      fill=FILL_BLACK)

            high_str = ('' if high_price == 0 or high_price <= low_price
                        else '{} {}'.format(high_price, SIGN_RUB))

            draw.text((high_price_x + seat_width,
                       picture_height - int(1. * seat_height)),
                      high_str,
                      fill=FILL_BLACK)

            draw_window(draw, picture_width, x_offset, y_offset)


    tmpfile = tempfile.TemporaryFile()
    img.save(tmpfile, format='bmp', quality=80)
    tmpfile.seek(0)
    wrapper = FileWrapper(tmpfile)
    return wrapper
