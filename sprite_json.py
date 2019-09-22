#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Utilities for reading and writing local JSON files.

"""
import json
import glob
from sprite_utils import *

TEMPLATE_JSON_BASE = "{{{}}}"
TEMPLATE_JSON_HEAD = "\"{name}\": {{" \
                     "\"path\": [\"images\", \"head\", \"{name}.png\"]," \
                     "\"name\": \"{full}\"" \
                     "}},"
TEMPLATE_JSON_BODY = "\"{name}\": {{" \
                     "\"path\": [\"images\", \"body\", \"{name}.png\"]," \
                     "\"name\": \"{full}\"" \
                     "}},"

HEAD_DIRECTORY = os.path.join("inputs", "images", "head")
BODY_DIRECTORY = os.path.join("inputs", "images", "body")

IMPATH_DIRECTORY = os.path.join("inputs", "paths")
OFFSET_DIRECTORY = os.path.join("inputs", "offsets")
SOURCE_DIRECTORY = os.path.join("inputs", "sources")

JSON_IMPATH_HEAD = os.path.join(IMPATH_DIRECTORY, "head.json")
JSON_IMPATH_BODY = os.path.join(IMPATH_DIRECTORY, "body.json")
JSON_OFFSET_HEAD = os.path.join(OFFSET_DIRECTORY, "head_offsets.json")
JSON_OFFSET_BODY = os.path.join(OFFSET_DIRECTORY, "body_offsets.json")
JSON_SOURCE_COLR = os.path.join(SOURCE_DIRECTORY, ".color.json")
JSON_SOURCE_CROP = os.path.join(SOURCE_DIRECTORY, ".crop.json")
JSON_CREATE_BODY = os.path.join(SOURCE_DIRECTORY, ".body.json")
JSON_CREATE_HEAD = os.path.join(SOURCE_DIRECTORY, ".head.json")
PATH_SOURCE_HEAD = os.path.join(SOURCE_DIRECTORY, "head")
PATH_SOURCE_BODY = os.path.join(SOURCE_DIRECTORY, "body")

JSON_KEY_DEFAULT = "?.default"


def CreateHeadJSON():
    """
    Automatically generates a character head JSON file.

    JSON contents will reflect contents of "inputs/head/".

    :return: None.
    """
    path = os.path.join(HEAD_DIRECTORY, "*.png")

    contents = ""
    for fn in sorted(glob.glob(path)):
        n = os.path.splitext(os.path.basename(fn))[0]
        p = " ".join([(
            "({})".format(x.capitalize())
            if len(x) == 1
            else (
                x
                if len(x) == 2
                else x.capitalize()
            )
        ) for x in n.split("-")
        ])
        contents += TEMPLATE_JSON_HEAD.format(name=n, full=p)

    contents = contents.rstrip(",")
    contents = TEMPLATE_JSON_BASE.format(contents)
    with open(JSON_IMPATH_HEAD, "w") as f:
        f.write(contents)


def CreateBodyJSON():
    """
    Automatically generates a JSON file containing paths to body spritesheets.

    JSON contents will reflect contents of "inputs/body/".

    :return: None.
    """
    path = os.path.join(BODY_DIRECTORY, "*.png")

    contents = ""
    for fn in sorted(glob.glob(path)):
        n = os.path.splitext(os.path.basename(fn))[0]
        p = " ".join([(
            "({})".format(x.capitalize())
            if len(x) == 1
            else (
                x
                if len(x) == 2
                else x.capitalize()
            )
        ) for x in n.split("-")
        ])
        contents += TEMPLATE_JSON_BODY.format(name=n, full=p)

    contents = contents.rstrip(",")
    contents = TEMPLATE_JSON_BASE.format(contents)
    with open(JSON_IMPATH_BODY, "w") as f:
        f.write(contents)


def LoadHeadPaths():
    """
    Loads and returns relative filepaths to character head spritesheets.

    :return: Dictionary containing character head filepaths.
    """
    with open(JSON_IMPATH_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadBodyPaths():
    """
    Loads and returns relative filepaths to character body spritesheets.

    :return: Dictionary containing character body filepaths.
    """
    with open(JSON_IMPATH_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadBodyOffsets():
    """
    Loads and returns per-frame character body offsets.

    :return: Dictionary containing all characters' body offsets.
    """
    with open(JSON_OFFSET_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadHeadOffsets():
    """
    Loads and returns per-frame character head offsets.

    :return: Dictionary containing all characters' head offsets.
    """
    with open(JSON_OFFSET_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadCreateBody():
    """
    Loads and returns cropping regions on raw body spritesheets.

    :return: Dictionary containing cropping rules for body spritesheets.
    """
    with open(JSON_CREATE_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadCreateHead():
    """
    Loads and returns cropping regions on raw head spritesheets.

    :return: Dictionary containing cropping rules for head spritesheets.
    """
    with open(JSON_CREATE_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadSourceColoring():
    """
    Loads and returns standardized color order on master spritesheets.

    :return: Dictionary containing color region order.
    """
    with open(JSON_SOURCE_COLR, "r") as f:
        data = json.load(f)
    return data


def LoadSourceCropping():
    """
    Loads and returns standardized cropping regions on master spritesheets.

    :return: Dictionary containing standard cropping regions.
    """
    with open(JSON_SOURCE_CROP, "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    CreateHeadJSON()
    CreateBodyJSON()
