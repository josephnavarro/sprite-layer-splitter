#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Filepath utility functions.

"""
import shutil
import sys
from sprite_constant import *


def IsWindows():
    """
    Checks whether current platform is Windows.

    :return: True if running Windows; false otherwise.
    """
    return sys.platform == "win32"


def IsOSX():
    """
    Checks whether current platform is OS X.

    :return: True if running Mac OS X; false otherwise.
    """
    return sys.platform == "darwin"


def FlushInputs(key):
    """
    Flushes an input directory.

    :param key: Either of "head" or "body".

    :return: True on success; false otherwise.
    """
    path = DIRECTORIES["input"][key]
    try:
        shutil.rmtree(path)
        print("Removed directory '{}'!".format(path))
        return True
    except FileNotFoundError:
        print("Directory '{}' already removed!".format(path))
        return False


def FlushOutputs():
    """
    Flushes entire image output directory.

    :return: True on success; false otherwise.
    """
    try:
        shutil.rmtree(ROOT_OUTPUT_DIR)
        print("Removed directory '{}'!".format(ROOT_OUTPUT_DIR))
        return True
    except FileNotFoundError:
        print("Directory '{}' already removed!".format(ROOT_OUTPUT_DIR))
        return False


def FixPath(path):
    """
    Ensures existence of an output directory before returning it.

    :param path: Relative path to directory.

    :return: Fixed path.
    """
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path


if __name__ == "__main__":
    FlushOutputs()
