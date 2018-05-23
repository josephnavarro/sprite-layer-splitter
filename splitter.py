#!usr/bin/env python3
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
OUTDIR = 'outputs'
HEAD_IDLE_SIZE = 128,32
HEAD_MOVE_SIZE = 128,256
OUTPUT_BASE = 128,32
MOVE_BLOCK = 552
HEAD_BLOCK = 584

BASE_OFFSET_ARRAY = [(0,0),(0,0),(0,0),(0,0),]

# Sprite offsets exist on a class-by-class basis.
# Found this out the hard way.

BODY_PARAMS = {
    # Shift unit body by this much before pasting
    'ballistician': {
        'offset': [(0,-1),(0,-1),(0,-1),(0,-1),],
        },
    }

HEAD_PARAMS = {
    # Shift head by this much before pasting
    'adventurer-f': {
        'offset': [(0,2),(0,2),(0,2),(0,2),],
        'size': 'large',
        },
    'adventurer-m': {
        'offset': [(-1,2),(-1,2),(-1,2),(-1,2),],
        'size': 'large',
        },
    'apothecary-f': {
        'offset': [(-2,2),(-2,1),(-2,2),(-2,3),],
        'size': 'large',
        },
    'apothecary-m': {
        'offset': [(-2,2),(-2,1),(-2,2),(-2,3),],
        'size': 'large',
        },
    'archer-f': {
        'offset': [(0,1),(0,1),(0,1),(0,0),],
        'size': 'large',
        },
    'archer-m': {
        'offset': [(-1,2),(-1,2),(-1,2),(-1,1),],
        'size': 'large',
        },
    'ballistician': {
        'offset': [(0,-1),(0,-1),(0,-1),(0,-1),],
        'size': 'small',
        },
    'basara-f': {
        'offset': [(1,2),(1,3),(2,3),(2,3),],
        'size': 'large',
        },
    'basara-m': {
        'offset': [(2,2),(2,3),(3,3),(3,3),],
        'size': 'large',
        },
    'berserker-f': {
        'offset': [(0,3),(0,3),(0,3),(0,3),],
        'size': 'large',
        },
    'berserker-m': {
        'offset': [(0,2),(0,2),(0,2),(0,2),],
        'size': 'large',
        },
    'blacksmith-f': {
        'offset': [(0,0),(0,0),(0,0),(0,1),],
        'size': 'large',
        },
    'blacksmith-m': {
        'offset': [(1,1),(1,2),(1,3),(1,2),],
        'size': 'large',
        },
    'bow-knight': {
        'offset': [(1,0),(1,0),(1,0),(1,0),],
        'size': 'small',
        },
    'butler': {
        'offset': [(-1,3),(-1,3),(-1,3),(-1,3),],
        'size': 'large',
        },
    'cavalier-f': {
        'offset': [(2,-2),(2,-2),(2,-2),(2,-2),],
        'size': 'small',
        },
    'cavalier-m': {
        'offset': [(2,-2),(2,-2),(2,-2),(2,-2),],
        'size': 'small',
        },
    }

#Color offsets (multiplied by above blocks)
COLOR_OFFSETS = {
    'purple': 0,
    'green': 1,
    'red': 2,
    'blue': 3,
    }

#Clipping bounds for different sprite formats
CROP = {
    'head': { # Characters
        'idle': {
            'large': { # Large head idle poses
                'size' : (256,32),
                'start': (2,2),
                'sub'  : (32,32),
                },
            
            'small': { # Small head idle poses
                'size' : (256,16),
                'start': (2,34),
                'sub'  : (16,16),
                },
            },

        'move': {
            'large': { # Large head moving poses
                'size' : (256,256),
                'start': (2,68),
                'sub'  : (32,32),
                },
            
            'small': { # Small head moving poses
                'size' : (256,128),
                'start': (2,406),
                'sub'  : (16,16),
                },
            },        
        },
    
    'body': { # Character classes
        
        'idle': { # Idle poses
            'size' : (256,32),
            'start': (2,2),
            'sub'  : (32,32),
            },
        
        'move': { # Moving poses
            'size' : (256,256),
            'start': (2,38),
            'sub'  : (32,32),
            },            
        },
    }

