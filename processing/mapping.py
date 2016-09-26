# coding: utf-8


stop_words = ['кино', 'фильм', 'покупка', 'закупка']

when_nearest = {
    0: ['сегодня', 'сейчас', 'ближайшие'],
    1: ['завтра'],
    2: ['послезавтра']
}

when_week = {
    0: ['понедельник'],
    1: ['вторник'],
    2: ['среду', 'среда'],
    3: ['четверг'],
    4: ['пятницу', 'пятница'],
    5: ['cубботу', 'суббота'],
    6: ['воскресенье']
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


nearest_when = {}
for k, v in when_nearest.iteritems():
    for e in v:
        nearest_when[e] = k

week_when = {v[0]: k for k, v in when_week.iteritems()}

for ws in when_nearest.itervalues():
    for w in ws:
        stop_words.append(w)

for ws in when_week.itervalues():
    for w in ws:
        stop_words.append(w)
