# Fire Emblem 3DS Sprite Splitter

## Overview
**Fire Emblem Fates** and **Fire Emblem Echoes**, in order to accomodate their class-changing systems,
store their map sprites in separate layers for the head and body. Each of these layers is further
divided into smaller components using a greyscale mask. As such, sprites ripped from these games appear
in a strange-looking format.
<br><br>
Of course, the games have their own method of putting all these images together internally, but since we
do not have access to **Nintendo's voodoo magic**, we have no choice but to composite them ourselves.
This script is intended for such compositing. All sprites used for testing were stolen without credit
from [The Spriters Resource](https://www.spriters-resource.com/3ds/fireemblemfates/).

## Usage
`python3 splitter.py <head-image> <body-image> <head-size> <output-dir>`

`<head-image>` Relative path to head spritesheet<br>
`<body-image>` Relative path to body spritesheet<br>
`<head-size>` Either one of `small` or `large`<br>
`<output-dir` Subdirectory in `outputs`<br><br>

Head size must be manually specified. Mounted units (cavalry, pegasus, wyvern, etc.) use small heads, while infantry and armored units use the larger heads.

## Dependencies
* **[Python](https://www.python.org/)** 3.4+
* **[OpenCV](https://opencv.org/)**
* **[NumPy](http://www.numpy.org/)**


## Example
### Command line arguments
`python3 inputs/odin.png inputs/bowknight.png small odin-bowknight`
### Image output
Assembled images will be output to `outputs/odin-bowknight`.
<p align="center">
<img src="examples/base1.png" alt="base1"> <img src="examples/base2.png" alt="base2"><br>
Character class and head inputs<br>
  <i>(cropped for demonstration)</i>
<br><br><br>
<img src="examples/output1.png" alt="output-1"><br>
  Idle output <i>(blue)</i><br><br>
<img src="examples/output2.png" alt="output-2"><br>
  Moving output <i>(blue)</i><br>
</p>


