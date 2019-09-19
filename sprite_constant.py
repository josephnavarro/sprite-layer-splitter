#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Definitions of constant values.

--------------------------------------------------------------------------------
"""
import os
from namedenumiter import NamedEnumIter


""" 
Colors to avoid copying at all. 
"""
IGNORED_COLORS: list = [
    0x00,  # Black
    0xFF,  # White
    ]

"""
Root input directory.
"""
ROOT_INPUT_DIR: str = os.path.join("inputs", "")

""" 
Root spritesheet output directory. 
"""
ROOT_OUTPUT_DIR: str = os.path.join("outputs", "")

""" 
Recognized file types.
"""
FILETYPES: list = [
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
REGION_FULL_HEAD: list = [256, 192]

"""
Dimensions of complete body region (layer mask and sprites).
"""
REGION_FULL_BODY: list = [256, 96]

"""
Dimensions of a state region (e.g. idle/left/right).
"""
STATE_REGION: list = [128, 32]

"""
Dimensions of a color region.
"""
COLOR_REGION: list = [STATE_REGION[0], STATE_REGION[1] * len(STATES)]

"""
Vertical distance between color regions on 'body' sheet.
"""
BODY_BLOCK: int = 96

"""
Vertical distance between color regions on 'head' sheet.
"""
HEAD_BLOCK: int = 192

"""
Default set of per-frame X-Y offsets.
"""
BASE_OFFSETS: list = [(0, 0), (0, 0), (0, 0), (0, 0)]

"""
Default frame pasting order.
"""
BASE_ORDER: list = [0, 1, 2, 3]