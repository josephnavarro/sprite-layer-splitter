#! usr/bin/env python3
"""
------------------------------------------------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Utilities for reading and writing local JSON files.

------------------------------------------------------------------------------------------------------------------------
"""
import json
import glob
from sprite_constant import *


TEMPLATE_JSON_BASE = "{{{}}}"
TEMPLATE_JSON_CHARA = "\"{name}\":{{\"path\":[\"head\", \"{name}.png\"],\"name\":\"{full}\"}},"
TEMPLATE_JSON_CLASS = "\"{name}\":{{\"path\":[\"body\", \"{name}.png\"],\"name\":\"{full}\"}},"

PATH_JSON_CHARA = os.path.join("inputs", "head.json")
PATH_JSON_CLASS = os.path.join("inputs", "body.json")
PATH_JSON_OFFSET_HEAD = os.path.join("inputs", "head_offsets.json")
PATH_JSON_OFFSET_BODY = os.path.join("inputs", "body_offsets.json")
PATH_JSON_SOURCE_COLOR = os.path.join("inputs", ".src_color.json")
PATH_JSON_SOURCE_CROP = os.path.join("inputs", ".src_crop.json")
PATH_JSON_GENSRC_BODY = os.path.join("inputs", ".raw_body.json")
PATH_JSON_GENSRC_HEAD = os.path.join("inputs", ".raw_head.json")


def CreateHeadJSON() -> None:
    """
    Automatically generates a character head JSON file.
    JSON contents will reflect the contents of "inputs/head/".

    :return: None.
    """
    newstr = ""
    for _ in glob.glob(os.path.join(ROOT_INPUT_DIRECTORY, "head", "*.png")):
        n = os.path.splitext(os.path.basename(_))[0]
        p = " ".join([
            ("({})".format(x.capitalize()) if len(x) == 1 else (x if len(x) == 2 else x.capitalize()))
            for x in n.split("-")
            ])
        newstr += TEMPLATE_JSON_CHARA.format(name=n, full=p)

    newstr = newstr.rstrip(",")
    newstr = TEMPLATE_JSON_BASE.format(newstr)
    with open(PATH_JSON_CHARA, "w") as f:
        f.write(newstr)


def CreateBodyJSON() -> None:
    """
    Automatically generates a character body JSON file.
    JSON contents will reflect the contents of "inputs/body/".

    :return: None
    """
    newstr = ""
    for _ in glob.glob(os.path.join(ROOT_INPUT_DIRECTORY, "body", "*.png")):
        n = os.path.splitext(os.path.basename(_))[0]
        p = " ".join(
            [("({})".format(x.capitalize()) if len(x) == 1 else (x if len(x) == 2 else x.capitalize())) for x in
             n.split("-")])
        newstr += TEMPLATE_JSON_CLASS.format(name=n, full=p)

    newstr = newstr.rstrip(",")
    newstr = TEMPLATE_JSON_BASE.format(newstr)
    with open(PATH_JSON_CLASS, "w") as f:
        f.write(newstr)


def LoadHeadPaths() -> dict:
    """
    Loads and returns relative filepaths to character head spritesheets.

    :return: Dictionary containing character head filepaths.
    """
    with open(PATH_JSON_CHARA, "r") as f:
        data = json.load(f)
    return data


def LoadBodyPaths() -> dict:
    """
    Loads and returns relative filepaths to character body spritesheets.

    :return: Dictionary containing character body filepaths.
    """
    with open(PATH_JSON_CLASS, "r") as f:
        data = json.load(f)
    return data


def LoadBodyOffsets() -> dict:
    """
    Loads and returns per-frame character body offsets.

    :return: Dictionary containing all characters' body offsets.
    """
    with open(PATH_JSON_OFFSET_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadHeadOffsets() -> dict:
    """
    Loads and returns per-frame character head offsets.

    :return: Dictionary containing all characters' head offsets.
    """
    with open(PATH_JSON_OFFSET_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadGenSrcBody() -> dict:
    """
    Loads and returns cropping regions on raw body spritesheets.

    :return:
    """
    with open(PATH_JSON_GENSRC_BODY, "r") as f:
        data = json.load(f)
    return data


def LoadGenSrcHead() -> dict:
    """
    Loads and returns cropping regions on raw head spritesheets.
    :return:
    """
    with open(PATH_JSON_GENSRC_HEAD, "r") as f:
        data = json.load(f)
    return data


def LoadSourceImgColors() -> dict:
    """
    Loads and returns standardized color order on master spritesheets.

    :return: Dictionary containing color region order.
    """
    with open(PATH_JSON_SOURCE_COLOR, "r") as f:
        data = json.load(f)
    return data


def LoadSourceImgCropping() -> dict:
    """
    Loads and returns standardized cropping regions on master spritesheets.

    :return: Dictionary containing cropping regions.
    """
    with open(PATH_JSON_SOURCE_CROP, "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    CreateHeadJSON()
    CreateBodyJSON()
