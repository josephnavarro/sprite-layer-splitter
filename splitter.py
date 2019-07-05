#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool

Intended for Fire Emblem Fates and Fire Emblem Echoes sprites. Map sprites in
Fire Emblem Fates and Echoes store head and body sprites separately, and store
layer information using grayscale masks. This program puts them together.

(Currently only composites the idle frames).

"""
import cv2, sys, os
import numpy as np

# Fire Emblem 3DS Sprite Compositing Tool
#
# Intended for Fire Emblem Fates and Fire Emblem Echoes sprites.
# Map sprites in Fire Emblem Fates and Echoes store head and
# body sprites separately, and store layer information using
# grayscale masks. This program puts them together.
#
# (Currently only composites the idle frames).

IGNORE = 0, 255
HEAD_DIR = 'inputs/head'
BODY_DIR = 'inputs/body'
OUTDIR = 'outputs'
COLORS = 'blue', 'red', 'green', 'purple'
HEAD_IDLE_SIZE = 128, 32
HEAD_MOVE_SIZE = 128, 256
OUTPUT_BASE = 128, 32
MOVE_BLOCK = 552
HEAD_BLOCK = 584
BASE_OFFSET_ARRAY = [(0, 0), (0, 0), (0, 0), (0, 0), ]

BODY_PARAMS = {
    # Shift unit body by this much before pasting
    'ballistician': {
        'offset': [(0, -1), (0, -1), (0, -1), (0, -1), ],
        },
    }

HEAD_PARAMS = {
    # Shift head by this much before pasting
    'adventurer-f'    : {
        'offset': [(0, 2), (0, 2), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'adventurer-m'    : {
        'offset': [(-1, 2), (-1, 2), (-1, 2), (-1, 2), ],
        'size'  : 'large',
        },
    'apothecary-f'    : {
        'offset': [(-2, 2), (-2, 1), (-2, 2), (-2, 3), ],
        'size'  : 'large',
        },
    'apothecary-m'    : {
        'offset': [(-2, 2), (-2, 1), (-2, 2), (-2, 3), ],
        'size'  : 'large',
        },
    'archer-f'        : {
        'offset': [(0, 1), (0, 1), (0, 1), (0, 0), ],
        'size'  : 'large',
        },
    'archer-m'        : {
        'offset': [(-1, 2), (-1, 2), (-1, 2), (-1, 1), ],
        'size'  : 'large',
        },
    'ballistician'    : {
        'offset': [(0, -1), (0, -1), (0, -1), (0, -1), ],
        'size'  : 'small',
        },
    'basara-f'        : {
        'offset': [(1, 2), (1, 3), (2, 3), (2, 3), ],
        'size'  : 'large',
        },
    'basara-m'        : {
        'offset': [(2, 2), (2, 3), (3, 3), (3, 3), ],
        'size'  : 'large',
        },
    'berserker-f'     : {
        'offset': [(0, 2), (0, 2), (0, 3), (0, 2), ],
        'size'  : 'large',
        },
    'berserker-m'     : {
        'offset': [(0, 2), (0, 2), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'blacksmith-f'    : {
        'offset': [(0, 0), (0, 0), (0, 0), (0, 1), ],
        'size'  : 'large',
        },
    'blacksmith-m'    : {
        'offset': [(1, 1), (1, 2), (1, 3), (1, 2), ],
        'size'  : 'large',
        },
    'bow-knight'      : {
        'offset': [(1, 0), (1, 0), (1, 0), (1, 0), ],
        'size'  : 'small',
        },
    'butler'          : {
        'offset': [(-1, 3), (-1, 3), (-1, 3), (-1, 3), ],
        'size'  : 'large',
        },
    'cavalier-f'      : {
        'offset' : [(2, -2), (2, -2), (2, -2), (2, -2), ],
        'size'   : 'small',
        'reverse': True,
        },
    'cavalier-m'      : {
        'offset' : [(2, -2), (2, -2), (2, -2), (2, -2), ],
        'size'   : 'small',
        'reverse': True,
        },
    'dark-falcon-f'   : {
        'offset' : [(1, 0), (2, 0), (2, -1), (1, -1), ],
        'size'   : 'small',
        'reverse': True,
        },
    'dark-falcon-m'   : {
        'offset' : [(1, 0), (2, 0), (2, -1), (1, -1), ],
        'size'   : 'small',
        'reverse': True,
        },
    'dark-knight'     : {
        'offset' : [(1, 0), (1, 0), (1, 0), (1, 0), ],
        'size'   : 'small',
        'reverse': True,
        },
    'dark-mage-f'     : {
        'offset': [(-1, 3), (-1, 3), (-1, 3), (-1, 3), ],
        'size'  : 'large',
        },
    'dark-mage-m'     : {
        'offset': [(-1, 3), (-1, 3), (-1, 3), (-1, 3), ],
        'size'  : 'large',
        },
    'diviner-f'       : {
        'offset': [(0, 1), (0, 1), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'diviner-m'       : {
        'offset': [(0, 2), (0, 2), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'dread-fighter-f' : {
        'offset': [(-2, 2), (-2, 2), (-2, 1), (-2, 1), ],
        'size'  : 'large',
        },
    'dread-fighter-m' : {
        'offset': [(-2, 2), (-2, 2), (-2, 1), (-2, 1), ],
        'size'  : 'large',
        },
    'falcon-knight'   : {
        'offset': [(1, 0), (2, 1), (2, 0), (1, -1), ],
        'size'  : 'small',
        },
    'fighter-f'       : {
        'offset': [(1, 1), (1, 1), (1, 2), (1, 1), ],
        'size'  : 'large',
        },
    'fighter-m'       : {
        'offset': [(1, 0), (1, 1), (1, 2), (1, 1), ],
        'size'  : 'large',
        },
    'general'         : {
        'offset': [(-4, 3), (-4, 3), (-4, 3), (-4, 3), ],
        'size'  : 'large',
        },
    'grandmaster'     : {
        'offset': [(-1, 3), (-1, 3), (-1, 3), (-1, 3), ],
        'size'  : 'large',
        },
    'great-knight'    : {
        'offset': [(1, 0), (1, 0), (1, 0), (1, 0), ],
        'size'  : 'small',
        },
    'great-lord'      : {
        'offset': [(2, 2), (2, 2), (2, 1), (2, 1), ],
        'size'  : 'large',
        },
    'great-master'    : {
        'offset': [(0, 2), (0, 2), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'hero-f'          : {
        'offset': [(1, 2), (1, 1), (1, 1), (1, 0), ],
        'size'  : 'large',
        },
    'hero-m'          : {
        'offset': [(0, 2), (0, 2), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'hoshido-noble-m' : {
        'offset': [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'  : 'large',
        },
    'hoshido-noble-f' : {
        'offset': [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'  : 'large',
        },
    'kinshi-knight'   : {
        'offset' : [(-2, 0), (-2, -2), (-2, -1), (-2, -1), ],
        'size'   : 'small',
        'reverse': True,
        },
    'kitsune-f'       : {
        'offset': [(2, 2), (2, 2), (2, 1), (2, 1), ],
        'size'  : 'large',
        },
    'kitsune-m'       : {
        'offset': [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'  : 'large',
        },
    'knight'          : {
        'offset': [(-4, 2), (-4, 2), (-4, 2), (-4, 2), ],
        'size'  : 'large',
        },
    'lodestar'        : {
        'offset': [(2, 2), (2, 2), (2, 1), (2, 1), ],
        'size'  : 'large',
        },
    'maid'            : {
        'offset': [(0, 3), (0, 3), (0, 3), (0, 3), ],
        'size'  : 'large',
        },
    'malig-knight'    : {
        'offset': [(-2, 0), (-2, -2), (-2, -1), (-2, -1)],
        'size'  : 'small',
        },
    'master-ninja-f'  : {
        'offset': [(1, 2), (1, 2), (1, 1), (1, 1), ],
        'size'  : 'large',
        },
    'master-ninja-m'  : {
        'offset': [(-3, 0), (-3, 0), (-3, -1), (-3, -1), ],
        'size'  : 'large',
        },
    'master-of-arms-f': {
        'offset': [(0, 2), (0, 2), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'master-of-arms-m': {
        'offset': [(0, 2), (0, 2), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'mechanist'       : {
        'offset': [(2, 0), (2, 0), (2, 0), (2, 0), ],
        'size'  : 'small',
        },
    'mercenary-f'     : {
        'offset': [(0, 1), (0, 0), (0, -1), (0, 0)],
        'size'  : 'large',
        },
    'mercenary-m'     : {
        'offset': [(-1, 2), (-1, 2), (-1, 1), (-1, 1), ],
        'size'  : 'large',
        },
    'merchant-f'      : {
        'offset': [(0, 2), (0, 1), (0, 0), (1, -1), ],
        'size'  : 'large',
        },
    'merchant-m'      : {
        'offset': [(-2, 2), (-2, 1), (-2, 0), (-1, -1), ],
        'size'  : 'large',
        },
    'monk'            : {
        'offset': [(0, 2), (0, 2), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'ninja-f'         : {
        'offset' : [(0, 2), (0, 2), (0, 1), (0, 1), ],
        'size'   : 'large',
        'reverse': True,
        },
    'ninja-m'         : {
        'offset': [(-2, 0), (-2, 0), (-2, -1), (-2, -1), ],
        'size'  : 'large',
        },
    'nine-tails-f'    : {
        'offset': [(0, 3), (0, 3), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'nine-tails-m'    : {
        'offset': [(0, 3), (0, 3), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'nohr-noble-f'    : {
        'offset' : [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'   : 'large',
        'reverse': True,
        },
    'nohr-noble-m'    : {
        'offset' : [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'   : 'large',
        'reverse': True,
        },
    'nohr-princess'   : {
        'offset': [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'  : 'large',
        },
    'nohr-prince'     : {
        'offset': [(-1, 3), (-1, 3), (-1, 2), (-1, 2), ],
        'size'  : 'large',
        },
    'oni-chieftain-f' : {
        'offset': [(0, 0), (0, 0), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'oni-chieftain-m' : {
        'offset': [(1, 1), (1, 2), (1, 3), (1, 2), ],
        'size'  : 'large',
        },
    'oni-savage-f'    : {
        'offset': [(0, 0), (0, 0), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'oni-savage-m'    : {
        'offset': [(1, 1), (1, 2), (1, 3), (1, 2), ],
        'size'  : 'large',
        },
    'onmyoji-f'       : {
        'offset': [(0, 1), (0, 1), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'onmyoji-m'       : {
        'offset': [(0, 1), (0, 1), (0, 1), (0, 1), ],
        'size'  : 'large',
        },
    'outlaw-f'        : {
        'offset': [(1, 2), (1, 2), (1, 2), (1, 1), ],
        'size'  : 'large',
        },
    'outlaw-m'        : {
        'offset': [(-3, 1), (-3, 0), (-3, 0), (-3, 0), ],
        'size'  : 'large',
        },
    'paladin'         : {
        'offset': [(2, 0), (2, 0), (2, 0), (2, 0), ],
        'size'  : 'small',
        },
    'priestess'       : {
        'offset': [(0, 3), (0, 3), (0, 3), (0, 3), ],
        'size'  : 'large',
        },
    'samurai-f'       : {
        'offset': [(1, 2), (1, 2), (1, 1), (1, 2), ],
        'size'  : 'large',
        },
    'samurai-m'       : {
        'offset': [(0, 0), (0, 0), (0, -1), (0, -2), ],
        'size'  : 'large',
        },
    'shrine-maiden'   : {
        'offset': [(0, 3), (0, 3), (0, 3), (0, 3), ],
        'size'  : 'large',
        },
    'sky-knight'      : {
        'offset': [(1, 0), (2, 0), (2, -1), (1, -1), ],
        'size'  : 'small',
        },
    'sniper-f'        : {
        'offset': [(0, 1), (0, 2), (0, 2), (0, 2), ],
        'size'  : 'large',
        },
    'sniper-m'        : {
        'offset': [(1, 2), (1, 3), (1, 3), (1, 3), ],
        'size'  : 'large',
        },
    'sorcerer-f'      : {
        'offset': [(0, 3), ] * 4,
        'size'  : 'large',
        },
    'sorcerer-m'      : {
        'offset': [(0, 3), ] * 4,
        'size'  : 'large',
        },
    'spear-fighter-f' : {
        'offset': [(1, 2), (1, 1), (1, 0), (1, 1), ],
        'size'  : 'large',
        },
    'spear-fighter-m' : {
        'offset': [(1, 1), (1, 1), (1, 0), (1, 2), ],
        'size'  : 'large',
        },
    'spear-master-f'  : {
        'offset': [(-1, 3), (-1, 3), (0, 3), (0, 3), ],
        'size'  : 'large',
        },
    'spear-master-m'  : {
        'offset': [(0, 3), ] * 4,
        'size'  : 'large',
        },
    'strategist'      : {
        'offset': [(1, -1), (1, 0), (1, 0), (1, 0), ],
        'size'  : 'small',
        },
    'troubadour-f'    : {
        'offset': [(1, 0), ] * 4,
        'size'  : 'small',
        },
    'troubadour-m'    : {
        'offset': [(2, 0), ] * 4,
        'size'  : 'small',
        },
    'vanguard'        : {
        'offset': [(1, 2), (1, 2), (1, 1), (1, 1), ],
        'size'  : 'large',
        },
    'villager-f'      : {
        'offset': [(1, 1), (1, 0), (1, 0), (1, 1)],
        'size'  : 'large',
        },
    'villager-m'      : {
        'offset': [(1, 1), (1, 0), (1, 0), (1, 1)],
        'size'  : 'large',
        },
    'witch'           : {
        'offset': [(-1, 2), (-1, 2), (-1, 1), (-1, 1), ],
        'size'  : 'large',
        },
    'wolfskin-f'      : {
        'offset': [(0, 3), ] * 4,
        },
    'wolfskin-m'      : {
        'offset': [(-2, -1), (-2, 0), (-2, 1), (-2, 2), ],
        },
    'wolfssegner-f'   : {
        'offset': [(0, 3), ] * 4,
        },
    'wyvern-lord'     : {
        'offset' : [(-2, 0), (-2, -2), (-2, -1), (-2, -1), ],
        'size'   : 'small',
        'reverse': True,
        },
    }

# Color offsets (multiplied by above blocks)
COLOR_OFFSETS = {
    'purple': 0,
    'green' : 1,
    'red'   : 2,
    'blue'  : 3,
    }

CROP = {
    'head': {
        'large': {
            'size' : (256, 32),
            'start': (2, 2),
            'sub'  : (32, 32),
            },
        'small': {
            'size' : (256, 16),
            'start': (2, 34),
            'sub'  : (16, 16),
            },
        },
    'body': {
        'size' : (256, 32),
        'start': (2, 2),
        'sub'  : (32, 32),
        },
    }


def apply_mask(img, mask):
    '''
    Applies mask to (colored) image.
    '''
    return cv2.bitwise_and(img, mask)


def grayscale(img, colored=False):
    '''
    Converts RGB image to grayscale.
    '''
    out = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2GRAY)
    if colored:
        # Optionally output as BGR again
        out = cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def composite(img, alpha=True):
    '''
    Overlays head and body sprites.
    '''
    h, w, color = img.shape
    color = crop(img, (0, 0), (w >> 1, h))
    mask = crop(img, (w >> 1, 0), (w >> 1, h))

    # Sort by grayscale RGB value
    output = {}
    for value in [_ for _ in get_colors(grayscale(mask)) if _ not in IGNORE]:
        n = apply_mask(color, make_mask(mask, value))
        if alpha:
            n = convert_alpha(n)
        output[value] = n
    return output


def convert_alpha(img):
    '''
    Adds alpha channel to image.
    '''
    b, g, r = cv2.split(img)
    return cv2.merge((b, g, r, np.ones(b.shape, dtype=b.dtype) * 255))


def crop(img, start, size):
    '''
    Crops an image.
    '''
    y, x = start
    h, w = size
    return img[x:x + w, y:y + h]


def fix_paths(path):
    '''
    Fixes output directories.
    '''
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path


def get_colors(img):
    '''
    Gets all unique colors from image.
    '''
    return np.unique(img)


def is_grayscale(color):
    '''
    Detects if a color is monochrome.
    '''
    r, g, b = color
    return r == g == b


def make_mask(image, thresh, maxval=255):
    '''
    Create bitmask from grayscale image.
    '''
    r, t = cv2.threshold(image, thresh - 1, maxval, cv2.THRESH_TOZERO)
    r, t = cv2.threshold(t, thresh + 1, maxval, cv2.THRESH_TOZERO_INV)
    r, t = cv2.threshold(t, thresh - 1, maxval, cv2.THRESH_BINARY)
    r, t = cv2.threshold(t, thresh + 1, maxval, cv2.THRESH_BINARY)
    return t


def main(head, body, name, offset=(0, 0), alpha=True, outdir=OUTDIR):
    '''
    Image processor entrypoint.
    '''
    w = OUTPUT_BASE[0]
    h = OUTPUT_BASE[1] * (len(COLORS) + 1)
    y = 0
    output = make_blank(w, h)

    class_base, ext = os.path.splitext(os.path.basename(body))
    if class_base not in HEAD_PARAMS:
        print("Error! Undefined character class! Continuing with defaults...")

    for color in COLORS:
        # Offset on specific unit color
        head_offset = offset[0], offset[1] + HEAD_BLOCK * COLOR_OFFSETS[color]
        body_offset = offset[0], offset[1] + MOVE_BLOCK * COLOR_OFFSETS[color]

        # Process head and body separately
        d = process(head, body, head_offset, body_offset, alpha)

        # Put all idle images together
        image = make_blank(*HEAD_IDLE_SIZE)
        ids = sorted(list(set(
            list(d['head'].keys()) + list(d['body'].keys())
            )))

        if body in HEAD_PARAMS:
            if 'reverse' in HEAD_PARAMS[body]:
                if HEAD_PARAMS[body]['reverse']:
                    ids = ids[::-1]

        # Composite head and body
        for k in ids:
            if k in d['head'].keys():
                paste(d['head'][k], image, (0, 0))

            if k in d['body'].keys():
                paste(d['body'][k], image, (0, 0))

        paste(image, output, (0, 32 * y))

        # Generate grayscale image based on blue
        y += 1
        if color == 'purple':
            gr = image.copy()
            gr = cv2.cvtColor(gr, cv2.COLOR_BGR2GRAY)
            gr = cv2.cvtColor(gr, cv2.COLOR_GRAY2BGR)
            gr = convert_alpha(gr)
            replace_colors(gr, [0, 0, 0, 255], [0, 0, 0, 0])
            paste(gr, output, (0, y * 32))

    path = fix_paths(os.path.join(outdir, name))
    cv2.imwrite(path + '/sheet.png', output)


def make_blank(w, h, channels=4):
    '''
    Makes a blank image with given size.
    '''
    return np.zeros((h, w, channels), np.uint8)


# noinspection PyUnresolvedReferences
def replace_colors(img, color=None, replace=[0, 0, 0]):
    '''
    Replaces a color in an image with another one.
    Defaults to top-left pixel's color. (In-place).
    '''
    if not color:
        color = img[0, 0]
    img[np.where((img == color).all(axis=2))] = replace


def paste(src, dest, offset):
    '''
    Pastes source image onto destination image without overwriting alpha channels.
    '''
    h, w = src.shape[0], src.shape[1]
    x1, y1 = offset

    for y in range(h):
        for x in range(w):
            m, n = x1 + x, y1 + y
            if src[y, x, 3] != 0:
                dest[n, m] = src[y, x]


def process(head_path, body_path, head_offset, body_offset, alpha):
    '''
    Processes a single color-layered image.
    '''
    try:
        head_im = cv2.imread(os.path.join(HEAD_DIR, head_path))
    except:
        print("Error! Head source {} not found! Aborting...".format(head_path))
        raise SystemExit

    try:
        body_im = cv2.imread(os.path.join(BODY_DIR, body_path))
    except:
        print("Error! Body source {} not found! Aborting...".format(body_path))
        raise SystemExit

    replace_colors(head_im)
    replace_colors(body_im)

    # Process head
    head_params = {'offset': BASE_OFFSET_ARRAY[:], 'size': 'large', }
    class_base, ext = os.path.splitext(os.path.basename(body_path))
    if class_base in HEAD_PARAMS:
        head_params.update(HEAD_PARAMS[class_base])

    offset = head_params['offset'][:]
    head_size = head_params['size']

    x, y = CROP['head'][head_size]['start']
    w, h = HEAD_IDLE_SIZE
    head = composite(crop(head_im, (x + head_offset[0], y + head_offset[1]), CROP['head'][head_size]['size']), alpha)

    if alpha:
        for p in head.keys():
            replace_colors(head[p], [0, 0, 0, 255], [0, 0, 0, 0])

    if head_size == 'large':
        for p in head:
            new_image = np.zeros((h, w, 4), np.uint8)
            for q in range(4):
                paste(crop(head[p], (q * 32, 0), (32, 32)), new_image, (q * 32 + offset[q][0], -offset[q][1]))
            head[p] = new_image

    elif head_size == 'small':
        for p in head:
            new_image = np.zeros((h, w, 4), np.uint8)
            for q in range(4):
                paste(crop(head[p], (q * 16, 0), (16, 16)), new_image, (q * 32 - 24 + offset[q][0], -offset[q][1]))
            head[p] = new_image

    # Process body
    offset = BASE_OFFSET_ARRAY[:]
    if class_base in BODY_PARAMS:
        offset = BODY_PARAMS[class_base]['offset'][:]

    offset = offset[1:4] + [offset[0]]
    x, y = CROP['body']['start']
    body = composite(crop(body_im, (x + body_offset[0], y + body_offset[1]), CROP['body']['size']), alpha)

    if alpha:
        for _ in body.keys():
            replace_colors(body[_], [0, 0, 0, 255], [0, 0, 0, 0])

    for p in body.keys():
        new_image = np.zeros((h, w, 4), np.uint8)
        for q in range(4):
            paste((crop(body[p], (q * 32, 0), (32, 32))), new_image, (q * 32 + offset[q][0], -offset[q][1]))
        body[p] = new_image

    return {'head': head, 'body': body}


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
