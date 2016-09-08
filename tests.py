# coding: utf-8

import unittest

import telepot

import settings


class SlashCommandTests(unittest.TestCase):

    def setUp(self):
        self.telegram_bot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

    def start_test(self):
        """
        display start screen 'help.md'
        """
        pass

    def help_test(self):
        """
        as /start command, but another link
        """

    def running_movie_test(self):
        """
        display name of the films
        """
        pass

    def schedule_test(self):
        """
        display a schedule for the film that was chosen before
        """
        pass

    def cinemas_test(self):
        """
        display cinemas near to you
        """
        pass

    def nearest_test(self):
        """
        detect location and then emulate nearest cinemas illustration
        """

    def supports_test(self):
        """
        scenarios of support which should be decomposed later
        """
        pass

    def cinema_seances_test(self):
        """
        display illustration of seances in one cinema
        """
        pass

    def info_full_test(self):
        """
        display instruction of film info getting
        """
        pass

    def tearDown(self):
        pass
