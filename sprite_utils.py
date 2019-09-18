#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Filepath utility functions.

--------------------------------------------------------------------------------
"""
import shutil
import sys
from sprite_constant import *


def IsWindows() -> bool:
    """
    Checks whether current platform is Windows.

    :return: True if running Windows; false otherwise.
    """
    return sys.platform == "win32"


def IsOSX() -> bool:
    """
    Checks whether current platform is OS X.

    :return: True if running Mac OS X; false otherwise.
    """
    return sys.platform == "darwin"



def FlushOutputs() -> None:
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


def FixPath(path: str) -> str:
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
