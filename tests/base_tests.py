# coding: utf-8

import unittest

from mock import Mock

import telepot

from commands import (display_help, display_seances_cinema, display_info,
                      display_movies, display_info_full, display_nearest,
                      display_cinema, display_schedule, display_seance)

from views import detect_instruction, make_instruction

import settings


class SlashCommandTests(unittest.TestCase):

    def mock_send_message(self, chat_id, text, parse_mode=None,
                          disable_web_page_preview=None,
                          disable_notification=None, reply_to_message_id=None,
                          reply_markup=None):
        print 'chat_id={} and msg={}'.format(chat_id, text)
        return 'message'

    def setUp(self):
        self.telegram_bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

    def test_make_instruction(self):
        from collections import OrderedDict
        self.assertTrue(isinstance(make_instruction(), OrderedDict))

    def test_command_detection(self):
        instructions = make_instruction()

        cmds = {
            '/info123': display_info,
            '/info_full123': display_info_full,
            '/info': display_info,
            '/help': display_help,
            '/c123m321': display_seances_cinema,
            '/cinema': display_cinema
        }

        for k, v in cmds.iteritems():
            self.assertTrue(
                detect_instruction(instructions, k).__name__ == v.__name__,
                msg='text={} and command={} detected {}'.format(
                    k, v.__name__, detect_instruction(instructions, k).__name__
                )
            )

        self.assertIsNone(detect_instruction(cmds, 'help'))

    def test_start(self):
        """
        display start screen 'help.md'
        """
        bot = Mock(spec=telepot.Bot)

        bot_spec = {
            'sendMessage.side_effect': self.mock_send_message
        }

        bot.configure_mock(**bot_spec)

        display_help(bot, {}, 'cmd', 1)
        bot.assert_called_once()

        # display_help(self.telegram_bot, {}, '', 1)
        # self.telegram_bot.assert_called_once()

    def test_help(self):
        """
        as /start command, but another link
        """
        self.test_start()

    def test_running_movie(self):
        """
        display name of the films
        """
        bot = Mock(spec=telepot.Bot)

        bot_spec = {
            'sendMessage.side_effect': self.mock_send_message,
        }

        bot.configure_mock(**bot_spec)

        display_movies(
            bot, {'callback_query': True}, '/movies', 1
        )

        bot.assert_called_once()

    def test_schedule(self):
        """
        display a schedule for the film that was chosen before
        """
        pass

    def test_cinemas(self):
        """
        display cinemas near to you
        """
        pass

    def test_nearest(self):
        """
        detect location and then emulate nearest cinemas illustration
        """

    def test_supports(self):
        """
        scenarios of support which should be decomposed later
        """
        pass

    def test_cinema_seances(self):
        """
        display illustration of seances in one cinema
        """
        pass

    def test_info_full(self):
        """
        display instruction of film info getting
        """
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()