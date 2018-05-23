#!usr/bin/env python3
import cv2, sys, os
import numpy as np

# Fire Emblem 3DS Sprite Splitter
#
# Intended for Fire Emblem Fates and Fire Emblem Echoes sprites.
# Map sprites in Fire Emblem Fates and Echoes store head and
# body sprites separately, and give layer information via
# grayscale masks. This program puts them together

IGNORE = 0,255 #Ignored colors (black and white)

#Some dictionary keys
HEAD_IMG = 'head'
BODY_IMG = 'body'
LARGE    = 'large'
SMALL    = 'small'
IDLE     = 'idle'
MOVE     = 'move'
SIZE     = 'size'
START    = 'start'
SUB      = 'sub'

#Directory strings
OUTDIR = 'outputs'

#Output image dimensions
HEAD_IDLE_SIZE = 128,32
HEAD_MOVE_SIZE = 128,256
BODY_IDLE_SIZE = 128,32
BODY_MOVE_SIZE = 128,256
OUTPUT_BASE    = 128,32

#Pixel offsets for unit colors
MOVE_BLOCK = 552
HEAD_BLOCK = 584

#Color offsets (multiplied by above blocks)
COLORS = {
    'purple':0,
    'green' :1,
    'red'   :2,
    'blue'  :3,
    }

#Clipping bounds for different sprite formats
CROP = {
    HEAD_IMG: {
        #Characters
        IDLE: {
            LARGE: {
                #Large head idle poses
                SIZE : (256,32),
                START: (2,2),
                SUB  : (32,32),
                },
            
            SMALL: {
                #Small head idle poses
                SIZE : (256,16),
                START: (2,34),
                SUB  : (16,16),
                },
            
            },

        MOVE: {
            LARGE: {
                #Large head moving poses
                SIZE : (256,256),
                START: (2,68),
                SUB  : (32,32),
                },
            
            SMALL: {
                #Small head moving poses
                SIZE : (256,128),
                START: (2,406),
                SUB  : (16,16),
                },
            },        
        },
    
    BODY_IMG: {
        #Character classes
        IDLE: {
            #Idle poses
            SIZE : (256,32),
            START: (2,2),
            SUB  : (32,32),
            },
            
        MOVE: {
            #Moving poses
            SIZE : (256,256),
            START: (2,38),
            SUB  : (32,32),
            },            
        },
    }

def apply_mask(img, mask):
    #Applies mask to (colored) image
    return cv2.bitwise_and(img,mask)


