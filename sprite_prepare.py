#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Creates intermediate spritesheets used during the final compositing process.

--------------------------------------------------------------------------------
"""
from PIL import Image
from sprite_json import *
from sprite_utils import *


""" 
Default PIL image mode.
"""
MODE = "RGBA"

"""
Root "output" directories.
"""
HEAD_DIRECTORY: str = os.path.join("inputs", "head")
BODY_DIRECTORY: str = os.path.join("inputs", "body")

"""
Source spritesheet directories.
"""
SOURCE_HEAD_DIRECTORY: str = os.path.join("inputs", "raw_head")
SOURCE_BODY_DIRECTORY: str = os.path.join("inputs", "raw_body")

"""
Default key.
"""
JSON_KEY_DEFAULT: str = "?::default"


def CropImage(im: Image,
              x: int,
              y: int,
              w: int,
              h: int) -> Image:
    """
    Crops a PIL image.

    :param im: Image to crop.
    :param x: Topleft x-coordinate to crop from.
    :param y: Topleft y-coordinate to crop from.
    :param w: Width to crop to.
    :param h: Height to crop to.

    :return: Image cropped to the given bounds.
    """
    return im.crop((x, y, w + x, h + y))


def MakeImage(w: int,
              h: int) -> Image:
    """
    Creates a blank PIL image.

    :param w: Width of image.
    :param h: Height of image.

    :return: Blank RGBA image with the given dimensions.
    """
    return Image.new(MODE, (w, h), (0, 0, 0, 255))


def PrepareBody() -> None:
    """
    Create body source images.

    :return: None.
    """
    print("Now generating intermediate body spritesheets...")

    bodyData: dict = LoadGenSrcBody()

    for fn in glob.glob(os.path.join(SOURCE_BODY_DIRECTORY, "*.png")):
        print("Generating intermediate for {}...".format(fn))

        root: str = FixPath(BODY_DIRECTORY)
        path: str = os.path.join(root, os.path.split(fn)[-1])

        image: Image = ProcessBody(fn, bodyData)
        image.save(path)

    print("Intermediate body spritesheets complete!")


def PrepareHead() -> None:
    """
    Create head source images.

    :return: None.
    """
    print("Now generating intermediate head spritesheets...")

    headData: dict = LoadGenSrcHead()

    for fn in glob.glob(os.path.join(SOURCE_HEAD_DIRECTORY, "*.png")):
        print("Generating intermediate for {}...".format(fn))

        root: str = FixPath(HEAD_DIRECTORY)
        path: str = os.path.join(root, os.path.split(fn)[-1])

        image: Image = ProcessHead(fn, headData)
        image.save(path)

    print("Intermediate head spritesheets complete!")


def ProcessBody(filename: str,
                data: dict) -> Image:
    """
    Processes an input "body" image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single spritesheet.

    :param filename: Source image to crop from.
    :param data: Body data to use.

    :return: Newly-generated spritesheet.
    """
    img: Image = Image.open(filename)

    try:
        key: str = os.path.splitext(os.path.basename(filename))[0]
        rectData: dict = data[key]
    except KeyError:
        rectData: dict = data[JSON_KEY_DEFAULT]

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

    output: Image = MakeImage(256, len(rects) * 32)
    for n, r in enumerate(rects):
        output.paste(r, (0, n * 32))

    return output


def ProcessHead(filename: str, data: dict) -> Image:
    """
    Processes an input "head" image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single spritesheet.

    :param filename: Source image to crop from.
    :param data: Head data to use.

    :return: Newly-generated spritesheet.
    """
    img = Image.open(filename)

    try:
        key: str = os.path.splitext(os.path.basename(filename))[0]
        rectData: dict = data[key]
    except KeyError:
        rectData: dict = data[JSON_KEY_DEFAULT]

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

    output: Image = MakeImage(256, len(rects) * 64)
    for n, r in enumerate(rects):
        output.paste(r, (0, n * 64))

    return output


if __name__ == "__main__":
    PrepareBody()
    PrepareHead()
