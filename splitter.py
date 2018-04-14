#!usr/bin/env python3
import cv2, sys, os
import numpy as np

# Fire Emblem 3DS Sprite Splitter
#
# Intended for Fire Emblem Fates and Fire Emblem Echoes sprites.
# Map sprites in the later Fire Emblem games for the 3DS (that is,
# Fates and Echoes), unlike Awakening, have separate graphics for
# the head and body components.
#
# More importantly, in addition to directional information (i.e.
# upward-, downward-, left-, and right-facing sprites), these
# graphics contain "layer" information in the form of a greyscale
# channel. This layer data is meant to correct for differences in
# hair and equipment between character classes and characters
# themselves.
#
# This program splits the layer data according to the greyscale
# mask given.


IGNORE   = [0,255] #Colors to ignore (black and white)

#Some dictionary keys
OUTDIR   = 'outputs'
HEAD_IMG = 'head'
BODY_IMG = 'body'
LARGE    = 'large'
SMALL    = 'small'
IDLE     = 'idle'
MOVE     = 'move'
SIZE     = 'size'

#Sizes for output images
HEAD_IDLE_SIZE = 128,32
HEAD_MOVE_SIZE = 128,256
BODY_IDLE_SIZE = 128,32
BODY_MOVE_SIZE = 128,256

#Used to offset for different unit colors
MOVE_BLOCK = 552
HEAD_BLOCK = 584
COLORS = {
    'purple':0,
    'green' :1,
    'red'   :2,
    'blue'  :3,
    }


#Clipping bounds for different sprite formats
CROP = {
    HEAD_IMG: {
        IDLE: {
            LARGE: {
                SIZE : (256,32),
                'start': (2,2),
                'sub'  : (32,32),
                },
            
            SMALL: {
                SIZE : (256,16),
                'start': (2,34),
                'sub'  : (16,16),
                },
            
            },

        MOVE: {
            LARGE: {
                SIZE : (256,256),
                'start': (2,68),
                'sub'  : (32,32),
                },
            
            SMALL: {
                SIZE : (256,128),
                'start': (2,406),
                'sub'  : (16,16),
                },
            
            },
        
        },
    BODY_IMG: {
        IDLE: {
            SIZE : (256,32),
            'start': (2,2),
            'sub'  : (32,32),
            },
            
        MOVE: {
            SIZE : (256,256),
            'start': (2,38),
            'sub'  : (32,32),
            },            
        },
    }

def apply_mask(img,mask):
    #Applies mask to (colored) image
    return cv2.bitwise_and(img,mask)
    

