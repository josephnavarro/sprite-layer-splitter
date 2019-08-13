#! usr/bin/env python3
"""
Constant definitions.
"""

IGNORE = 0, 255
HEAD_DIR = "inputs/head"
BODY_DIR = "inputs/body"
OUTDIR = "outputs"
COLORS = (
    'blue',
    'red',
    'green',
    'purple',
    )

STATE_REGION_SIZE = 128, 32
COLOR_REGION_SIZE = 128, 96  # Unit dimensions for a uniquely-colored sprite in output image
BODY_BLOCK = 96
HEAD_BLOCK = 192
BASE_OFFSET_ARRAY = [(0, 0), (0, 0), (0, 0), (0, 0)]

""" Shift body by this much before pasting. """
BODY_PARAMS = {
    "ballistician": {
        "offset": {
            "idle":  [(+0, -1), (+0, -1), (+0, -1), (+0, -1)],
            "left":  [(+0, +0), (+0, +0), (+0, +0), (+0, +0)],
            "right": [(+0, +0), (+0, +0), (+0, +0), (+0, +0)],
            },
        },
    }

""" Shift head by this much before pasting. """
HEAD_PARAMS = {
    "adventurer-f":     {
        "size":   "large",
        "offset": {
            "idle":  [(+0, +2), (+0, +2), (+0, +2), (+0, +2)],
            "left":  [(+0, +0), (+0, +0), (+0, +0), (+0, +0)],
            "right": [(+0, +0), (+0, +0), (+0, +0), (+0, +0)],
            },
        },
    "adventurer-m":     {
        "size":   "large",
        "offset": {
            "idle":  [(-1, +2), (-1, +2), (-1, +2), (-1, +2)],
            "left":  [(+0, +0), (+0, +0), (+0, +0), (+0, +0)],
            "right": [(+0, +0), (+0, +0), (+0, +0), (+0, +0)],
            },
        },
    'apothecary-f':     {
        'offset': [(-2, +2), (-2, +1), (-2, +2), (-2, +3)],
        'size':   'large'
        },
    'apothecary-m':     {'offset': [(-2, +2), (-2, +1), (-2, +2), (-2, +3)], 'size': 'large'},
    'archer-f':         {'offset': [(+0, +1), (+0, +1), (+0, +1), (+0, +0)], 'size': 'large'},
    'archer-m':         {'offset': [(-1, +2), (-1, +2), (-1, +2), (-1, +1)], 'size': 'large'},
    'ballistician':     {'offset': [(+0, -1), (+0, -1), (+0, -1), (+0, -1)], 'size': 'small'},
    'basara-f':         {'offset': [(+1, +2), (+1, +3), (+2, +3), (+2, +3)], 'size': 'large'},
    'basara-m':         {'offset': [(+2, +2), (+2, +3), (+3, +3), (+3, +3)], 'size': 'large'},
    'berserker-f':      {'offset': [(+0, +2), (+0, +2), (+0, +3), (+0, +2)], 'size': 'large'},
    'berserker-m':      {'offset': [(+0, +2), (+0, +2), (+0, +2), (+0, +2)], 'size': 'large'},
    'blacksmith-f':     {'offset': [(+0, +0), (+0, +0), (+0, +0), (+0, +1)], 'size': 'large'},
    'blacksmith-m':     {'offset': [(+1, +1), (+1, +2), (+1, +3), (+1, +2)], 'size': 'large'},
    'bow-knight':       {'offset': [(+1, +0), (+1, +0), (+1, +0), (+1, +0)], 'size': 'small'},
    'butler':           {'offset': [(-1, +3), (-1, +3), (-1, +3), (-1, +3)], 'size': 'large'},
    'cavalier-f':       {'offset': [(+2, -2), (+2, -2), (+2, -2), (+2, -2)], 'size': 'small', 'reverse': True},
    'cavalier-m':       {'offset': [(+2, -2), (+2, -2), (+2, -2), (+2, -2)], 'size': 'small', 'reverse': True},
    'dark-falcon-f':    {'offset': [(+1, +0), (+2, +0), (+2, -1), (+1, -1)], 'size': 'small', 'reverse': True},
    'dark-falcon-m':    {'offset': [(+1, +0), (+2, +0), (+2, -1), (+1, -1)], 'size': 'small', 'reverse': True},
    'dark-knight':      {'offset': [(+1, +0), (+1, +0), (+1, +0), (+1, +0)], 'size': 'small', 'reverse': True},
    'dark-mage-f':      {'offset': [(-1, +3), (-1, +3), (-1, +3), (-1, +3)], 'size': 'large'},
    'dark-mage-m':      {'offset': [(-1, +3), (-1, +3), (-1, +3), (-1, +3)], 'size': 'large'},
    'diviner-f':        {'offset': [(+0, +1), (+0, +1), (+0, +1), (+0, +1)], 'size': 'large'},
    'diviner-m':        {'offset': [(+0, +2), (+0, +2), (+0, +2), (+0, +2)], 'size': 'large'},
    'dread-fighter-f':  {'offset': [(-2, +2), (-2, +2), (-2, +1), (-2, +1)], 'size': 'large'},
    'dread-fighter-m':  {'offset': [(-2, +2), (-2, +2), (-2, +1), (-2, +1)], 'size': 'large'},
    'falcon-knight':    {'offset': [(+1, +0), (+2, +1), (+2, +0), (+1, -1)], 'size': 'small'},
    'fighter-f':        {'offset': [(+1, +1), (+1, +1), (+1, +2), (+1, +1)], 'size': 'large'},
    'fighter-m':        {'offset': [(+1, +0), (+1, +1), (+1, +2), (+1, +1)], 'size': 'large'},
    'general':          {'offset': [(-4, +3), (-4, +3), (-4, +3), (-4, +3)], 'size': 'large'},
    'grandmaster':      {'offset': [(-1, +3), (-1, +3), (-1, +3), (-1, +3)], 'size': 'large'},
    'great-knight':     {'offset': [(+1, +0), (+1, +0), (+1, +0), (+1, +0)], 'size': 'small'},
    'great-lord':       {'offset': [(+2, +2), (+2, +2), (+2, +1), (+2, +1)], 'size': 'large'},
    'great-master':     {'offset': [(+0, +2), (+0, +2), (+0, +2), (+0, +2)], 'size': 'large'},
    'hero-f':           {'offset': [(+1, +2), (+1, +1), (+1, +1), (+1, +0)], 'size': 'large'},
    'hero-m':           {'offset': [(+0, +2), (+0, +2), (+0, +1), (+0, +1)], 'size': 'large'},
    'hoshido-noble-m':  {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large'},
    'hoshido-noble-f':  {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large'},
    'kinshi-knight':    {'offset': [(-2, +0), (-2, -2), (-2, -1), (-2, -1)], 'size': 'small', 'reverse': True},
    'kitsune-f':        {'offset': [(+2, +2), (+2, +2), (+2, +1), (+2, +1)], 'size': 'large'},
    'kitsune-m':        {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large'},
    'knight':           {'offset': [(-4, +2), (-4, +2), (-4, +2), (-4, +2)], 'size': 'large'},
    'lodestar':         {'offset': [(+2, +2), (+2, +2), (+2, +1), (+2, +1)], 'size': 'large'},
    'maid':             {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'malig-knight':     {'offset': [(-2, +0), (-2, -2), (-2, -1), (-2, -1)], 'size': 'small'},
    'master-ninja-f':   {'offset': [(+1, +2), (+1, +2), (+1, +1), (+1, +1)], 'size': 'large'},
    'master-ninja-m':   {'offset': [(-3, +0), (-3, +0), (-3, -1), (-3, -1)], 'size': 'large'},
    'master-of-arms-f': {'offset': [(+0, +2), (+0, +2), (+0, +1), (+0, +1)], 'size': 'large'},
    'master-of-arms-m': {'offset': [(+0, +2), (+0, +2), (+0, +1), (+0, +1)], 'size': 'large'},
    'mechanist':        {'offset': [(+2, +0), (+2, +0), (+2, +0), (+2, +0)], 'size': 'small'},
    'mercenary-f':      {'offset': [(+0, +1), (+0, +0), (+0, -1), (+0, +0)], 'size': 'large'},
    'mercenary-m':      {'offset': [(-1, +2), (-1, +2), (-1, +1), (-1, +1)], 'size': 'large'},
    'merchant-f':       {'offset': [(+0, +2), (+0, +1), (+0, +0), (+1, -1)], 'size': 'large'},
    'merchant-m':       {'offset': [(-2, +2), (-2, +1), (-2, +0), (-1, -1)], 'size': 'large'},
    'monk':             {'offset': [(+0, +2), (+0, +2), (+0, +2), (+0, +2)], 'size': 'large'},
    'ninja-f':          {'offset': [(+0, +2), (+0, +2), (+0, +1), (+0, +1)], 'size': 'large', 'reverse': True},
    'ninja-m':          {'offset': [(-2, +0), (-2, +0), (-2, -1), (-2, -1)], 'size': 'large'},
    'nine-tails-f':     {'offset': [(+0, +3), (+0, +3), (+0, +2), (+0, +2)], 'size': 'large'},
    'nine-tails-m':     {'offset': [(+0, +3), (+0, +3), (+0, +2), (+0, +2)], 'size': 'large'},
    'nohr-noble-f':     {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large', 'reverse': True},
    'nohr-noble-m':     {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large', 'reverse': True},
    'nohr-princess':    {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large'},
    'nohr-prince':      {'offset': [(-1, +3), (-1, +3), (-1, +2), (-1, +2)], 'size': 'large'},
    'oni-chieftain-f':  {'offset': [(+0, +0), (+0, +0), (+0, +1), (+0, +1)], 'size': 'large'},
    'oni-chieftain-m':  {'offset': [(+1, +1), (+1, +2), (+1, +3), (+1, +2)], 'size': 'large'},
    'oni-savage-f':     {'offset': [(+0, +0), (+0, +0), (+0, +1), (+0, +1)], 'size': 'large'},
    'oni-savage-m':     {'offset': [(+1, +1), (+1, +2), (+1, +3), (+1, +2)], 'size': 'large'},
    'onmyoji-f':        {'offset': [(+0, +1), (+0, +1), (+0, +1), (+0, +1)], 'size': 'large'},
    'onmyoji-m':        {'offset': [(+0, +1), (+0, +1), (+0, +1), (+0, +1)], 'size': 'large'},
    'outlaw-f':         {'offset': [(+1, +2), (+1, +2), (+1, +2), (+1, +1)], 'size': 'large'},
    'outlaw-m':         {'offset': [(-3, +1), (-3, +0), (-3, +0), (-3, +0)], 'size': 'large'},
    'paladin':          {'offset': [(+2, +0), (+2, +0), (+2, +0), (+2, +0)], 'size': 'small'},
    'priestess':        {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'samurai-f':        {'offset': [(+1, +2), (+1, +2), (+1, +1), (+1, +2)], 'size': 'large'},
    'samurai-m':        {'offset': [(+0, +0), (+0, +0), (+0, -1), (+0, -2)], 'size': 'large'},
    'shrine-maiden':    {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'sky-knight':       {'offset': [(+1, +0), (+2, +0), (+2, -1), (+1, -1)], 'size': 'small'},
    'sniper-f':         {'offset': [(+0, +1), (+0, +2), (+0, +2), (+0, +2)], 'size': 'large'},
    'sniper-m':         {'offset': [(+1, +2), (+1, +3), (+1, +3), (+1, +3)], 'size': 'large'},
    'sorcerer-f':       {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'sorcerer-m':       {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'spear-fighter-f':  {'offset': [(+1, +2), (+1, +1), (+1, +0), (+1, +1)], 'size': 'large'},
    'spear-fighter-m':  {'offset': [(+1, +1), (+1, +1), (+1, +0), (+1, +2)], 'size': 'large'},
    'spear-master-f':   {'offset': [(-1, +3), (-1, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'spear-master-m':   {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], 'size': 'large'},
    'strategist':       {'offset': [(+1, -1), (+1, +0), (+1, +0), (+1, +0)], 'size': 'small'},
    'troubadour-f':     {'offset': [(+1, +0), (+1, +0), (+1, +0), (+1, +0)], 'size': 'small'},
    'troubadour-m':     {'offset': [(+2, +0), (+2, +0), (+2, +0), (+2, +0)], 'size': 'small'},
    'vanguard':         {'offset': [(+1, +2), (+1, +2), (+1, +1), (+1, +1)], 'size': 'large'},
    'villager-f':       {'offset': [(+1, +1), (+1, +0), (+1, +0), (+1, +1)], 'size': 'large'},
    'villager-m':       {'offset': [(+1, +1), (+1, +0), (+1, +0), (+1, +1)], 'size': 'large'},
    'witch':            {'offset': [(-1, +2), (-1, +2), (-1, +1), (-1, +1)], 'size': 'large'},
    'wolfskin-f':       {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], },
    'wolfskin-m':       {'offset': [(-2, -1), (-2, +0), (-2, +1), (-2, +2)], },
    'wolfssegner-f':    {'offset': [(+0, +3), (+0, +3), (+0, +3), (+0, +3)], },
    'wyvern-lord':      {'offset': [(-2, +0), (-2, -2), (-2, -1), (-2, -1)], 'size': 'small', 'reverse': True},
    }

""" Color offsets (multiplied by above blocks) """
COLOR_OFFSETS = {
    "purple": 0,
    "green":  1,
    "red":    2,
    "blue":   3,
    }

""" Spritesheet cropping subsurface regions. """
CROP = {
    "head": {
        "large": {
            "size":  (256, 32),
            "sub":   (32, 32),
            "start": {
                "idle":  (0, 0),
                "left":  (0, 64),
                "right": (0, 96),
                },
            },
        "small": {
            "size":  (256, 16),
            "sub":   (16, 16),
            "start": {
                "idle":  (0, 32),
                "left":  (0, 127),
                "right": (0, 143),
                }
            },
        },

    "body": {
        "size":  (256, 96),
        "sub":   (32, 32),
        "start": {
            "idle":  (0, 0),
            "left":  (0, 32),
            "right": (0, 64),
            },

        },
    }
