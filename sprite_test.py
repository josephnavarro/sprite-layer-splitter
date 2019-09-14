#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Image splitting tests. All spritesheets used in these
examples were taken from The Spriters Resource.
(https://www.spriters-resource.com/3ds/fireemblemfates/)

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


def DoComposite(cmd: iter, idle: bool = False):
    if len(cmd) == 3:
        sprite_utils.FixPath(ROOT_OUTPUT_DIRECTORY)
        head = cmd[1]
        body = cmd[2]
        output = os.path.join(ROOT_OUTPUT_DIRECTORY, '{}_{}'.format(head, body))

        if idle:
            sprite_splitter.MainIdle(head, body, output)
            print("Composited {} (idle only)!".format(output))
        else:
            sprite_splitter.Main(head, body, output)
            print("Composited {}!".format(output))


def DoRefresh():
    importlib.reload(sprite_splitter)
    print("Refreshed sprite loader!")


def main():
    is_running = True
    while is_running:
        cmd = input(PROMPT).lower().split()
        if cmd:
            if cmd[0] in ("c", "composite"):
                DoComposite(cmd)
            elif cmd[0] in ("i", "idle"):
                DoComposite(cmd, idle=True)
            elif cmd[0] in ("r", "refresh"):
                DoRefresh()
            elif cmd[0] in ("q", "quit"):
                is_running = False


if __name__ == "__main__":
    main()
