#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Intended for Fire Emblem Fates and Fire Emblem Echoes sprites. Map sprites in
Fire Emblem Fates and Echoes store head and body sprites separately, and store
layer information using grayscale masks. This program puts them together.

"""
import itertools
from sprite_json import *
from sprite_imaging import *
from sprite_utils import *


"""
Head source image error string.
"""
HEAD_SRC_NOT_FOUND: str = "Error! Head source image {} not found! Aborting..."

"""
Body source image error string.
"""
BODY_SRC_NOT_FOUND: str = "Error! Body source image {} not found! Aborting..."


class NonexistentHeadException(Exception):
    """
    Exception thrown upon referencing a nonexistent head spritesheet.
    """

    def __init__(self, name):
        super().__init__()
        self.filename = name


class NonexistentBodyException(Exception):
    """
    Exception thrown upon referencing a nonexistent body spritesheet.
    """

    def __init__(self, name):
        super().__init__()
        self.filename = name


def SortedSet(*lists, reverse=False):
    """
    Sorts unique elements among one or more input lists.

    :param lists:   Lists containing elements to sort.
    :param reverse: Whether to reverse output list. (Default False).

    :return: Sorted list of unique elements.
    """
    outList = sorted(list(set(itertools.chain(*[list(x) for x in lists]))))
    if reverse:
        outList.reverse()
    return outList


def PasteLayers(dest, head, body, layers, *, headfirst=True, reverse=False):
    """
    Pastes head and body subregions in proper layering order.
    (In-place).

    :param dest:      Destination image to paste to.
    :param head:      Head compositing data.
    :param body:      Body compositing data.
    :param layers:    List of layers to process.
    :param headfirst: Whether to paste head first. (Default True).
    :param reverse:   Whether to invert layers. (Default False).

    :return: None.
    """
    # Experimental!!
    if reverse:
        layers = layers[::-1]

    for layer in layers:
        if headfirst:
            try:
                # Paste head first, body second
                Paste(dest, head[layer], (0, 0))
            except KeyError:
                pass
            try:
                Paste(dest, body[layer], (0, 0))
            except KeyError:
                pass

        else:
            try:
                # Paste body first, head second
                Paste(dest, body[layer], (0, 0))
            except KeyError:
                pass
            try:
                Paste(dest, head[layer], (0, 0))
            except KeyError:
                pass


def Split(image):
    """
    Isolates irregular regions on an image, then sorts by luminosity.

    :param image: Image to extract regions from.

    :return: Dictionary mapping luminosity to sprite layers.
    """
    h, w, channels = image.shape
    base = Crop(image, [0, 0], [w >> 1, h])
    mask = ReplaceColor(Crop(image, [w >> 1, 0], [w >> 1, h]),
                        [255, 255, 255],
                        [252, 252, 252])

    # Isolate regions and sort into layers
    return {p: ConvertAlpha(ApplyMask(base, MakeMask(mask, p)))
            for p in [q for q in GetUniqueColors(ToGrayscale(mask))
                      if q not in IGNORED_COLORS]}


def GetBodyOffsets(name, data):
    """
    Retrieves framewise offset data for body sprites.

    :param name: Key mapping to desired body data.
    :param data: Full body data.

    :return: Offsetting data for idle, left-, and right-facing frames.
    """
    offsets = data.get(name, {}).get("offset", {})
    return {
        "idle":  offsets.get("idle", BASE_OFFSETS)[:],
        "left":  offsets.get("left", BASE_OFFSETS)[:],
        "right": offsets.get("right", BASE_OFFSETS)[:]
    }


def GetBodyOrder(name, data):
    """
    Retrieves frame ordering data for body sprites.

    :param name: Key mapping to desired body data.
    :param data: Full body data.

    :return: Order of iteration for idle-, left-, and right-facing frames.
    """
    order = data.get(name, {}).get("order", {})
    return {
        "idle":  order.get("idle", BASE_ORDER[:]),
        "left":  order.get("left", BASE_ORDER[:]),
        "right": order.get("right", BASE_ORDER[:])
    }


def GetHeadOffsets(name, data):
    """
    Retrieves framewise offset data for head sprites.

    :param name: Key mapping to head data.
    :param data: Full head data.

    :return: Offsetting data for idle, left-, and right-facing frames.
    """
    offsets = data.get(name, {}).get("offset", {})
    return {
        "idle":  offsets.get("idle", BASE_OFFSETS)[:],
        "left":  offsets.get("left", BASE_OFFSETS)[:],
        "right": offsets.get("right", BASE_OFFSETS)[:],
        "size":  data.get(name, {}).get("size", "large")
    }


def GetHeadOrder(name, data):
    """
    Retrieves frame ordering data for head sprites.

    :param name: Key mapping to desired head data.
    :param data: Full head data.

    :return: Order of iteration for idle-, left-, and right-facing frames.
    """
    order = data.get(name, {}).get("order", {})
    return {
        "idle":  order.get("idle", BASE_ORDER[:]),
        "left":  order.get("left", BASE_ORDER[:]),
        "right": order.get("right", BASE_ORDER[:])
    }


def ProcessBody(name, image, where, body_data, source_data, is_alpha):
    """
    Processes a unit's body sprite.

    :param name:        Spritesheet's base name.
    :param image:       Source image to crop from.
    :param where:       X-Y offset to colored region on source spritesheet.
    :param body_data:   Body compositing data from file.
    :param source_data: Source referencing data from file.
    :param is_alpha:    Whether to replace black with transparency.

    :return: Dictionary mapping luminosities to image layers.
    """
    layers = Split(Crop(image, where, REGION_FULL_BODY))
    if is_alpha:
        layers = {k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0])
                  for k, v in layers.items()}

    data = GetBodyOffsets(name, body_data)
    order = GetBodyOrder(name, body_data)
    size = source_data["body"]["size"]
    where = source_data["body"]["where"]

    output = {}
    for state in STATES:
        dx = +0
        if state == "right":
            dy = +32 * 2
        elif state == "left":
            dy = +32 * 1
        else:
            dy = +32 * 0

        output[state] = {}
        for layer, image in layers.items():
            # Make blank image with room for 4 sprite frames
            shape = (COLOR_REGION[1], COLOR_REGION[0], 4)
            frame = np.zeros(shape, np.uint8)

            for n in range(4):
                whereX = where[state][0] + (size[0] * order[state][n])
                whereY = where[state][1]
                new = Crop(image, [whereX, whereY], size)
                x = dx + data[state][n][0] + (32 * n)
                y = dy - data[state][n][1]
                Paste(frame, new, (x, y))

            output[state][layer] = frame

    return output


def ProcessHead(name, image, where, head_data, source_data, is_alpha):
    """
    Processes a unit's head sprite.

    :param name:        Spritesheet's base name.
    :param image:       Source image to crop from.
    :param where:       X-Y offset to colored region on source spritesheet.
    :param head_data:   Head compositing data from file.
    :param source_data: Source referencing data from file.
    :param is_alpha:    Whether to replace black with transparency.

    :return: Dictionary mapping luminosities to image layers.
    """
    layers = Split(Crop(image, where, REGION_FULL_HEAD))
    if is_alpha:
        layers = {k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0])
                  for k, v in layers.items()}

    data = GetHeadOffsets(name, head_data)
    order = GetHeadOrder(name, head_data)
    type = data["size"]
    size = source_data["head"][type]["size"]
    where = source_data["head"][type]["where"]

    output = {}
    for state in STATES:
        dx = 8 if type == "small" else 0
        if state == "right":
            dy = +32 * 2
        elif state == "left":
            dy = +32 * 1
        else:
            dy = +32 * 0

        output[state] = {}
        for layer, image in layers.items():
            # Make blank image with room for 4 sprite frames
            shape = (COLOR_REGION[1], COLOR_REGION[0], 4)
            frame = np.zeros(shape, np.uint8)

            for n in range(4):
                whereX = where[state][0] + (size[0] * order[state][n])
                whereY = where[state][1]
                new = Crop(image, [whereX, whereY], size)
                x = dx + data[state][n][0] + (32 * n)
                y = dy - data[state][n][1]
                Paste(frame, new, (x, y))

            output[state][layer] = frame

    return output


def Process(head_path,
            body_path,
            head_offset,
            body_offset,
            head_data,
            body_data,
            source_data,
            is_alpha):
    """
    Assembles sprite data for both head and body images.

    :param head_path:    Head spritesheet's filename.
    :param body_path:    Body spritesheet's filename.
    :param head_offset:  X-Y offset onto head spritesheet.
    :param body_offset:  X-Y offset onto body spritesheet.
    :param head_data:    Head compositing data.
    :param body_data:    Body compositing data.
    :param source_data:  Source-referencing data.
    :param is_alpha:     Whether to make black pixels transparent.

    :return: Dictionary containing head and body compositing rules.
    """
    # Load head spritesheet from file
    if not head_path:
        headImage = np.zeros([256, 384, 3], dtype=np.uint8)
        headImage[:, :] = (0, 0, 0)
    else:
        headImage = cv2.imread(head_path)
        if headImage.size == 0:
            print(HEAD_SRC_NOT_FOUND.format(head_path))
            raise SystemExit

    # Load body spritesheet from file
    if not body_path:
        bodyImage = np.zeros([256, 384, 3], dtype=np.uint8)
        bodyImage[:, :] = (0, 0, 0)
    else:
        bodyImage = cv2.imread(body_path)
        if bodyImage.size == 0:
            print(BODY_SRC_NOT_FOUND.format(body_path))
            raise SystemExit

    baseName = os.path.splitext(os.path.basename(body_path))[0]
    return {
        "head": ProcessHead(baseName,
                            headImage,
                            head_offset,
                            head_data,
                            source_data,
                            is_alpha),
        "body": ProcessBody(baseName,
                            bodyImage,
                            body_offset,
                            body_data,
                            source_data,
                            is_alpha)
    }


def CompositeIdle(head,
                  body,
                  offset=(0, 0),
                  is_alpha=True,
                  headfirst=True,
                  reverse=False,
                  ):
    """
    Composites spritesheet (idle frames only).

    :param head:      Head name.
    :param body:      Body name.
    :param offset:    Manual X-Y offset onto master sheet. (Default (0, 0)).
    :param is_alpha:  Whether to make black pixels transparent. (Default True).
    :param headfirst: Whether to paste heads before bodies. (Default True).
    :param reverse:   Whether to invert layering order. (Default False).

    :return: Composited image.
    """
    # Load head compositing data from JSON
    headOffsets = LoadHeadOffsets()
    headPaths = LoadHeadPaths()
    if not head:
        headPath = ""
    else:
        headPath = os.path.join(ROOT_INPUT_DIR, *headPaths[head]["path"])
        if not os.path.isfile(headPath):
            raise NonexistentHeadException(headPath)

    # Load body compositing data from JSON
    bodyOffsets = LoadBodyOffsets()
    bodyPaths = LoadBodyPaths()
    if not body:
        bodyPath = ""
    else:
        bodyPath = os.path.join(ROOT_INPUT_DIR, *bodyPaths[body]["path"])
        if not os.path.isfile(bodyPath):
            raise NonexistentBodyException(bodyPath)

    # Load source processing rules from JSON
    srcColors = LoadSourceColoring()
    srcCrops = LoadSourceCropping()

    # Make master spritesheet
    outImage = MakeBlank(COLOR_REGION[0], STATE_REGION[1] * (len(COLORS) + 1))

    # Process each color
    for y, color in enumerate(COLORS):
        newImage = MakeBlank(*COLOR_REGION)
        newData = Process(
            headPath,
            bodyPath,
            [offset[0], offset[1] + HEAD_BLOCK * srcColors[color]],
            [offset[0], offset[1] + BODY_BLOCK * srcColors[color]],
            headOffsets,
            bodyOffsets,
            srcCrops,
            is_alpha,
            )

        # Composite idle frames
        PasteLayers(newImage,
                    newData["head"]["idle"],
                    newData["body"]["idle"],
                    SortedSet(
                        newData["head"]["idle"],
                        newData["body"]["idle"],
                        reverse=headOffsets.get(
                            body, {}).get("reverse", False)),
                    headfirst=headfirst,
                    reverse=reverse,
                    )

        # Paste onto master spritesheet
        Paste(outImage, newImage, (0, y * STATE_REGION[1]))

        # (Optional) Make grayscale based on purple sprite
        if color == "purple":
            newGray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
            newGray = cv2.cvtColor(newGray, cv2.COLOR_GRAY2BGR)

            if is_alpha:
                newGray = ConvertAlpha(newGray)
                newGray = ReplaceColor(newGray, [0, 0, 0, 255], [0, 0, 0, 0])

            Paste(outImage, newGray, (0, (y + 1) * STATE_REGION[1]))

    # Save image to file
    return outImage


def CompositeFull(head,
                  body,
                  offset=(0, 0),
                  is_alpha=True,
                  headfirst=True,
                  reverse=False,
                  ):
    """
    Composites spritesheet.

    :param head:      Head spritesheet name.
    :param body:      Body spritesheet name.
    :param offset:    Manual X-Y offset onto master sheet. (Default (0,0)).
    :param is_alpha:  Whether to make black pixels transparent. (Default True).
    :param headfirst: Whether to paste heads before bodies. (Default True).
    :param reverse:   Whether to invert layering order. (Default False).

    :return: Composited image.
    """
    # Load head compositing data from JSON
    headOffsets = LoadHeadOffsets()
    headPaths = LoadHeadPaths()
    if not head:
        headPath = ""
    else:
        headPath = os.path.join(ROOT_INPUT_DIR, *headPaths[head]["path"])
        if not os.path.isfile(headPath):
            raise NonexistentHeadException(headPath)

    # Load body compositing data from JSON
    bodyOffsets = LoadBodyOffsets()
    bodyPaths = LoadBodyPaths()
    if not body:
        bodyPath = ""
    else:
        bodyPath = os.path.join(ROOT_INPUT_DIR, *bodyPaths[body]["path"])
        if not os.path.isfile(bodyPath):
            raise NonexistentBodyException(bodyPath)

    # Load compositing rules from JSON
    srcColorData = LoadSourceColoring()
    srcCropData = LoadSourceCropping()

    # Make master spritesheet
    outImage = MakeBlank(COLOR_REGION[0], COLOR_REGION[1] * (len(COLORS) + 1))

    # Process frames for each color
    for y, color in enumerate(COLORS):
        newImage = MakeBlank(*COLOR_REGION)
        newData = Process(
            headPath,
            bodyPath,
            [offset[0], offset[1] + HEAD_BLOCK * srcColorData[color]],
            [offset[0], offset[1] + BODY_BLOCK * srcColorData[color]],
            headOffsets,
            bodyOffsets,
            srcCropData,
            is_alpha,
            )

        # Composite idle frames
        PasteLayers(newImage,
                    newData["head"]["idle"],
                    newData["body"]["idle"],
                    SortedSet(
                        newData["head"]["idle"],
                        newData["body"]["idle"],
                        reverse=headOffsets.get(
                            body, {}).get("reverse", False)),
                    headfirst=headfirst,
                    reverse=reverse,
                    )

        # Composite left-moving frames
        PasteLayers(newImage,
                    newData["head"]["left"],
                    newData["body"]["left"],
                    SortedSet(newData["head"]["left"],
                              newData["body"]["left"]),
                    headfirst=headfirst,
                    reverse=reverse,
                    )

        # Composite right-moving frames
        PasteLayers(newImage,
                    newData["head"]["right"],
                    newData["body"]["right"],
                    SortedSet(newData["head"]["right"],
                              newData["body"]["right"]),
                    headfirst=headfirst,
                    reverse=reverse,
                    )

        # Paste onto master spritesheet
        Paste(outImage, newImage, (0, y * COLOR_REGION[1]))

        # (Optional) Make grayscale based on purple sprite
        if color == "purple":
            newGray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
            newGray = cv2.cvtColor(newGray, cv2.COLOR_GRAY2BGR)

            if is_alpha:
                newGray = ConvertAlpha(newGray)
                newGray = ReplaceColor(newGray, [0, 0, 0, 255], [0, 0, 0, 0])

            Paste(outImage, newGray, (0, (y + 1) * COLOR_REGION[1]))

    # Save image to file
    return outImage


def SaveImage(image, path):
    """
    Saves a CV2-format image to file.

    :param image: CV2 image to save.
    :param path:  Relative path to save to.

    :return: None.
    """
    cv2.imwrite(path, image)
