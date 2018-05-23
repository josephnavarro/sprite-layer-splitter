#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

splitter.main(
    'inputs/niles.png',
    'inputs/adventurer-m.png',
    'large',
    'testing',
    )
