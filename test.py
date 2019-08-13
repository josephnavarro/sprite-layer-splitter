#! usr/bin/env python3
"""
Image splitting tests. All spritesheets used in these
examples were taken from The Spriters Resource.
(https://www.spriters-resource.com/3ds/fireemblemfates/)

"""
import splitter, importlib, os

FILE_STRING = "{}.png"
PROMPT = """
Commands:
[c]omposite <unit> <class> -> Composite new sprite
[r]efresh -> Refresh sprite loader
[q]uit -> Quit application

What do?
>>> """

running = True

while running:
    cmd = input(PROMPT).lower().split()

    if not cmd:
        continue

    elif cmd[0] in ('c', 'composite'):
        if len(cmd) != 3:
            continue
        else:
            head = FILE_STRING.format(cmd[1])
            body = FILE_STRING.format(cmd[2])

            if not os.path.exists(os.path.join(splitter.HEAD_DIR, head)):
                print("Error: file {} does not exist!".format(head))
                continue
            elif not os.path.exists(os.path.join(splitter.BODY_DIR, body)):
                print("Error: file {} does not exist!".format(body))
                continue
            else:
                splitter.main(head, body, '{}_{}'.format(cmd[1], cmd[2]))
                print("Composited sprite for {}_{}!".format(cmd[1], cmd[2]))

    elif cmd[0] in ('r', 'refresh'):
        importlib.reload(splitter)
        print("Refreshed sprite loader!")

    elif cmd[0] in ('q', 'quit'):
        running = False
