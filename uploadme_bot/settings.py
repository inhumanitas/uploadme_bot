# coding: utf-8

try:
    token = open('.token').read().strip()
except IOError:
    token = None
