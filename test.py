#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

splitter.main(
    'inputs/camilla.png',
    'inputs/malig-knight-m.png',
    'small',
    'camilla-malig-knight',
    )


splitter.main(
    'inputs/camilla.png',
    'inputs/hero.png',
    'large',
    'camilla-hero',
    )
