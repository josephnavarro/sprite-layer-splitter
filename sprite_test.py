#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Image splitting tests. All spritesheets used in these
examples were taken from The Spriters Resource.
(https://www.spriters-resource.com/3ds/fireemblemfates/)

"""
import sprite_splitter
import importlib

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
        if idle:
            sprite_splitter.MainIdle(cmd[1], cmd[2], '{}_{}'.format(cmd[1], cmd[2]))
            print("Composited idle sprites for {}_{}!".format(cmd[1], cmd[2]))
        else:
            sprite_splitter.Main(cmd[1], cmd[2], '{}_{}'.format(cmd[1], cmd[2]))
            print("Composited sprites for {}_{}!".format(cmd[1], cmd[2]))


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
