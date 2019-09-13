#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Path utility functions.

"""
import shutil
from sprite_constant import *


def FlushOutputs():
    shutil.rmtree(ROOT_OUTPUT_DIRECTORY)


def FixPath(path: str):
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
