#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Creates intermediate spritesheets used during the final compositing process.

"""
from PIL import Image
from sprite_json import *
from sprite_utils import *

""" 
Default PIL image mode.
"""
MODE = "RGBA"


def crop_image(im, x, y, w, h):
    """
    Crops a PIL image.

    :param im: Image to crop.
    :param x:  Topleft x-coordinate to crop from.
    :param y:  Topleft y-coordinate to crop from.
    :param w:  Width to crop to.
    :param h:  Height to crop to.

    :return: Specified subregion from image.
    """
    return im.crop((x, y, w + x, h + y))


def make_image(w, h):
    """
    Creates a blank PIL image.

    :param w: Width of image.
    :param h: Height of image.

    :return: Blank RGBA image with the given dimensions.
    """
    return Image.new(MODE, (w, h), (0, 0, 0, 255))


def prepare(key, profile):
    """
    Creates intermediate spritesheets.

    :param key: Either of "head" or "body".

    :return: None.
    """
    print("Now generating intermediate {} spritesheets...".format(key))

    data = load_create(key)
    dir = os.path.join(PATHS["source"]["root"], profile, key, "*.png")
    files = glob.glob(dir)
    files.sort()

    for filename in files:
        print("Generating intermediate for {}...".format(filename))

        root = fix_path(os.path.join(PATHS["images"], profile, key))
        path = os.path.join(root, os.path.split(filename)[-1])

        if key == "head":
            image = process_head(filename, profile, data)
            image.save(path)
        elif key == "body":
            image = process_body(filename, profile, data)
            image.save(path)

    print("Intermediate {} spritesheets complete!".format(key))


def process_body(filename, profile, data):
    """
    Processes an input "body" image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single intermediate spritesheet.

    :param filename: Source image to crop from.
    :param data:     Body data to use.

    :return: Newly-generated spritesheet.
    """
    img = Image.open(filename)

    try:
        key = os.path.splitext(os.path.basename(filename))[0]
        rectData = data[JSON_KEY_RESERVE.format(profile)][key]
    except KeyError:
        rectData = data[JSON_KEY_RESERVE.format(profile)][JSON_KEY_DEFAULT]

    rects = [
        crop_image(img, *rectData["0"]["idle"]),
        crop_image(img, *rectData["0"]["left"]),
        crop_image(img, *rectData["0"]["right"]),
        crop_image(img, *rectData["1"]["idle"]),
        crop_image(img, *rectData["1"]["left"]),
        crop_image(img, *rectData["1"]["right"]),
        crop_image(img, *rectData["2"]["idle"]),
        crop_image(img, *rectData["2"]["left"]),
        crop_image(img, *rectData["2"]["right"]),
        crop_image(img, *rectData["3"]["idle"]),
        crop_image(img, *rectData["3"]["left"]),
        crop_image(img, *rectData["3"]["right"]),
    ]

    output = make_image(256, len(rects) * 32)
    for n, r in enumerate(rects):
        output.paste(r, (0, n * 32))

    return output


def process_head(filename, profile, data):
    """
    Processes an input "head" image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single intermediate spritesheet.

    :param filename: Source image to crop from.
    :param data:     Head data to use.

    :return: Newly-generated spritesheet.
    """
    img = Image.open(filename)

    try:
        key = os.path.splitext(os.path.basename(filename))[0]
        rectData = data[JSON_KEY_RESERVE.format(profile)][key]
    except KeyError:
        rectData = data[JSON_KEY_RESERVE.format(profile)][JSON_KEY_DEFAULT]

    rects = [
        crop_image(img, *rectData["0"]["idle"]),
        crop_image(img, *rectData["0"]["large-direction"]),
        crop_image(img, *rectData["0"]["small-direction"]),
        crop_image(img, *rectData["1"]["idle"]),
        crop_image(img, *rectData["1"]["large-direction"]),
        crop_image(img, *rectData["1"]["small-direction"]),
        crop_image(img, *rectData["2"]["idle"]),
        crop_image(img, *rectData["2"]["large-direction"]),
        crop_image(img, *rectData["2"]["small-direction"]),
        crop_image(img, *rectData["3"]["idle"]),
        crop_image(img, *rectData["3"]["large-direction"]),
        crop_image(img, *rectData["3"]["small-direction"]),
    ]

    output = make_image(256, len(rects) * 64)
    for n, r in enumerate(rects):
        output.paste(r, (0, n * 64))

    return output


if __name__ == "__main__":
    prepare("body", "echoes")
    prepare("head", "echoes")