def apply_mask(img, mask):
    '''Applies mask to (colored) image.'''
    return cv2.bitwise_and(img,mask)


def grayscale(img, colored=False):
    '''Converts RGB image to grayscale.'''
    out = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    
    if colored: # Optionally output as BGR again
        out = cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def composite(img, alpha=True):
    '''Overlays head and body sprites.'''
    h1,w1,c1 = img.shape

    # Head layer
    c1 = crop(img, (0,0), (w1//2,h1)) # Color
    m1 = crop(img, (w1//2,0), (w1//2,h1)) # Bitmask
    g1 = grayscale(m1)

    # Outputs categorized by grayscale value
    outputs = {}
    colors = [c for c in get_colors(g1) if c not in IGNORE]
    for col in colors:
        m = make_mask(m1,col)
        n = apply_mask(c1,m)
        if alpha:
            n = convert_alpha(n)
        outputs[col] = n

    return outputs


def convert_alpha(img):
    '''Adds alpha channel to image.'''
    bChannel, gChannel, rChannel = cv2.split(img)
    aChannel = np.ones(bChannel.shape, dtype=bChannel.dtype) * 255
    return cv2.merge((bChannel,gChannel,rChannel,aChannel))
    

def crop(img, start, size):
    '''Crops an image.'''
    y,x = start
    h,w = size
    return img[x:x+w, y:y+h]


def fix_paths(path):
    '''Fixes output directories.'''
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path


def get_colors(img):
    '''Gets all unique colors from image.'''
    return np.unique(img)


def is_grayscale(color):
    '''Detects if a color is monochrome.'''
    r, g, b = color
    return r==g==b


def make_mask(im, thresh, maxval=255):
    '''Create bitmask from grayscale image.'''
    r,t = cv2.threshold(im, thresh-1, maxval, cv2.THRESH_TOZERO)
    r,t = cv2.threshold(t,  thresh+1, maxval, cv2.THRESH_TOZERO_INV)
    r,t = cv2.threshold(t,  thresh-1, maxval, cv2.THRESH_BINARY)
    r,t = cv2.threshold(t,  thresh+1, maxval, cv2.THRESH_BINARY)
    return t


def main(hd, bd, name, offset=(0,0), alpha=True, outdir=OUTDIR):
    '''Image processor entrypoint.'''
    images = {}
    colorKeys = 'blue','red','green','purple'
    w, h = OUTPUT_BASE[0], OUTPUT_BASE[1] * (len(colorKeys) + 1)
    output = make_blank(w, h)
    y = 0

    for c in colorKeys:
        #Offset for specific unit color
        hpos = offset[0], offset[1] + HEAD_BLOCK * COLOR_OFFSETS[c]
        mpos = offset[0], offset[1] + MOVE_BLOCK * COLOR_OFFSETS[c]

        #Process head and body separately
        d = process(hd, bd, hpos, mpos, alpha, outdir)

        #Put all idle images together
        idb = make_blank(*HEAD_IDLE_SIZE)
        ids = sorted(list(set(
            list(d['head'].keys()) + list(d['body'].keys())
            )))[::-1]

        #Composite head and body
        for k in ids:
            if k in d['head'].keys():
                paste(d['head'][k], idb, (0,0))

            if k in d['body'].keys():
                paste(d['body'][k], idb, (0,0))

        paste(idb, output, (0, 32*y))

        #Generate grayscale image based on blue
        y += 1
        if c == 'purple':
            gr = idb.copy()
            gr = cv2.cvtColor(gr, cv2.COLOR_BGR2GRAY)
            gr = cv2.cvtColor(gr, cv2.COLOR_GRAY2BGR)
            gr = convert_alpha(gr)
            replace_colors(gr, [0,0,0,255], [0,0,0,0])
            paste(gr, output, (0,y*32))

    path = fix_paths(os.path.join(outdir, name))
    cv2.imwrite(path + '/sheet.png', output)
    

def make_blank(w,h,channels=4):
    '''Makes a blank image with given size.'''
    return np.zeros((h,w,channels), np.uint8)


def remove_border(img, bw, bh):
    '''Removes surrounding border from image. (In-place).'''
    h,w,c = img.shape
    img = crop(img, (bw-1,bh-1), (w-bw,h-bh))
    return img


def replace_colors(img, color=None, replace=[0,0,0]):
    '''
    Replaces a color in an image with another one.
    Defaults to top-left pixel's color. (In-place).
    '''
    if color == None:
        color = img[0,0]
    img[np.where((img==color).all(axis=2))] = replace


def paste(src, dest, offset):
    '''Pastes source image onto destination image.'''
    h,w = src.shape[0], src.shape[1]
    x1,y1 = offset
    x2,y2 = x1+w, y1+h

    for y in range(h):
        for x in range(w):
            m,n = x1+x, y1+y
            if src[y,x,3] != 0:
                dest[n,m] = src[y,x]

    
def process(hd, bd, hoff, boff, alpha, outdir):
    '''Processes a single color-layered image.'''
    hbase, ext = os.path.splitext(os.path.basename(hd))
    bbase, ext = os.path.splitext(os.path.basename(bd))
    himg = cv2.imread(hd)
    bimg = cv2.imread(bd)
    hsize = 'large'

    replace_colors(himg)
    replace_colors(bimg)
    
    offset = [(0,0), (0,0), (0,0), (0,0)]


    if bbase in HEAD_PARAMS:
        offset = HEAD_PARAMS[bbase]['offset'][:]
        hsize = HEAD_PARAMS[bbase]['size']


    #offset = offset[1:4] + [offset[0]]
    head = CROP['head']['idle'][hsize]
    
    xStart, yStart = head['start']
    start = xStart + hoff[0], yStart + hoff[1]
    idleh = composite(crop(himg, start, head['size']), alpha)
    
    if alpha:
        for k in idleh.keys():
            replace_colors(idleh[k], [0,0,0,255], [0,0,0,0])

    if hsize == 'large':
        # Large head size
        w,h = HEAD_IDLE_SIZE
        
        for k in idleh.keys():
            newIdle = np.zeros((h,w,4), np.uint8)
            
            for x in range(4):
                start = x*32,0
                size = 32,32
                sub = crop(idleh[k], start, size)
                dest = x*32 + offset[x][0], -offset[x][1]
                paste(sub, newIdle, dest)
                
            idleh[k] = newIdle
            
    elif hsize == 'small':
        # Small head size
        w,h = HEAD_IDLE_SIZE
        
        for k in idleh.keys():
            newIdle = np.zeros((h,w,4), np.uint8)
            
            for x in range(4):
                start = x*16,0
                size = 16,16
                sub = crop(idleh[k], start, size)
                dest = x*32-24 + offset[x][0], -offset[x][1]
                paste(sub, newIdle, dest)
                
            idleh[k] = newIdle
    

    #Processing for body-formatted image (idle)
    offset = [(0,0), (0,0), (0,0), (0,0)]
    if bbase in BODY_PARAMS:
        offset = BODY_PARAMS[bbase]['offset'][:]

    offset = offset[1:4] + [offset[0]]
        
    body = CROP['body']['idle']
    xStart, yStart = body['start']
    start = xStart + boff[0], yStart + boff[1]
    idleb = composite(crop(bimg, start, body['size']), alpha)
    
    if alpha:
        for k in idleb.keys():
            replace_colors(idleb[k],[0,0,0,255],[0,0,0,0])

    for k in idleb.keys():
        newIdle = np.zeros((h,w,4), np.uint8)
        
        for x in range(4):
            start = x*32,0
            size = 32,32
            sub = crop(idleb[k], start, size)
            dest = x*32 + offset[x][0], -offset[x][1]
            paste(sub, newIdle, dest)
            
        idleb[k] = newIdle

        
    return {'head': idleh, 'body': idleb}


if __name__ == '__main__':
    head, body, name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[3]
    main(head,body,name)
    
