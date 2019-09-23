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


def FlushBodies():
    """
    Flushes entire body input directory.

    :return: None.
    """
    try:
        shutil.rmtree(BODY_DIRECTORY)
        print("Removed directory '{}'!".format(BODY_DIRECTORY))
    except FileNotFoundError:
        print("Directory '{}' already removed!".format(BODY_DIRECTORY))
        return


def FlushHeads():
    """
    Flushes entire head input directory.

    :return:
    """
    try:
        shutil.rmtree(HEAD_DIRECTORY)
        print("Removed directory '{}'!".format(HEAD_DIRECTORY))
    except FileNotFoundError:
        print("Directory '{}' already removed!".format(HEAD_DIRECTORY))
        return


def FlushOutputs():
    """
    Flushes entire image output directory.

    :return: None.
    """
    try:
        shutil.rmtree(ROOT_OUTPUT_DIR)
        print("Removed directory '{}'!".format(ROOT_OUTPUT_DIR))
    except FileNotFoundError:
        print("Directory '{}' already removed!".format(ROOT_OUTPUT_DIR))
        return


def FixPath(path):
    """
    Ensures existence of an output directory.

    :param path: Relative path to directory.

    :return: Fixed path.
    """
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path


if __name__ == "__main__":
    FlushOutputs()