def composite(img, alpha=True):
    #Combines head and body images by grayscale layers
    h1,w1,c1 = img.shape

    #Head layer
    c1 = crop(img, (0,0), (w1//2,h1))         #Colored layer
    m1 = crop(img, (w1//2,0), (w1//2,h1))     #Masking layer
    m1 = cv2.cvtColor(m1, cv2.COLOR_RGB2BGR)  #Fix mask's color format
    g1 = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY) #Change mask to grayscale

    outputs = {}
    colors = [c for c in get_colors(g1) if c not in IGNORE]
    
    for col in colors:
        #Use grayscale bitwise masking
        m = make_mask(m1,col)
        n = apply_mask(c1,m)

        #Add alpha channel
        if alpha:
            bChannel, gChannel, rChannel = cv2.split(n)
            aChannel = np.ones(bChannel.shape, dtype=bChannel.dtype) * 255
            n = cv2.merge((bChannel,gChannel,rChannel,aChannel))
            
        outputs[col] = n

    return outputs
    

def crop(img, start, size):
    #Crops an image
    y,x = start
    h,w = size
    return img[x:x+w, y:y+h]


def fix_paths(outdir, name, color):
    #Fixes output directories (rigid, I don't really care)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    if not os.path.isdir(os.path.join(outdir,name)):
        os.makedirs(os.path.join(outdir,name))
        
    if not os.path.isdir(os.path.join(outdir,name,color)):
        os.makedirs(os.path.join(outdir,name,color))

    return os.path.join(outdir, name, color)
        

def get_colors(img):
    #Gets all unique colors from image
    return np.unique(img)


def is_grayscale(color):
    #Detects if a color is monochrome
    r,g,b = color
    return r==g==b


def make_mask(im, thresh, maxval=255):
    #Create mask from grayscale image
    r,t = cv2.threshold(im, thresh-1, maxval, cv2.THRESH_TOZERO)
    r,t = cv2.threshold(t,  thresh+1, maxval, cv2.THRESH_TOZERO_INV)
    r,t = cv2.threshold(t,  thresh-1, maxval, cv2.THRESH_BINARY)
    r,t = cv2.threshold(t,  thresh+1, maxval, cv2.THRESH_BINARY)
    return t


def main(headFile, bodyFile, size, name, offset=(0,0), alpha=True, outdir=OUTDIR):
    #Main processing method
    images = {}

    for colorType in COLORS.keys():
        headOffset = offset[0], offset[1]+HEAD_BLOCK*COLORS[colorType]
        moveOffset = offset[0], offset[1]+MOVE_BLOCK*COLORS[colorType]
    
        head = process(headFile, 'head', size, headOffset, alpha, outdir)
        body = process(bodyFile, 'body', size, moveOffset, alpha, outdir)

        #Put all idle images together
        w,h = HEAD_IDLE_SIZE
        idleBlank = np.zeros((h,w,4), np.uint8)
        idles = list(set(list(head[IDLE].keys()) + list(body[IDLE].keys())))
        idles.sort()
        for key in idles:
            if key in head[IDLE].keys():
                paste(head[IDLE][key], idleBlank, (0,0))

            if key in body[IDLE].keys():
                paste(body[IDLE][key], idleBlank, (0,0))


        path = fix_paths(outdir, name, colorType)
        cv2.imwrite(path + '/idle.png', idleBlank)

        #Put all movement images together
        w,h = HEAD_MOVE_SIZE
        moveBlank = np.zeros((h,w,4), np.uint8)
        moves = list(set(list(head[MOVE].keys()) + list(body[MOVE].keys())))
        moves.sort()
        for key in moves:
            if key in head[MOVE].keys():
                paste(head[MOVE][key], moveBlank, (0,0))
            if key in body[MOVE].keys():
                paste(body[MOVE][key], moveBlank, (0,0))

        path = fix_paths(outdir, name, colorType)
        cv2.imwrite(path + '/move.png', moveBlank)


def remove_border(img, bw, bh):
    #Removes surrounding border from image. (In-place).
    h,w,c = img.shape
    img = crop(img, (bw-1,bh-1), (w-bw,h-bh))
    return img


def replace_colors(img, color=None, replace=[0,0,0]):
    #Replaces a color in an image with another one.
    #Defaults to top-left pixel's color. (In-place).
    if color == None:
        color = img[0,0]
    img[np.where((img==color).all(axis=2))] = replace


def paste(src, dest, offset):
    #Pastes source image onto destination image
    h,w = src.shape[0], src.shape[1]
    
    x1,y1 = offset
    x2,y2 = x1+w, y1+h

    for y in range(h):
        for x in range(w):
            m,n = x1+x, y1+y
            if src[y,x,3] != 0:
                dest[n,m] = src[y,x]
    
def process(fn, type, size, offset, alpha, outdir):
    #Processes a single color-layered image
    img = cv2.imread(fn)
    replace_colors(img)
    xOff, yOff = offset

    if type==HEAD_IMG:
        #Processing for head-formatted image (idle)
        cropIdle = CROP[HEAD_IMG][IDLE][size]
        xStart, yStart = cropIdle['start']
        start = xStart+xOff, yStart+yOff
        idle = crop(img, start, cropIdle[SIZE])
        idle = composite(idle, alpha)
        if alpha:
            for k in idle.keys():
                replace_colors(idle[k],[0,0,0,255],[0,0,0,0])


        #Processing for head-formatted image (moving)
        cropMove = CROP[HEAD_IMG][MOVE][size]
        xStart, yStart = cropMove['start']
        start = xStart+xOff, yStart+yOff
        move = crop(img, start, cropMove[SIZE])
        move = composite(move, alpha)
        if alpha:
            for k in move.keys():
                replace_colors(move[k],[0,0,0,255],[0,0,0,0])

        #Fix image formatting if small size
        if size==SMALL:
            #Idle image
            w,h = HEAD_IDLE_SIZE
            for k in idle.keys():
                newIdle = np.zeros((h,w,4), np.uint8)
                for x in range(4):
                    start = x*16,0
                    size  = 16,16
                    sub   = crop(idle[k], start, size)
                    dest  = x*32-24, 0
                    paste(sub, newIdle, dest)
                idle[k] = newIdle

            #Moving image
            w,h = HEAD_MOVE_SIZE
            for k in move.keys():
                newMove = np.zeros((h,w,4), np.uint8)
                for y in range(8):
                    for x in range(4):
                        start = x*16,y*16
                        size  = 16,16
                        sub   = crop(move[k], start, size)
                        dest  = x*32-24, y*32
                        paste(sub, newMove, dest)
                move[k] = newMove

        #Format output dictionary (0: Draw head before body)
            
        return {IDLE:idle, MOVE:move, SIZE:size,}
    

    if type==BODY_IMG:
        #Processing for body-formatted image (idle)
        cropIdle = CROP[BODY_IMG][IDLE]
        xStart, yStart = cropIdle['start']
        start = xStart+xOff, yStart+yOff
        idle = crop(img, start, cropIdle[SIZE])
        idle = composite(idle, alpha)
        if alpha:
            for k in idle.keys():
                replace_colors(idle[k],[0,0,0,255],[0,0,0,0])

        #Processing for body-formatted image (moving)
        cropMove = CROP[BODY_IMG][MOVE]
        xStart, yStart = cropMove['start']
        start = xStart+xOff, yStart+yOff
        move = crop(img, start, cropMove[SIZE])
        move = composite(move, alpha)
        if alpha:
            for k in move.keys():
                replace_colors(move[k],[0,0,0,255],[0,0,0,0])

        #Format output dictionary (1: Draw body after head)
        return {IDLE:idle, MOVE:move, SIZE:None}
        
    return {}

    #for k,v in imgs.items():
    #    cv2.imwrite('{0}/{1}/{2}.png'.format(OUTDIR,name,k),v)


if __name__ == '__main__':
    head, body, size, name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[3]
    main(head,body,size,name)
    
