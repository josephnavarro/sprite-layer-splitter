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

PATHS = {
    "impath": os.path.join(ROOT_INPUT_DIR, "paths"),
    "offset": os.path.join(ROOT_INPUT_DIR, "offsets"),
    "source": {
        "root": os.path.join(ROOT_INPUT_DIR, "sources"),
        "head": os.path.join(ROOT_INPUT_DIR, "sources", "head"),
        "body": os.path.join(ROOT_INPUT_DIR, "sources", "body"),
    },
}

JSONS = {
    "offset":  {
        "head": os.path.join(PATHS["offset"], "head_offsets.json"),
        "body": os.path.join(PATHS["offset"], "body_offsets.json"),
    },
    "paths":   {
        "head": os.path.join(PATHS["impath"], "head.json"),
        "body": os.path.join(PATHS["impath"], "body.json"),
    },
    "sources": {
        "color": os.path.join(PATHS["source"]["root"], ".color.json"),
        "crop":  os.path.join(PATHS["source"]["root"], ".crop.json"),
        "body":  os.path.join(PATHS["source"]["root"], ".body.json"),
        "head":  os.path.join(PATHS["source"]["root"], ".head.json"),
    },
}

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
    with open(JSONS["paths"]["head"], "w") as f:
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
    with open(JSONS["paths"]["body"], "w") as f:
        f.write(contents)

def LoadPaths(key):
    """
    Loads and returns relative filepaths to spritesheets.

    :param key: Either of "head" or "body".

    :return: Dictionary containing spritesheet filepaths.
    """
    with open(JSONS["paths"][key], "r") as f:
        data = json.load(f)
    return data


def _LoadHeadPaths():
    """
    Loads and returns relative filepaths to character head spritesheets.

    :return: Dictionary containing character head filepaths.
    """
    with open(JSONS["paths"]["head"], "r") as f:
        data = json.load(f)
    return data


def _LoadBodyPaths():
    """
    Loads and returns relative filepaths to character body spritesheets.

    :return: Dictionary containing character body filepaths.
    """
    with open(JSONS["paths"]["body"], "r") as f:
        data = json.load(f)
    return data


def LoadBodyOffsets():
    """
    Loads and returns per-frame character body offsets.

    :return: Dictionary containing all characters' body offsets.
    """
    with open(JSONS["offset"]["body"], "r") as f:
        data = json.load(f)
    return data


def LoadHeadOffsets():
    """
    Loads and returns per-frame character head offsets.

    :return: Dictionary containing all characters' head offsets.
    """
    with open(JSONS["offset"]["head"], "r") as f:
        data = json.load(f)
    return data


def LoadCreateBody():
    """
    Loads and returns cropping regions on raw body spritesheets.

    :return: Dictionary containing cropping rules for body spritesheets.
    """
    with open(JSONS["sources"]["body"], "r") as f:
        data = json.load(f)
    return data


def LoadCreateHead():
    """
    Loads and returns cropping regions on raw head spritesheets.

    :return: Dictionary containing cropping rules for head spritesheets.
    """
    with open(JSONS["sources"]["head"], "r") as f:
        data = json.load(f)
    return data


def LoadSourceColoring():
    """
    Loads and returns standardized color order on master spritesheets.

    :return: Dictionary containing color region order.
    """
    with open(JSONS["sources"]["color"], "r") as f:
        data = json.load(f)
    return data


def LoadSourceCropping():
    """
    Loads and returns standardized cropping regions on master spritesheets.

    :return: Dictionary containing standard cropping regions.
    """
    with open(JSONS["sources"]["crop"], "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    CreateHeadJSON()
    CreateBodyJSON()
