# coding: utf-8

import settings


def get_help():
    template = settings.JINJA_ENVIRONMENT.get_template('help.md')
    return template.render({
        'write': settings.SIGN_WRITE,
        'help': settings.SIGN_SMILE_HELP,
        'clipsign': settings.SIGN_CLIP
    })
