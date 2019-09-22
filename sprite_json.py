#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Utilities for reading and writing local JSON files.

"""
import json
import glob
from sprite_constant import *

TEMPLATE_JSON_BASE = "{{{}}}"
TEMPLATE_JSON_CHARA = "\"{name}\": {{" \
                      "\"path\": [\"head\", \"{name}.png\"]," \
                      "\"name\": \"{full}\"" \
                      "}},"
TEMPLATE_JSON_CLASS = "\"{name}\": {{" \
                      "\"path\": [\"body\", \"{name}.png\"]," \
                      "\"name\": \"{full}\"" \
                      "}},"

PATH_JSON_CHARA = os.path.join("inputs", "head.json")
PATH_JSON_CLASS = os.path.join("inputs", "body.json")
PATH_JSON_OFFSET_HEAD = os.path.join("inputs", "head_offsets.json")
PATH_JSON_OFFSET_BODY = os.path.join("inputs", "body_offsets.json")
PATH_JSON_SOURCE_COLOR = os.path.join("inputs", ".src_color.json")
PATH_JSON_SOURCE_CROP = os.path.join("inputs", ".src_crop.json")
PATH_JSON_GENSRC_BODY = os.path.join("inputs", ".raw_body.json")
PATH_JSON_GENSRC_HEAD = os.path.join("inputs", ".raw_head.json")


def CreateHeadJSON():
    """
    Automatically generates a character head JSON file.

    JSON contents will reflect contents of "inputs/head/".

    :return: None.
    """
    contents: str = ""
    for fn in glob.glob(os.path.join(ROOT_INPUT_DIR, "head", "*.png")):
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
        contents += TEMPLATE_JSON_CHARA.format(name=n, full=p)

    contents = contents.rstrip(",")
    contents = TEMPLATE_JSON_BASE.format(contents)
    with open(PATH_JSON_CHARA, "w") as f:
        f.write(contents)


def CreateBodyJSON():
    """
    Automatically generates a JSON file containing paths to body spritesheets.

    JSON contents will reflect contents of "inputs/body/".

    :return: None.
    """
    contents: str = ""
    files: list = glob.glob(os.path.join(ROOT_INPUT_DIR, "body", "*.png"))
    files.sort()

    for fn in glob.glob(os.path.join(ROOT_INPUT_DIR, "body", "*.png")):
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
        contents += TEMPLATE_JSON_CLASS.format(name=n, full=p)

    contents = contents.rstrip(",")
    contents = TEMPLATE_JSON_BASE.format(contents)
    with open(PATH_JSON_CLASS, "w") as f:
        f.write(contents)


def LoadHeadPaths():
    """
    Loads and returns relative filepaths to character head spritesheets.

    :return: Dictionary containing character head filepaths.
    """
    with open(PATH_JSON_CHARA, "r") as f:
        data = json.load(f)
    return data


def LoadBodyPaths():
    """
    Loads and returns relative filepaths to character body spritesheets.

    :return: Dictionary containing character body filepaths.
    """
    with open(PATH_JSON_CLASS, "r") as f:
        data = json.load(f)
    return data


def LoadBodyOffsets():
    """
    Loads and returns per-frame character body offsets.

    :return: Dictionary containing all characters' body offsets.
    """
    with open(PATH_JSON_OFFSET_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadHeadOffsets():
    """
    Loads and returns per-frame character head offsets.

    :return: Dictionary containing all characters' head offsets.
    """
    with open(PATH_JSON_OFFSET_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadGenSrcBody():
    """
    Loads and returns cropping regions on raw body spritesheets.

    :return: Dictionary containing cropping rules for body spritesheets.
    """
    with open(PATH_JSON_GENSRC_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadGenSrcHead():
    """
    Loads and returns cropping regions on raw head spritesheets.

    :return: Dictionary containing cropping rules for head spritesheets.
    """
    with open(PATH_JSON_GENSRC_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadSourceImgColors():
    """
    Loads and returns standardized color order on master spritesheets.

    :return: Dictionary containing color region order.
    """
    with open(PATH_JSON_SOURCE_COLOR, "r") as f:
        data = json.load(f)
    return data


def LoadSourceImgCropping():
    """
    Loads and returns standardized cropping regions on master spritesheets.

    :return: Dictionary containing standard cropping regions.
    """
    with open(PATH_JSON_SOURCE_CROP, "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    CreateHeadJSON()
    CreateBodyJSON()