def grayscale(img, colored=False):
    #Converts RGB image to grayscale
    out = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
    
    if colored:
        #Optionally output BGR again
        out = cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def composite(img, alpha=True):
    #Overlays head and body sprites
    h1,w1,c1 = img.shape

    #Head layer
    c1 = crop(img, (0,0), (w1//2,h1))     #Color layer
    m1 = crop(img, (w1//2,0), (w1//2,h1)) #Mask layer
    g1 = grayscale(m1)

    #Outputs sorted by grayscale for layering
    outputs = {}
    colors = [c for c in get_colors(g1) if c not in IGNORE]
    
    for col in colors:
        #Bitwise masking
        m = make_mask(m1,col)
        n = apply_mask(c1,m)

        #Add alpha channel
        if alpha:
            n = convert_alpha(n)
        outputs[col] = n

    return outputs


def convert_alpha(img):
    #Adds alpha channel to image
    bChannel, gChannel, rChannel = cv2.split(img)
    aChannel = np.ones(bChannel.shape, dtype=bChannel.dtype) * 255
    return cv2.merge((bChannel,gChannel,rChannel,aChannel))
    

def crop(img, start, size):
    #Crops an image
    y,x = start
    h,w = size
    return img[x:x+w, y:y+h]


def fix_paths(path):
    #Fixes output directories
    path = os.path.normpath(path)
    os.makedirs(path, exist_ok=True)
    return path


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
    colorKeys = 'blue','red','green','purple'
    n = len(colorKeys) + 1
    w,h = OUTPUT_BASE[0], OUTPUT_BASE[1] * n
    outImage = make_blank(w,h)
    yPos = 0

    for colorType in colorKeys:
        #Offset for specific unit color
        headOffset = offset[0], offset[1]+HEAD_BLOCK*COLORS[colorType]
        moveOffset = offset[0], offset[1]+MOVE_BLOCK*COLORS[colorType]

        #Process head and body separately
        head = process(headFile, 'head', size, headOffset, alpha, outdir)
        body = process(bodyFile, 'body', size, moveOffset, alpha, outdir)

        #Put all idle images together
        idleBlank = make_blank(*HEAD_IDLE_SIZE)
        idles = sorted(list(set(
            list(head[IDLE].keys()) + list(body[IDLE].keys())
            )))

        #Composite head and body
        for key in idles:
            if key in head[IDLE].keys():
                paste(head[IDLE][key], idleBlank, (0,0))

            if key in body[IDLE].keys():
                paste(body[IDLE][key], idleBlank, (0,0))

        paste(idleBlank, outImage, (0,yPos*32))

        #Generate grayscale image based on blue
        yPos += 1
        if colorType == 'purple':
            idleGray = idleBlank.copy()
            idleGray = cv2.cvtColor(idleGray, cv2.COLOR_BGR2GRAY)
            idleGray = cv2.cvtColor(idleGray, cv2.COLOR_GRAY2BGR)
            idleGray = convert_alpha(idleGray)
            replace_colors(idleGray, [0,0,0,255], [0,0,0,0])
            paste(idleGray, outImage, (0,yPos*32))

    path = fix_paths(os.path.join(outdir, name))
    cv2.imwrite(path + '/sheet.png', outImage)
    

def make_blank(w,h,channels=4):
    #Makes a blank image with given size
    return np.zeros((h,w,channels), np.uint8)


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
        xStart, yStart = cropIdle[START]
        start = xStart+xOff, yStart+yOff
        idle = crop(img, start, cropIdle[SIZE])
        idle = composite(idle, alpha)
        if alpha:
            for k in idle.keys():
                replace_colors(idle[k],[0,0,0,255],[0,0,0,0])

        #Processing for head-formatted image (moving)
        cropMove = CROP[HEAD_IMG][MOVE][size]
        xStart, yStart = cropMove[START]
        start = xStart+xOff, yStart+yOff
        move = crop(img, start, cropMove[SIZE])
        move = composite(move, alpha)
        if alpha:
            for k in move.keys():
                replace_colors(move[k],[0,0,0,255],[0,0,0,0])

        #Fix image formatting if small size
        if size==LARGE:
            w,h = HEAD_IDLE_SIZE
            for k in idle.keys():
                newIdle = np.zeros((h,w,4), np.uint8)
                for x in range(4):
                    start = x*32,0
                    size = 32,32
                    sub = crop(idle[k], start, size)
                    dest = x*32, -1 if x==3 else -2
                    paste(sub, newIdle, dest)
                idle[k] = newIdle
                
        if size==SMALL:
            #Idle image
            w,h = HEAD_IDLE_SIZE
            for k in idle.keys():
                newIdle = np.zeros((h,w,4), np.uint8)
                for x in range(4):
                    start = x*16,0
                    size  = 16,16
                    sub   = crop(idle[k], start, size)
                    dest  = x*32-24 - 2, 3 + (-1 if x==3 else -2)
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
        xStart, yStart = cropIdle[START]
        start = xStart+xOff, yStart+yOff
        idle = crop(img, start, cropIdle[SIZE])
        idle = composite(idle, alpha)
        if alpha:
            for k in idle.keys():
                replace_colors(idle[k],[0,0,0,255],[0,0,0,0])

        #Processing for body-formatted image (moving)
        cropMove = CROP[BODY_IMG][MOVE]
        xStart, yStart = cropMove[START]
        start = xStart+xOff, yStart+yOff
        move = crop(img, start, cropMove[SIZE])
        move = composite(move, alpha)
        if alpha:
            for k in move.keys():
                replace_colors(move[k],[0,0,0,255],[0,0,0,0])

        #Format output dictionary (1: Draw body after head)
        return {IDLE:idle, MOVE:move, SIZE:None}
        
    return {}


if __name__ == '__main__':
    head, body, size, name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[3]
    main(head,body,size,name)
    
