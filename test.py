#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

PATH_TO  = 'inputs/'
FILETYPE = '.png'
INPUTS   = [
    ('azura', 'head', 'small'),
    ('azura', 'head', 'large'),
    ('ballistician', 'body', None),
    ('bowknight',    'body', None),
    
    ]

for input in INPUTS:
    name, type, size = input
    fn = PATH_TO + name + FILETYPE
    splitter.process(fn, name, type, size)
