# coding: utf-8
from __future__ import generators

from collections import defaultdict

import numpy as np


def damerau_levenshtein_distance(a, b):

    da = defaultdict(int)
    max_dist = len(a) + len(b)
    score = np.zeros((len(a) + 2, len(b) + 2))
    score[0, 0] = max_dist

    for i in xrange(len(a) + 1):
        score[i + 1, 0], score[i + 1, 1] = max_dist, i

    for i in xrange(len(b) + 1):
        score[0, i + 1], score[1, i + 1] = max_dist, i

    for i in xrange(1, len(a) + 1):
        db = 0
        for j in xrange(1, len(b) + 1):
            fi, se = da[b[j - 1]], db
            cost = 1
            if a[i - 1] == b[j - 1]:
                cost = 0
                db = j

            score[i + 1, j + 1] = min(
                score[i, j] + cost,
                score[i + 1, j] + 1,
                score[i, j + 1] + 1,
                score[fi, se] + (i - fi - 1) + 1 + (j - se - 1))
        da[a[i - 1]] = i

    return score[len(a) + 1, len(b) + 1]


def naive_match(pattern, text):
    for start_pos in xrange(len(text) - len(pattern) + 1):
        match_len = 0
        while pattern[match_len] == text[start_pos + match_len]:
            match_len += 1
            if match_len == len(pattern):
                return start_pos


def kmp_first_match(pattern, text):
    shift = compute_shifts(pattern)
    start_pos = 0
    match_len = 0
    for c in text:
        while match_len >= 0 and pattern[match_len] != c:
            start_pos += shift[match_len]
            match_len -= shift[match_len]
        match_len += 1
        if match_len == len(pattern):
            return start_pos


def kmp_all_matches(pattern, text):
    shift = compute_shifts(pattern)
    start_pos = 0
    match_len = 0
    for c in text:
        while match_len >= 0 and pattern[match_len] != c:
            start_pos += shift[match_len]
            match_len -= shift[match_len]
        match_len += 1
        if match_len == len(pattern):
            yield start_pos
            start_pos += shift[match_len]
            match_len -= shift[match_len]


def compute_shifts(pattern):
    shifts = [None] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern) + 1):
        while shift < pos and pattern[pos-1] != pattern[pos-shift-1]:
            shift += shifts[pos-shift-1]
        shifts[pos] = shift
    return shifts
