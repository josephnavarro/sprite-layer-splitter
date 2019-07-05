#!usr/bin/env python3
import splitter, importlib, os

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

running = True

while running:
    command = input(PROMPT).lower().split()
    if not command:
        continue

    if command[0] in ('c', 'composite'):
        if len(command) != 3:
            continue

        head = FILE_STRING.format(command[1])
        body = FILE_STRING.format(command[2])

        if not os.path.exists(head):
            print("Error: file {} does not exist!".format(head))
            continue
        if not os.path.exists(body):
            print("Error: file {} does not exist!".format(body))
            continue

        splitter.main(head, body, '{}_{}'.format(command[1], command[2]))
        print("Composited sprite for {}_{}!".format(command[1], command[2]))

    elif command[0] in ('r', 'refresh'):
        importlib.reload(splitter)
        print("Refreshed sprite loader!")

    elif command[0] in ('q', 'quit'):
        running = False

