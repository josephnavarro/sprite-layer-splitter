#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Utilities for reading and writing local JSON files.

"""
import json
import glob
from sprite_utils import *


JSON_TEMPLATES = {
    "base": "{{{}}}",
    "head": "\"{name}\":{{"
            "\"path\":[\"images\",\"{profile}\",\"head\",\"{name}.png\"],"
            "\"name\":\"{full}\""
            "}},",
    "body": "\"{name}\":{{"
            "\"path\":[\"images\",\"{profile}\",\"body\",\"{name}.png\"],"
            "\"name\":\"{full}\""
            "}},",
}

PATHS = {
    "images": os.path.join(DIRECTORIES["input"]["root"], "images"),
    "impath": os.path.join(DIRECTORIES["input"]["root"], "paths"),
    "offset": os.path.join(DIRECTORIES["input"]["root"], "offsets"),
    "source": {
        "root": os.path.join(DIRECTORIES["input"]["root"], "sources"),
        "head": os.path.join(DIRECTORIES["input"]["root"], "sources", "head"),
        "body": os.path.join(DIRECTORIES["input"]["root"], "sources", "body"),
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

JSON_KEY_RESERVE = "?.{}"
JSON_KEY_DEFAULT = JSON_KEY_RESERVE.format("default")


def create_input_json(key, profile):
    """
    Automatically generates a character head or body JSON file.

    JSON contents will reflect contents of "inputs/{profile}/{head|body}/".

    :param key:
    :param profile:

    :return: None.
    """
    path = os.path.join(PATHS["images"], profile, key, "*.png")
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
        contents += JSON_TEMPLATES[key].format(profile=profile, name=n, full=p)

    contents = contents.rstrip(",")
    contents = JSON_TEMPLATES["base"].format(contents)

    # print(contents)

    with open(JSONS["paths"][key], "w") as f:
        f.write(contents)


def load_offsets(key, profile):
    """
    Loads and returns per-frame (x,y) offsets.

    :param key: Either of "head" or "body".

    :return: Dictionary containing all (x,y) offsets.
    """
    with open(JSONS["offset"][key], "r") as f:
        data = json.load(f).get(JSON_KEY_RESERVE.format(profile), {})
    return data


def load_paths(key):
    """
    Loads and returns relative filepaths to spritesheets.

    :param key: Either of "head" or "body".

    :return: Dictionary containing spritesheet filepaths.
    """
    with open(JSONS["paths"][key], "r") as f:
        data = json.load(f)
    return data


def load_create(key):
    """
    Loads and returns cropping regions on raw spritesheets.

    :param key: Either of "head" or "body".

    :return: Dictionary containing cropping rules for body spritesheets.
    """
    with open(JSONS["sources"][key], "r") as f:
        data = json.load(f)
    return data


def load_source_coloring():
    """
    Loads and returns standardized color order on master spritesheets.

    :return: Dictionary containing color region order.
    """
    with open(JSONS["sources"]["color"], "r") as f:
        data = json.load(f)
    return data


def load_source_cropping():
    """
    Loads and returns standardized cropping regions on master spritesheets.

    :return: Dictionary containing standard cropping regions.
    """
    with open(JSONS["sources"]["crop"], "r") as f:
        data = json.load(f)
    return data
