#!usr/bin/env python3
import splitter, importlib

# Image splitting tests. All spritesheets used in these
# examples were taken from The Spriters Resource.
# (https://www.spriters-resource.com/3ds/fireemblemfates/)

FILE_STRING = 'inputs/{}.png'
PROMPT = '''
Commands:
[c]omposite <unit> <class> -> Composite new sprite
[r]efresh -> Refresh sprite loader
[q]uit -> Quit application

What do?
>>> '''

doContinue = True

while doContinue:
    cmd = input(PROMPT).lower().split()
    if not cmd:
        continue

    if cmd[0] in ('c', 'composite'):
        if len(cmd) != 3:
            continue
        
        splitter.main(
            FILE_STRING.format(cmd[1]),
            FILE_STRING.format(cmd[2]),
            '{}_{}'.format(cmd[1], cmd[2]),
            )

        print("Composited sprite for {}_{}!".format(cmd[1], cmd[2]))

    elif cmd[0] in ('r', 'refresh'):
        importlib.reload(splitter)
        print("Refreshed sprite loader!")

    elif cmd[0] in ('q', 'quit'):
        doContinue = False
        
