#! usr/bin/env python3
"""
Image processing functions.
"""
import cv2
import numpy as np


def apply_mask(img, mask):
    """
    Applies an alpha mask to the given (colored) image.
    """
    return cv2.bitwise_and(img, mask)


def convert_alpha(img):
    """
    Adds alpha channel to a CV2 image.
    """
    b, g, r = cv2.split(img)
    return cv2.merge((b, g, r, np.ones(b.shape, dtype=b.dtype) * 255))


def crop(image, start, size):
    """
    Returns a subregion on a CV2-formatted image.
    Does not modify original image.

    :param image:  Image to crop from
    :param start:  X-Y coordinate to start cropping from
    :param size:   Width and height (2-tuple) of cropping region

    :return:  Newly-cropped subregion from image.
    """
    y, x = start
    h, w = size
    return image[x:x + w, y:y + h]


def get_colors(image):
    """
    Gets all unique colors from a CV2 image.
    """
    return np.unique(image)


def grayscale(image, colored=False):
    """
    Converts RGB image to grayscale.
    """
    out = cv2.cvtColor(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    if colored:
        # Optionally output as RGB again
        out = cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def is_grayscale(color):
    """
    Detects if a color is monochrome.
    """
    r, g, b = color
    return r == g == b


def make_blank(w, h, channels=4):
    """
    Makes a blank CV2-ready image of the given size.
    """
    return np.zeros((h, w, channels), np.uint8)


def make_mask(image, thresh, maxval=255):
    '''
    Create a bitmask from a grayscale CV2 image.
    '''
    r, t = cv2.threshold(image, thresh - 1, maxval, cv2.THRESH_TOZERO)
    r, t = cv2.threshold(t, thresh + 1, maxval, cv2.THRESH_TOZERO_INV)
    r, t = cv2.threshold(t, thresh - 1, maxval, cv2.THRESH_BINARY)
    r, t = cv2.threshold(t, thresh + 1, maxval, cv2.THRESH_BINARY)
    return t


def paste(src, dest, pos):
    """
    Pastes source image onto destination image (in-place).
    Preserves alpha transparency (i.e. transparent pixels in `src` won't overwrite upon paste).

    :param src:   Source image to be pasted
    :param dest:  Destination image to paste onto
    :param pos:   X-Y coordinate on destination to paste at
    """
    h, w = src.shape[0], src.shape[1]
    x, y = pos

    for yy in range(h):
        for xx in range(w):
            if src[yy, xx, 3]:
                # Copy pixel if not transparent
                dest[y + yy, x + xx] = src[yy, xx]


# noinspection PyUnresolvedReferences
def replace_color(img, color=None, replace=[0, 0, 0]):
    """
    Replaces a color in an image with another one (in-place).
    Defaults to top-left pixel's color.
    """
    if not color:
        color = img[0, 0]
    img[np.where((img == color).all(axis=2))] = replace
