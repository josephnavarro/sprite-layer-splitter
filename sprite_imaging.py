#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

General image processing functions.

"""

import cv2
import numpy as np


def ApplyMask(image: np.ndarray,
              mask: np.ndarray) -> np.ndarray:
    """
    Applies an alpha mask to a colored image.

    :param image: Image to modify.
    :param mask:  Mask to apply.

    :return: Image with alpha mask applied.
    """
    return cv2.bitwise_and(image, mask)


def ConvertAlpha(image: np.ndarray) -> np.ndarray:
    """
    Adds an alpha channel to a CV2 image.

    :param image: Image to modify.

    :return: Image with alpha channel added.
    """
    b, g, r = cv2.split(image)
    return cv2.merge((b, g, r, np.ones(b.shape, dtype=b.dtype) * 255))


def Crop(image: np.ndarray,
         start: list,
         size: list) -> np.ndarray:
    """
    Returns a subregion from a CV2 image.
    (Does not modify the original image).

    :param image: Image to crop from.
    :param start: X-Y coordinate to start cropping from.
    :param size:  Width and height (2-tuple) of cropping region.

    :return: Newly-cropped subregion from image.
    """
    y, x = start
    h, w = size
    return image[x: x + w, y: y + h]


def GetUniqueColors(image: np.ndarray) -> np.ndarray:
    """
    Returns all unique colors within an image.

    :param image: Image to check colors of.

    :return: Numpy array containing all unique colors within image.
    """
    return np.unique(image)


def ToGrayscale(image: np.ndarray,
                is_color: bool = False) -> np.ndarray:
    """
    Converts an RGB image to grayscale.

    :param image:    CV2 image to convert.
    :param is_color: Whether to preserve color channels. (Default False).

    :return: Image as converted to grayscale.
    """
    out_image = cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)

    # Optionally output as RGB again
    if is_color:
        out_image = cv2.cvtColor(out_image, cv2.COLOR_GRAY2RGB)

    return out_image


def IsGrayscale(color: iter) -> bool:
    """
    Checks whether a color is monochrome.

    :param color: RGB color iterable.

    :return: True if color is grayscale; false otherwise.
    """
    r, g, b = color
    return r == g == b


def MakeBlank(w: int,
              h: int,
              channels: int = 4) -> np.ndarray:
    """
    Makes a blank image of the given size.

    :param w:        Width of output image.
    :param h:        Height of output image.
    :param channels: Number of color channels. (Default 4).

    :return: Blank CV2-ready image.
    """
    return np.zeros((h, w, channels), np.uint8)


def MakeMask(image: np.ndarray,
             thresh: float,
             maxval: int = 255) -> np.ndarray:
    """
    Creates a bitmask from a grayscale CV2 image.

    :param image:  Image to create mask from.
    :param thresh: Transparency threshold.
    :param maxval: Maximum threshold value. (Default 255).

    :return: Newly-generated bitmask.
    """
    image = cv2.threshold(image, thresh - 1, maxval, cv2.THRESH_TOZERO)[1]
    image = cv2.threshold(image, thresh + 1, maxval, cv2.THRESH_TOZERO_INV)[1]
    image = cv2.threshold(image, thresh - 1, maxval, cv2.THRESH_BINARY)[1]
    image = cv2.threshold(image, thresh + 1, maxval, cv2.THRESH_BINARY)[1]

    return image


def Paste(dest: np.ndarray,
          src: np.ndarray,
          pos: tuple) -> None:
    """
    Pastes one image onto another. (In-place).
    Preserves alpha transparency; transparent pixels won't overwrite anything.

    :param dest: Destination image to modify.
    :param src:  Source image to paste.
    :param pos:  X-Y coordinate to paste at.

    :return: None.
    """
    x, y = pos
    for yy in range(src.shape[0]):
        for xx in range(src.shape[1]):
            try:
                if src[yy, xx, 3]:
                    # Copy if not transparent
                    dest[y + yy, x + xx] = src[yy, xx]
            except IndexError:
                dest[y + yy, x + xx] = src[yy, xx]


# noinspection PyUnresolvedReferences
def ReplaceColor(image: np.ndarray,
                 color: list = [],
                 replace: list = [0, 0, 0]) -> np.ndarray:
    """
    Replaces a color in an image with another one.
    Defaults to top-left pixel's color.

    :param image:   Image to modify.
    :param color:   RGB color to be replaced.
    :param replace: RGB color to replace with.

    :return: Copy of image with the given color replaced.
    """
    out_image = np.copy(image)
    if not color:
        color = out_image[0, 0]
    out_image[np.where((out_image == color).all(axis=2))] = replace
    return out_image
