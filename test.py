#!usr/bin/env python3
import splitter, glob, os

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

for fn in glob.glob('inputs/*.png'):
    base = os.path.basename(fn)
    name,ext = os.path.splitext(base)
    splitter.process(fn, name)
