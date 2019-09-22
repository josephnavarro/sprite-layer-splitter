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


def CropImage(im, x, y, w, h):
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


def MakeImage(w, h):
    """
    Creates a blank PIL image.

    :param w: Width of image.
    :param h: Height of image.

    :return: Blank RGBA image with the given dimensions.
    """
    return Image.new(MODE, (w, h), (0, 0, 0, 255))


def PrepareBody():
    """
    Creates intermediate body spritesheets.

    :return: None.
    """
    print("Now generating intermediate body spritesheets...")

    bodyData = LoadCreateBody()
    files = glob.glob(os.path.join(PATH_SOURCE_BODY, "*.png"))
    files.sort()

    for filename in files:
        print("Generating intermediate for {}...".format(filename))

        root = FixPath(BODY_DIRECTORY)
        path = os.path.join(root, os.path.split(filename)[-1])

        image = ProcessBody(filename, bodyData)
        image.save(path)

    print("Intermediate body spritesheets complete!")


def PrepareHead():
    """
    Creates intermediate head spritesheets.

    :return: None.
    """
    print("Now generating intermediate head spritesheets...")

    headData = LoadCreateHead()
    files = glob.glob(os.path.join(PATH_SOURCE_HEAD, "*.png"))
    files.sort()

    for filename in files:
        print("Generating intermediate for {}...".format(filename))

        root = FixPath(HEAD_DIRECTORY)
        path = os.path.join(root, os.path.split(filename)[-1])

        image = ProcessHead(filename, headData)
        image.save(path)

    print("Intermediate head spritesheets complete!")


def ProcessBody(filename, data):
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
        rectData = data[key]
    except KeyError:
        rectData = data[JSON_KEY_DEFAULT]

    rects = [
        CropImage(img, *rectData["0"]["idle"]),
        CropImage(img, *rectData["0"]["left"]),
        CropImage(img, *rectData["0"]["right"]),
        CropImage(img, *rectData["1"]["idle"]),
        CropImage(img, *rectData["1"]["left"]),
        CropImage(img, *rectData["1"]["right"]),
        CropImage(img, *rectData["2"]["idle"]),
        CropImage(img, *rectData["2"]["left"]),
        CropImage(img, *rectData["2"]["right"]),
        CropImage(img, *rectData["3"]["idle"]),
        CropImage(img, *rectData["3"]["left"]),
        CropImage(img, *rectData["3"]["right"]),
    ]

    output = MakeImage(256, len(rects) * 32)
    for n, r in enumerate(rects):
        output.paste(r, (0, n * 32))

    return output


def ProcessHead(filename, data):
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
        rectData = data[key]
    except KeyError:
        rectData = data[JSON_KEY_DEFAULT]

    rects = [
        CropImage(img, *rectData["0"]["idle"]),
        CropImage(img, *rectData["0"]["large-direction"]),
        CropImage(img, *rectData["0"]["small-direction"]),
        CropImage(img, *rectData["1"]["idle"]),
        CropImage(img, *rectData["1"]["large-direction"]),
        CropImage(img, *rectData["1"]["small-direction"]),
        CropImage(img, *rectData["2"]["idle"]),
        CropImage(img, *rectData["2"]["large-direction"]),
        CropImage(img, *rectData["2"]["small-direction"]),
        CropImage(img, *rectData["3"]["idle"]),
        CropImage(img, *rectData["3"]["large-direction"]),
        CropImage(img, *rectData["3"]["small-direction"]),
    ]

    output = MakeImage(256, len(rects) * 64)
    for n, r in enumerate(rects):
        output.paste(r, (0, n * 64))

    return output


if __name__ == "__main__":
    PrepareBody()
    PrepareHead()
