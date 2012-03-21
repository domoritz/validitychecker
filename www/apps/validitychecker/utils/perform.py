#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date
import re

# a_ for one element
# m_ for map

a_first = lambda x: x[0] if x else ''
a_join = lambda x: ''.join(x)
a_split_komma = lambda x: x.split(',')
a_split_semicolon = lambda x: x.split(';')

def a_date(y):
    if y: # year may be 0 if nothing found
        d = date(y, 1, 1)
        return d
    else:
        return None

def a_find(string, pattern):
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        return ''

a_int = lambda i: int(i) if i else 0

def a_trim(n):
    n = n.strip()
    n = n.strip(u'…')
    return n

m_trim = lambda l: map(a_trim, l)

def perform(element, *functions):
    result = element
    for f in functions:
        result = f(result)
    return result

