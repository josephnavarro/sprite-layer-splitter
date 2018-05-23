#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

FILE_STRING = 'inputs/{}.png'
UNIT_NAME = 'jakob'
CLASS_NAME = 'butler'

splitter.main(
    FILE_STRING.format(UNIT_NAME),
    FILE_STRING.format(CLASS_NAME),
    '{}_{}'.format(UNIT_NAME,CLASS_NAME),
    )
     
