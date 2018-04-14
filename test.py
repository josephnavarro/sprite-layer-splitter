#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

PATH_TO  = 'inputs/'
FILETYPE = '.png'
HEAD = 'azura', 'azura', 'head', 'small'
BODY = 'bowknight', 'bowknight', 'body', None

file, name, type, size = HEAD
file = PATH_TO + file + FILETYPE
head = file, name, type, size

file, name, type, size = BODY
file = PATH_TO + file + FILETYPE
body = file, name, type, size

splitter.main(head, body)
