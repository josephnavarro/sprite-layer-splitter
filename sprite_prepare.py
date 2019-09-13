#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Creates intermediate spritesheets used during the final compositing process.

"""
from PIL import Image
from sprite_json import *
from sprite_utils import *

""" Default PIL image mode. """
MODE = "RGBA"

""" Root "output" directories. """
HEAD_DIRECTORY: str = os.path.join("inputs", "head")
BODY_DIRECTORY: str = os.path.join("inputs", "body")

""" Source spritesheet directories. """
SOURCE_HEAD_DIRECTORY: str = os.path.join("inputs", "raw_head")
SOURCE_BODY_DIRECTORY: str = os.path.join("inputs", "raw_body")

""" Body regions. """
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

""" Head regions. """
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


def MakeImage(w: int, h: int) -> Image:
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

    for fn in glob.glob(os.path.join(SOURCE_BODY_DIRECTORY, "*.png")):
        print("Generating intermediate for {}...".format(fn))
        FixPath(BODY_DIRECTORY)
        ProcessBody(fn).save(os.path.join(BODY_DIRECTORY, os.path.split(fn)[-1]))

    print("Intermediate body spritesheets complete!")


def PrepareHead() -> None:
    """
    Create head source images.

    :return: None.
    """
    print("Now generating intermediate head spritesheets...")

    for fn in glob.glob(os.path.join(SOURCE_HEAD_DIRECTORY, "*.png")):
        print("Generating intermediate for {}...".format(fn))
        FixPath(HEAD_DIRECTORY)
        ProcessHead(fn).save(os.path.join(HEAD_DIRECTORY, os.path.split(fn)[-1]))

    print("Intermediate head spritesheets complete!")


def ProcessBody(filename: str) -> Image:
    """
    Processes an input "body" image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single spritesheet.

    :param filename: Source image to crop from.

    :return: Newly-generated spritesheet.
    """

    img = Image.open(filename)
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

    out_img = MakeImage(256, len(rects) * 32)
    for n, r in enumerate(rects):
        out_img.paste(r, (0, n * 32))

    return out_img


def ProcessHead(filename: str) -> Image:
    """
    Processes an input "head" image.

    Specifically, takes a Fire Emblem spritesheet formatted in a certain way,
    then extracts the idle, left-, and right-moving frames to composite into
    a single spritesheet.

    :param filename: Source image to crop from.

    :return: Newly-generated spritesheet.
    """

    img = Image.open(filename)
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

    out_img = MakeImage(256, len(rects) * 64)
    for n, r in enumerate(rects):
        out_img.paste(r, (0, n * 64))

    return out_img


if __name__ == "__main__":
    PrepareBody()
    PrepareHead()