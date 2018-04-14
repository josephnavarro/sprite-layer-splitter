#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

PATH_TO  = 'inputs/'
FILETYPE = '.png'
HEAD = 'odin', 'odin', 'head'
BODY = 'bowknight', 'bowknight', 'body'

file, name, type = HEAD
file = PATH_TO + file + FILETYPE
head = file, name, type

file, name, type = BODY
file = PATH_TO + file + FILETYPE
body = file, name, type

splitter.main(head, body, 'small')
