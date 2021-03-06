#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

General image processing functions.

"""
import cv2
import numpy as np
from PIL import Image, ImageTk


def ApplyMask(image, mask):
    """
    Applies an alpha mask to a colored image.

    :param image: Image to modify.
    :param mask:  Mask to apply.

    :return: Image with alpha mask applied.
    """
    return cv2.bitwise_and(image, mask)


def ConvertAlpha(image):
    """
    Adds an alpha channel to a CV2 image.

    Assumes BGR color for the input image.

    :param image: Image to modify.

    :return: Image with alpha channel added.
    """
    b, g, r = cv2.split(image)
    return cv2.merge((b, g, r, np.ones(b.shape, dtype=b.dtype) * 255))


def Crop(image, start, size):
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
    return image[x: (x + w), y: (y + h)]


def GetUniqueColors(image: np.ndarray) -> np.ndarray:
    """
    Returns all unique colors within an image.

    :param image: Image to check colors of.

    :return: Numpy array containing all unique colors within image.
    """
    return np.unique(image)


def ToGrayscale(image, is_color=False):
    """
    Converts an RGB image to grayscale.

    :param image:    CV2 image to convert.
    :param is_color: Whether to preserve color channels. (Default False).

    :return: Image as converted to grayscale.
    """
    try:
        outImage = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        outImage = cv2.cvtColor(outImage, cv2.COLOR_BGR2GRAY)

        # Optionally output as RGB again
        if is_color:
            outImage = cv2.cvtColor(outImage, cv2.COLOR_GRAY2RGB)

        return outImage
    except cv2.error:
        return image


def ToPIL(image):
    """
    Converts a numpy array to a PIL image.

    :param image: Numpy image array.

    :return: PIL Image object.
    """
    return Image.fromarray(image)


def ToTkinter(image):
    """
    Converts a PIL image to a Tkinter-compatible object.

    :param image: PIL image.

    :return: PhotoImage compatible with Tkinter.
    """
    return ImageTk.PhotoImage(image)


def OpenTkinter(path, w, h):
    """
    Docstring goes here.

    :param path: Path to image file.
    :param w:    Width of image.
    :param h:    Height of image.

    :return: Tkinter PhotoImage instance.
    """
    image = Image.open(path)
    return ImageTk.PhotoImage(image.resize((w, h), Image.ANTIALIAS))


def ToPILToTkinter(image):
    """
    Converts a numpy array to a PIL image to a Tkinter-compatible object.

    :param image: Numpy image array.

    :return: PhotoImage compatible with Tkinter.
    """
    return ToTkinter(ToPIL(image))


def IsGrayscale(color):
    """
    Checks whether a color is monochrome.

    :param color: RGB color iterable.

    :return: True if color is grayscale; false otherwise.
    """
    r, g, b = color
    return r == g == b


def MakeBlank(w, h, channels=4, *, color=(0, 0, 0, 0)):
    """
    Makes a blank image of the given size.

    :param w:        Width of output image.
    :param h:        Height of output image.
    :param channels: Number of color channels. (Default 4).
    :param color:    RGBA color. (Default black).

    :return: Blank CV2-ready image.
    """
    image = np.zeros((h, w, channels), np.uint8)
    if len(color) == 4:
        fill = color[2], color[1], color[0], color[3]
    elif len(color) == 3:
        fill = color[2], color[1], color[0], 0
    else:
        fill = 0, 0, 0, 0
    image[:, :] = fill
    return image


def MakeMask(image, thresh, maxval=255):
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


def Paste(dest, src, pos):
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
                # If alpha channel, copy if non-transparent
                if src[yy, xx, 3]:
                    dest[y + yy, x + xx] = src[yy, xx]
            except IndexError:
                # Has no alpha channel
                try:
                    dest[y + yy, x + xx] = src[yy, xx]
                except IndexError:
                    # Out of bounds
                    pass


# noinspection PyUnresolvedReferences
def ReplaceColor(image, color=[], replace=[0, 0, 0]):
    """
    Replaces a color in an image with another one.

    Defaults to top-left pixel's color.

    :param image:   Image to modify.
    :param color:   RGB color to be replaced.
    :param replace: RGB color to replace with.

    :return: Copy of image with the given color replaced.
    """
    outImage = np.copy(image)

    if not color:
        color = outImage[0, 0]

    try:
        outImage[np.where((outImage == color).all(axis=2))] = replace
    except AttributeError:
        outImage[:, :] = replace

    return outImage
