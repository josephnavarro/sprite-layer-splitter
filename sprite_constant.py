#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Definitions of constant values.

"""
import os
from namedenumiter import NamedEnumIter

""" 
Colors to avoid copying at all. 
"""
IGNORED_COLORS = [
    0x00,  # Black
    0xFF,  # White
]

"""
Various source directories.
"""
DIRECTORIES = {
    "input":  {
        "root": os.path.join("inputs", ""),
        "body": os.path.join("inputs", "images", "body"),
        "head": os.path.join("inputs", "images", "head"),
    },
    "output": {
        "root": os.path.join("outputs", ""),
    }
}

""" 
Root spritesheet output directory. 
"""
ROOT_OUTPUT_DIR = os.path.join("outputs", "")

""" 
Recognized file types.
"""
FILETYPES = [
    ("PNG", "*.png"),
    ("JPEG", "*.jpg; *.jpeg; *.jpe; *.jfif; *.exif"),
    ("BMP", "*.bmp; *.dib; *.rle"),
    ("TIFF", "*.tiff; *.tif"),
    ("GIF", "*.gif"),
    ("TGA", "*.tga"),
    ("DirectDraw Surface (DDS)", "*.dds"),
]

""" 
Recognized color names. 
"""
COLORS = NamedEnumIter(
    "blue",
    "red",
    "green",
    "purple",
)

"""
Recognized sprite profiles.
"""
PROFILES = NamedEnumIter(
    "echoes",
    "fates",
)

""" 
Recognized sprite states. 
"""
STATES = NamedEnumIter(
    "idle",
    "left",
    "right",
)

""" 
Dimensions of complete head region (layer mask and sprites). 
"""
REGION_FULL_HEAD = [256, 192]

"""
Dimensions of complete body region (layer mask and sprites).
"""
REGION_FULL_BODY = [256, 96]

"""
Dimensions of a state region (e.g. idle/left/right).
"""
STATE_REGION = [128, 32]

"""
Dimensions of a color region.
"""
COLOR_REGION = [STATE_REGION[0], STATE_REGION[1] * len(STATES)]

"""
Vertical distance between color regions on 'body' sheet.
"""
BODY_BLOCK = 96

"""
Vertical distance between color regions on 'head' sheet.
"""
HEAD_BLOCK = 192

"""
Default set of per-frame X-Y offsets.
"""
BASE_OFFSETS = [(0, 0), (0, 0), (0, 0), (0, 0)]

"""
Default frame pasting order.
"""
BASE_ORDER = [0, 1, 2, 3]
