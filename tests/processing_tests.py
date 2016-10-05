# coding: utf-8

import unittest

from datetime import datetime, timedelta
from mock import Mock

from processing.parser import Parser


class ParserTests(unittest.TestCase):

    def setUp(self):
        self.bot = Mock('telepot.Bot', name='telegram_bot')
        self.chat_id = 0
        self.t_uid = 0

        self.film_names, self.places = self.gen_films_places()

    def preprocess_fo_what(self, info):
        for text, r in info.iteritems():
            parser = Parser(text, 'film')
            parser.parse()

            self.assertTrue(
                len(parser.data.what) > 0,
                msg='cannot recognize text'
            )

            count = 0
            for w in parser.data.what:
                title = w['title'].lower().encode('utf-8')
                # not soft variant
                # self.assertTrue(
                #     title.find(r.lower()) > -1,
                #     msg='title={} does not consist text={}'.format(title, r)
                # )

                if title.find(r.lower()) > -1:
                    count += 1

            self.assertTrue(count > 0, msg='true variant does not exist')

    def preprocess_for_place(self, info):
        for text, r in info.iteritems():
            parser = Parser(text, 'base')
            parser.parse()

            self.assertIsNotNone(
                parser.data.place, msg='does not detect place correctly'
            )

            for p in parser.data.place:
                place = p['shortTitle'], p['address'], p['mall']
                place = [c.lower().encode('utf-8') for c in place if c]
                self.assertTrue(
                    sum(
                        [(1 if c.find(r.lower()) > -1 else 0) for c in place]
                    ) > 0,
                    msg='error, result: {} enter: {}'.format(
                        r, ' '.join(place)
                    )
                )

    def preprocess_when(self, info):
        for text, r in info.iteritems():
            parser = Parser(text, 'time')
            time = parser.parse()

            parser.data.when = time[0]
            self.assertIsNotNone(parser.data.when)

            self.assertTrue(
                parser.data.when.strftime('%d%m') == r.strftime('%d%m'),
                msg='recognition is not correct {} {} in msg={}'.format(
                    parser.data.when.strftime('%d%m'),
                    r.strftime('%d%m'),
                    text
                )
            )

    def gen_info(self, info, index, as_list=True):
        # if as_list:
        return {k: v[index] for k, v in info.iteritems()}

    def week_day(self, p):
        d = datetime.utcnow()
        if d.isoweekday() > p:
            return d + timedelta(days=(7 - d.isoweekday() + 1 + p))
        return d + timedelta(days=p)

    def gen_films_places(self):
        from processing.parser import get_data
        films, places = get_data('base')

        film_names = [title for title, f in films.iteritems()]

        return film_names, places.keys()

    def gen_info_film(self, info):
        from random import randint
        from math import ceil

        film_names = self.film_names[:]
        new_info = {}
        for k, v in info.iteritems():
            name = film_names.pop()
            splitted_name = name.split()

            c = len(splitted_name)
            future_k = ''
            for i in xrange(int(ceil(c / 2.))):
                r_ind = randint(0, len(splitted_name) - 1)
                future_k += splitted_name[r_ind].lower().encode('utf-8') + ' '
                splitted_name.pop(r_ind)

            if isinstance(v, (str, unicode)):
                new_info[k.format(future_k)] = name.lower().encode('utf-8')
            else:
                v[0] = name.lower().encode('utf-8')
                new_info[k.format(future_k)] = v
        return new_info

    def test_parse_what(self):
        """
        just soft test for film detection
        """

        info = {
            'хочу билет на {}': '{}',
            'билет на {}': '{}',
            'взять {} парочку': '{}',
            'хочу на {}': '{}'
        }

        new_info = self.gen_info_film(info)
        self.preprocess_fo_what(new_info)

    def test_category_detection(self):
        """
        now it is not useful test
        """
        pass

    def test_signle_place(self):
        """
        test location detection without film detection
        """

        info = {
            'на павелецкой': 'павелецк',
            'павелецкая': 'павелецк',
            'на арбате': 'арбат',
            'на октябрьской': 'октябрь',
            'ночь с друзьями в пионере': 'пионер'
        }

        self.preprocess_for_place(info)

    def test_when(self):
        """
        detect time recognition all of types.
        """

        from processing.mapping import week_when
        now = datetime.utcnow()
        info = {
            'купить билет на завтра': (now + timedelta(days=1)),
            'билет на что-то на сегодня': now,
            'хочу в кино в понедельник':
                self.week_day(week_when['понедельник'])
        }

        self.preprocess_when(info)

    def test_combination_what_place(self):
        info = {
            'хочу билет на {} на павелецкой': [{}, 'павелецк'],
            '{} на арбате': ['{}', 'арбат'],
            '{} в пионер завтра':
                ['{}', 'пионер']
        }

        info = self.gen_info_film(info)
        for text, r in info.iteritems():
            parser = Parser(text, 'base')
            parser.parse()

            self.assertIsNotNone(parser.data.what, 'film cannot be detected')
            self.assertIsNotNone(parser.data.place, 'place cannot be detected')

            # make soft film detection - it is mean only that one of
            #  result illustrates true results

        self.preprocess_fo_what(self.gen_info(info, 0))
        self.preprocess_for_place(self.gen_info(info, 1))

    def test_combination_what_place_when(self):

        from processing.mapping import week_when
        now = datetime.utcnow()
        info = {
            'хочу билет на {} на павелецкой сегодня':
                ['{}', 'павелецк', now],
            '{} на арбате в понедельник':
                ['{}', 'арбат', self.week_day(week_when['понедельник'])],
            '{} в пионер завтра':
                ['{}', 'пионер', datetime.utcnow() + timedelta(days=1)]
        }

        info = self.gen_info_film(info)
        self.preprocess_fo_what(self.gen_info(info, 0))
        self.preprocess_for_place(self.gen_info(info, 1))
        self.preprocess_when(self.gen_info(info, 2, as_list=False))

    def test_film_search(self):
        """
        it should work as search of films
        """
        info = self.gen_info_film({'{}': '{}', '{}': '{}', '{}': '{}'})
        self.preprocess_fo_what(info)

    def test_time_detection(self):

        texts = {
            '1.10': datetime.now().replace(day=1, month=10),
            '01:10':  datetime.now().replace(day=1, month=10),
            '1:09':  datetime.now().replace(day=1, month=9),
            '1 сентября':  datetime.now().replace(day=1, month=9),
            'завтра':  datetime.now() + timedelta(days=1),
            '3.10':  datetime.now().replace(day=3, month=10),
        }

        for t, v in texts.iteritems():
            predict = Parser.detect_time(t)
            self.assertTrue(
                predict.date() == v.date(),
                msg='error text: {} != {} predicted: {}'.format(t, v, predict))

if __name__ == '__main__':
    unittest.main()
