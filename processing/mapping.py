# coding: utf-8

from collections import OrderedDict

stop_words = [w.decode('utf-8')
              for w in ['кино', 'фильм', 'синема', 'парк',
                        'покупка', 'закупка', 'чем-то', 'завтра', 'послезавтра'
                        'что-нибудь', 'кто-нибудь', 'где-то',
                        'какое', 'какие', 'нибудь', 'как-то', 'что-то',
                        'какой', 'какие', 'как', 'кинцо']]

when_nearest = OrderedDict({
    ('сегодня', 'сейчас', 'ближайшее'): 0,
    ('послезавтра', ): 2,
    ('завтра', ): 1
})

when_week = {
    0: ['понедельник'],
    1: ['вторник'],
    2: ['среду', 'среда'],
    3: ['четверг'],
    4: ['пятниц', 'пятницу'],
    5: ['cуббот', 'суботу', 'субботу', 'суббота'],
    6: ['воскрес', 'воскресенье']
}

when_month = {
    'january': 'январь',
    'february': 'февраль',
    'march': 'март',
    'april': 'апрель',
    'may': 'май',
    'june': 'июнь',
    'july': 'июль',
    'august': 'август',
    'september': 'сентябрь',
    'october': 'октябрь',
    'november': 'ноябрь',
    'december': 'декабрь'
}


nearest_when = OrderedDict({})
for v, k in when_nearest.iteritems():
    for e in v:
        nearest_when[e] = k

week_when = {v[0]: k for k, v in when_week.iteritems()}

for ws in when_nearest.iterkeys():
    for w in ws:
        stop_words.append(w)

for ws in when_week.itervalues():
    for w in ws:
        stop_words.append(w)
