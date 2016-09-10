# coding: utf-8

from mock import patch, Mock

import settings


class Foo(object):
    # instance properties
    _fooValue = 123

    def callFoo(self):
        print "Foo:callFoo_"

    def doFoo(self, argValue):
        print "Foo:doFoo:input = ", argValue

    def detect_f(self, a, b):
        return int(a) + int(b)

mockFoo = Mock(spec=Foo, return_value=555)
print mockFoo()
# returns: 555

mockFoo.configure_mock(return_value=999)
print mockFoo()
# returns: 999


def function_side(a, b):
    return int(a) * int(b)

print hash(function_side)
print hash(function_side)

fooSpec = {
    'callFoo.return_value': "narf",
    'doFoo.return_value': "zort",
    'doFoo.side_effect': StandardError,
    'detect_f.side_effect': function_side
}

mockFoo.configure_mock(**fooSpec)

print mockFoo.detect_f('5', '6')

import logging
logging.info(msg='hey hey')

print mockFoo.callFoo()
# returns: narf
print mockFoo.doFoo("narf")
# raises: StandardError

fooSpec = {'doFoo.side_effect': None}
mockFoo.configure_mock(**fooSpec)
print mockFoo.doFoo("narf")
# returns: zort

