#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

splitter.main(
    'inputs/anna.png',
    'inputs/adventurer-f.png',
    'large',
    'anna-adventurer',
    )


splitter.main(
    'inputs/selena.png',
    'inputs/hero-f.png',
    'large',
    'selena-hero',
    )

splitter.main(
    'inputs/anna.png',
    'inputs/hero-f.png',
    'large',
    'anna-hero',
    )


splitter.main(
    'inputs/anna.png',
    'inputs/bow-knight.png',
    'small',
    'anna-bow-knight',
    )

splitter.main(
    'inputs/anna.png',
    'inputs/dark-knight.png',
    'small',
    'anna-dark-knight',
    )

splitter.main(
    'inputs/anna.png',
    'inputs/falcon-knight.png',
    'small',
    'anna-falcon-knight',
    )

splitter.main(
    'inputs/anna.png',
    'inputs/general.png',
    'large',
    'anna-general',
    )


splitter.main(
    'inputs/anna.png',
    'inputs/malig-knight-m.png',
    'small',
    'anna-malig-knight',
    )


