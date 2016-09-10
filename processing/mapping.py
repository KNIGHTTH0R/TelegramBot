# coding: utf-8

categories = {
    'buy': ['купить', 'билет', 'покупка', 'приобретение',
            'приобрести', 'перекупить',
            'накупить', 'заплатить', 'подкупать', 'отовариться', 'взять',
            'достать', 'достань', 'затовариться', 'прикупить',
            'покупать', 'нарыть', 'закупить', 'закупать'],

    'info': ['расскажи', 'покажи', 'поведуй', 'поведай']
}

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