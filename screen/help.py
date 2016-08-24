# coding: utf-8

import settings


def display_help():
    template = settings.JINJA_ENVIRONMENT.get_template('help.md')
    return template.render({'help': settings.SIGN_SMILE_HELP})
