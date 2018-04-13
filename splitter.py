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


IGNORE  = [0,255] #Colors to ignore (black and white)
DIRNAME = 'outputs'

def apply_mask(img,mask):
    #Applies mask to (colored) image
    return cv2.bitwise_and(img,mask)
    

def composite(img):
    #Combines head and body images by grayscale layers
    h1,w1,c1 = img.shape

    #Head layer
    c1 = crop(img, (0,0), (w1//2,h1))         #Color
    #c1 = cv2.cvtColor(c1, cv2.COLOR_RGB2BGR)  #Fix color
    m1 = crop(img, (w1//2,0), (w1//2,h1))     #Mask
    m1 = cv2.cvtColor(m1, cv2.COLOR_RGB2BGR)  #Fix color
    g1 = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY) #Grayscale

    outputs = {}
    colors = [c for c in get_colors(g1) if c not in IGNORE]
    for col in colors:
        m = make_mask(m1,col)
        n = apply_mask(c1,m)
        outputs[col] = n

    return outputs
    

def crop(img, start, size):
    #Crops an image
    y,x = start
    h,w = size
    return img[x:x+w, y:y+h]
    

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


def process(fn,name,outdir=DIRNAME):
    #Processes a single color-layered image
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        
    if not os.path.isdir(os.path.join(outdir,name)):
        os.makedirs(os.path.join(outdir,name))
        
    img = cv2.imread(fn)
    replace_colors(img)
    img = remove_border(img, 4,4)
    imgs = composite(img)

    for k,v in imgs.items():
        cv2.imwrite('{0}/{1}/{2}.png'.format(DIRNAME,name,k),v)


if __name__ == '__main__':
    process(sys.argv[1], sys.argv[2])  
    
