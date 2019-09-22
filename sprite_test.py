#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Image splitting tests.

All spritesheets used were taken from The Spriters Resource.

"""
import sprite_splitter
import sprite_utils
import importlib
from sprite_constant import *


PROMPT = """
Commands:
[c]omposite <unit> <class> -> Composite full sprite
[i]dle <unit> <class>      -> Composite idle frames
[r]efresh                  -> Refresh sprite loader
[q]uit                     -> Quit application

What do?
>>> """


def DoComposite(command, idle=False):
    """
    Composites and saves a spritesheet.

    :param command: Sprite compositing functin to use.
    :param idle:    Whether to composite only idle frames. (Default False).

    :return: None.
    """
    if len(command) == 3:
        sprite_utils.FixPath(ROOT_OUTPUT_DIR)
        head = command[1]
        body = command[2]
        path = os.path.join(ROOT_OUTPUT_DIR, "{}_{}.png".format(head, body))

        if idle:
            image = sprite_splitter.CompositeIdle(head, body)
            sprite_splitter.SaveImage(image, path)
            print("Composited {} (idle only)!".format(path))
        else:
            image = sprite_splitter.CompositeFull(head, body)
            sprite_splitter.SaveImage(image, path)
            print("Composited {}!".format(path))


def DoRefresh():
    """
    Refreshes imported Python library `sprite_splitter`.

    This currently is kinda useless, as data is now configured in JSON
    instead of raw Python.

    :return: None.
    """
    importlib.reload(sprite_splitter)
    print("Refreshed sprite loader!")


def TestMain():
    """
    Main testing function.

    :return: None.
    """
    isRunning = True

    while isRunning:
        command = input(PROMPT).lower().split()
        if command:
            if command[0] in ("c", "composite"):
                DoComposite(command)
            elif command[0] in ("i", "idle"):
                DoComposite(command, idle=True)
            elif command[0] in ("r", "refresh"):
                DoRefresh()
            elif command[0] in ("q", "quit"):
                isRunning = False


if __name__ == "__main__":
    TestMain()
