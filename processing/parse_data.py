# coding: utf-8


class Data(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)