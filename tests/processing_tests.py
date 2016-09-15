# coding: utf-8

import unittest

from datetime import datetime, timedelta
from mock import Mock

from processing.parser import parser


class ParserTests(unittest.TestCase):

    def setUp(self):
        self.bot = Mock('telepot.Bot', name='telegram_bot')
        self.chat_id = 0
        self.t_uid = 0

    def preprocess_fo_what(self, info):
        for text, r in info.iteritems():
            cmds = parser(text)

            self.assertTrue(len(cmds['what']) > 0, msg='cannot recognize text')

            count = 0
            for w in cmds['what']:
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
            cmds = parser(text)

            self.assertIsNotNone(
                cmds['place'], msg='does not detect place correctly'
            )

            for p in cmds['place']:
                location = p['shortTitle'].lower().encode('utf-8')
                self.assertTrue(
                    (location.find(r.lower()) > -1),
                    msg='one of examples was not detected: {} vs {}'.format(
                        location, r
                    )
                )

    def preprocess_when(self, info):
        for text, r in info.iteritems():
            cmds = parser(text)

            self.assertIsNotNone(cmds['when'])

            self.assertTrue(
                cmds['when'].strftime('%d%m') == r.strftime('%d%m'),
                msg='recognition is not correct {} {} in msg={}'.format(
                    (cmds['when']).strftime('%d%m'), r.strftime('%d%m'), text
                )
            )

    def gen_info(self, info, index, as_list=True):
        # if as_list:
        return {k: v[index] for k, v in info.iteritems()}
        # return {k: v[index] for k, v in info.iteritems()}

    def week_day(self, p):
        d = datetime.utcnow()
        if d.isoweekday() > p:
            return d + timedelta(days=(7 - d.isoweekday() + 1 + p))
        return d + timedelta(days=p)

    def test_parse_what(self):
        """
        just soft test for film detection
        """

        info = {
            'хочу билет на борн': 'борн',
            'билет на Бен-Гур': 'бен-гур',
            'взять Гамба парочку': 'гамба',
            'хочу на жизнь домашних животных': 'тайная жизнь домашних животных'
        }

        self.preprocess_fo_what(info)

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
            'хочу билет на механика на павелецкой': ['механик', 'павелецк'],
            'борн на арбате': ['борн', 'арбат'],
            'жизнь домашних животных в пионер завтра':
                ['тайная жизнь домашних животных', 'пионер']
        }

        for text, r in info.iteritems():
            cmds = parser(text)

            self.assertIsNotNone(cmds['what'], 'film cannot be detected')
            self.assertIsNotNone(cmds['place'], 'place cannot be detected')

            # make soft film detection - it is mean only that one of
            #  result illustrates true results

            self.preprocess_fo_what(self.gen_info(info, 0))
            self.preprocess_for_place(self.gen_info(info, 1))

    def test_combination_what_place_when(self):

        from processing.mapping import week_when
        now = datetime.utcnow()
        info = {
            'хочу билет на механика на павелецкой сегодня':
                ['механик', 'павелецк', now],
            'борн на арбате в понедельник':
                ['борн', 'арбат', self.week_day(week_when['понедельник'])],
            'жизнь домашних животных в пионер завтра':
                ['тайная жизнь домашних животных', 'пионер',
                 datetime.utcnow() + timedelta(days=1)]
        }

        self.preprocess_fo_what(self.gen_info(info, 0))
        self.preprocess_for_place(self.gen_info(info, 1))
        self.preprocess_when(self.gen_info(info, 2, as_list=False))

    def test_film_search(self):
        """
        it should work as search of films
        """
        info = {
            'борн': 'борн',
            'жизнь домашних животных': 'тайная жизнь домашних животных',
            'бен': 'бен-гур'
        }

        self.preprocess_fo_what(info)


if __name__ == '__main__':
    unittest.main()
