#! usr/bin/env python3
"""
Creates intermediate spritesheets used for final compositing.
"""
from PIL import Image
from paths import *

BODY_RECT_1A = (2, 2, 2 + 256, 2 + 32)  # Idle
BODY_RECT_1B = (2, 38, 2 + 256, 38 + 32)  # Move left
BODY_RECT_1C = (2, 70, 2 + 256, 70 + 32)  # Move right

BODY_RECT_2A = (2, 554, 2 + 256, 554 + 32)  # Idle
BODY_RECT_2B = (2, 590, 2 + 256, 590 + 32)  # Move left
BODY_RECT_2C = (2, 622, 2 + 256, 622 + 32)  # Move right

BODY_RECT_3A = (2, 1106, 2 + 256, 1106 + 32)  # Idle
BODY_RECT_3B = (2, 1142, 2 + 256, 1142 + 32)  # Move left
BODY_RECT_3C = (2, 1174, 2 + 256, 1174 + 32)  # Move right

BODY_RECT_4A = (2, 1658, 2 + 256, 1658 + 32)  # Idle
BODY_RECT_4B = (2, 1694, 2 + 256, 1694 + 32)  # Move left
BODY_RECT_4C = (2, 1726, 2 + 256, 1726 + 32)  # Move right

HEAD_RECT_1A = (2, 2, 2 + 256, 2 + 64)  # Idle (large + small)
HEAD_RECT_1B = (2, 70, 2 + 256, 70 + 64)  # Move left + right (large)
HEAD_RECT_1C = (2, 406, 2 + 256, 406 + 48)  # Move left + right (small)

HEAD_RECT_2A = (2, 586, 2 + 256, 586 + 64)  # Idle (large + small)
HEAD_RECT_2B = (2, 654, 2 + 256, 654 + 64)  # Move left + right (large)
HEAD_RECT_2C = (2, 990, 2 + 256, 990 + 48)  # Move left + right (small)

HEAD_RECT_3A = (2, 1170, 2 + 256, 1170 + 64)  # Idle (large + small)
HEAD_RECT_3B = (2, 1238, 2 + 256, 1238 + 64)  # Move left + right (large)
HEAD_RECT_3C = (2, 1574, 2 + 256, 1574 + 48)  # Move left + right (small)

HEAD_RECT_4A = (2, 1754, 2 + 256, 1754 + 64)  # Idle (large + small)
HEAD_RECT_4B = (2, 1822, 2 + 256, 1822 + 64)  # Move left + right (large)
HEAD_RECT_4C = (2, 2158, 2 + 256, 2158 + 48)  # Move left + right (small)

MODE = "RGBA"


def new_image(w: int, h: int) -> Image:
    """
    Creates a new image.

    :param w: Width of image.
    :param h: Height of image.

    :return: RGBA image (uninitialised) with the given dimensions.
    """
    return Image.new(MODE, (w, h), (0, 0, 0, 255))


def process_body(filename: str) -> Image:
    """
    Processes an input body image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single spritesheet.

    :param filename: Source image to crop from.

    :return: Newly-generated spritesheet (Image).
    """
    img = Image.open(filename)  # type: Image
    rects = [
        img.crop(BODY_RECT_1A),
        img.crop(BODY_RECT_1B),
        img.crop(BODY_RECT_1C),
        img.crop(BODY_RECT_2A),
        img.crop(BODY_RECT_2B),
        img.crop(BODY_RECT_2C),
        img.crop(BODY_RECT_3A),
        img.crop(BODY_RECT_3B),
        img.crop(BODY_RECT_3C),
        img.crop(BODY_RECT_4A),
        img.crop(BODY_RECT_4B),
        img.crop(BODY_RECT_4C),
        ]

    num = len(rects)
    new = new_image(256, num * 32)  # type: Image

    for y in range(num):
        new.paste(rects[y], (0, y * 32))

    return new


def process_head(filename: str) -> Image:
    """
    Processes an input head image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single spritesheet.

    :param filename:

    :return:
    """
    img = Image.open(filename)  # type: Image
    rects = [
        img.crop(HEAD_RECT_1A),
        img.crop(HEAD_RECT_1B),
        img.crop(HEAD_RECT_1C),
        img.crop(HEAD_RECT_2A),
        img.crop(HEAD_RECT_2B),
        img.crop(HEAD_RECT_2C),
        img.crop(HEAD_RECT_3A),
        img.crop(HEAD_RECT_3B),
        img.crop(HEAD_RECT_3C),
        img.crop(HEAD_RECT_4A),
        img.crop(HEAD_RECT_4B),
        img.crop(HEAD_RECT_4C),
        ]

    num = len(rects)
    new = new_image(256, num * 64)

    for y in range(num):
        new.paste(rects[y], (0, y * 64))

    return new


if __name__ == "__main__":
    import glob

    for filename in glob.glob("./inputs/0body/*.png"):
        body = process_body(filename)
        outpath = fix_paths("inputs/body/")
        body.save(os.path.join("inputs", "body", os.path.split(filename)[-1]))

    for filename in glob.glob("./inputs/0head/*.png"):
        head = process_head(filename)
        outpath = fix_paths("inputs/head/")
        head.save(os.path.join("inputs", "head", os.path.split(filename)[-1]))
