#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Intended for Fire Emblem Fates and Fire Emblem Echoes sprites. Map sprites in
Fire Emblem Fates and Echoes store head and body sprites separately, and store
layer information using grayscale masks. This program puts them together.

--------------------------------------------------------------------------------
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


def SortedSet(*lists,
              reverse: bool = False) -> list:
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


def PasteLayers(dest: np.ndarray,
                head: dict,
                body: dict,
                layers: list,
                headfirst: bool = True) -> None:
    """
    Pastes head and body subregions in proper layering order.
    (In-place).

    :param dest:      Destination image to paste to.
    :param head:      Head compositing data.
    :param body:      Body compositing data.
    :param layers:    List of layers to process.
    :param headfirst: Whether to paste head first.

    :return: None.
    """
    for layer in layers:
        if headfirst:
            # Paste head first, body second
            try:
                Paste(dest, head[layer], (0, 0))
            except KeyError:
                pass
            try:
                Paste(dest, body[layer], (0, 0))
            except KeyError:
                pass

        else:
            # Paste body first, head second
            try:
                Paste(dest, body[layer], (0, 0))
            except KeyError:
                pass
            try:
                Paste(dest, head[layer], (0, 0))
            except KeyError:
                pass


def Split(image: np.ndarray) -> dict:
    """
    Isolates irregular regions on an image, then sorts by luminosity.

    :param image: Image to extract regions from.

    :return: Dictionary mapping luminosity to sprite layers.
    """
    h, w, channels = image.shape

    # Generate `base` and `mask` images
    base: np.ndarray = Crop(image, [0, 0], [w >> 1, h])
    mask: np.ndarray = Crop(image, [w >> 1, 0], [w >> 1, h])
    mask: np.ndarray = ReplaceColor(mask, [255, 255, 255], [252, 252, 252])

    # Isolate regions and sort into layers
    outData: dict = {}
    values: list = [
        v for v in GetUniqueColors(ToGrayscale(mask))
        if v not in IGNORED_COLORS
    ]

    for v in values:
        outData[v] = ConvertAlpha(ApplyMask(base, MakeMask(mask, v)))

    # Return ordered layers
    return outData


def GetBodyOffsets(name: str,
                   data: dict) -> dict:
    """
    Retrieves framewise offset data for body sprites.

    :param name: Name of character or character class.
    :param data: Body offsetting data.

    :return: Idle, left-, and right-facing frame data.
    """
    offsets: dict = data.get(name, {}).get("offset", {})
    idle: list = offsets.get("idle", BASE_OFFSETS)[:]
    left: list = offsets.get("left", BASE_OFFSETS)[:]
    right: list = offsets.get("right", BASE_OFFSETS)[:]

    # Rearrange offsets
    idle = idle[1:4] + [idle[0]]
    left = left[1:4] + [left[0]]
    right = right[1:4] + [right[0]]

    return {"idle": idle, "left": left, "right": right}


def GetHeadOffsets(name: str,
                   data: dict) -> dict:
    """
    Retrieves framewise offset data for head sprites.

    :param name: Name of character or character class.
    :param data: Head offsetting data.

    :return: Idle, left-, and right-facing frame data.
    """
    size: str = data.get(name, {}).get("size", "large")
    offsets: dict = data.get(name, {}).get("offset", {})
    idle: list = offsets.get("idle", BASE_OFFSETS)[:]
    left: list = offsets.get("left", BASE_OFFSETS)[:]
    right: list = offsets.get("right", BASE_OFFSETS)[:]

    return {"idle": idle, "left": left, "right": right, "size": size}


def ProcessBody(name: str,
                image: np.ndarray,
                where: list,
                body_data: dict,
                source_data: dict,
                is_alpha: bool) -> dict:
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
    newBodyData: dict = GetBodyOffsets(name, body_data)
    bodySize: list = source_data["body"]["size"]
    bodyWhere: list = source_data["body"]["where"]

    layers: dict = Split(Crop(image, where, REGION_FULL_BODY))
    if is_alpha:
        layers = {
            k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0])
            for k, v in layers.items()
        }

    outData: dict = {}

    for s in STATES:
        dx: int = +0
        dy: int = +32 * (2 if s == "right" else (1 if s == "left" else 0))

        outData[s] = {}
        for k, image in layers.items():
            newFrame: np.ndarray = np.zeros(
                (COLOR_REGION[1], COLOR_REGION[0], 4),
                np.uint8
            )

            for n in range(len(COLORS)):
                offX: int = newBodyData[s][n][0]
                offY: int = newBodyData[s][n][1]

                whereX: int = bodyWhere[s][0] + (bodySize[0] * n)
                whereY: int = bodyWhere[s][1]

                newImage: np.ndarray = Crop(image, [whereX, whereY], bodySize)
                newPos: tuple = (dx + offX + (32 * n), dy - offY)

                Paste(newFrame, newImage, newPos)

            outData[s][k] = newFrame

    return outData


def ProcessHead(name: str,
                image: np.ndarray,
                where: list,
                head_data: dict,
                source_data: dict,
                is_alpha: bool) -> dict:
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
    newHeadData: dict = GetHeadOffsets(name, head_data)
    headType: str = newHeadData["size"]
    headSize: list = source_data["head"][headType]["size"]
    headWhere: list = source_data["head"][headType]["where"]

    layers: dict = Split(Crop(image, where, REGION_FULL_HEAD))
    if is_alpha:
        layers = {
            k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0])
            for k, v in layers.items()
        }

    outData: dict = {}

    for s in STATES:
        dx: int = -24 if headType == "small" else 0
        dy: int = +32 * (2 if s == "right" else (1 if s == "left" else 0))

        outData[s] = {}
        for k, image in layers.items():
            newFrame: np.ndarray = np.zeros(
                (COLOR_REGION[1], COLOR_REGION[0], 4),
                np.uint8,
            )

            for n in range(len(COLORS)):
                offX: int = newHeadData[s][n][0]
                offY: int = newHeadData[s][n][1]

                whereX: int = headWhere[s][0] + (headSize[0] * n)
                whereY: int = headWhere[s][1]

                newImage: np.ndarray = Crop(image, [whereX, whereY], headSize)
                newPos: tuple = (dx + offX + (32 * n), dy - offY)

                Paste(newFrame, newImage, newPos)

            outData[s][k] = newFrame

    return outData


def Process(head_path: str,
            body_path: str,
            head_offset: list,
            body_offset: list,
            head_data: dict,
            body_data: dict,
            source_data: dict,
            is_alpha: bool) -> dict:
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
    headImage: np.ndarray = cv2.imread(head_path)
    if headImage.size == 0:
        print(HEAD_SRC_NOT_FOUND.format(head_path))
        raise SystemExit

    # Load body spritesheet from file
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
                            is_alpha,
                            ),
        "body": ProcessBody(baseName,
                            bodyImage,
                            body_offset,
                            body_data,
                            source_data,
                            is_alpha,
                            ),
        }


def CompositeIdle(head: str,
                  body: str,
                  offset: tuple = (0, 0),
                  is_alpha: bool = True) -> np.ndarray:
    """
    Composites spritesheet (idle frames only).

    :param head:     Head name.
    :param body:     Body name.
    :param offset:   Manual X-Y offset onto master sheet. (Default (0, 0)).
    :param is_alpha: Whether to make black pixels transparent. (Default True).

    :return: Composited image.
    """
    # Load compositing data from JSON
    headOffsetData: dict = LoadHeadOffsets()
    bodyOffsetData: dict = LoadBodyOffsets()

    # Load filepaths from JSON
    headPathData: dict = LoadHeadPaths()
    bodyPathData: dict = LoadBodyPaths()

    # Load compositing rules from JSON
    srcColorData: dict = LoadSourceImgColors()
    srcCropData: dict = LoadSourceImgCropping()

    # Check path to head spritesheet
    headPath: str = os.path.join(ROOT_INPUT_DIR, *headPathData[head]["path"])
    if not os.path.isfile(headPath):
        raise NonexistentHeadException(headPath)

    # Check path to body spritesheet
    bodyPath: str = os.path.join(ROOT_INPUT_DIR, *bodyPathData[body]["path"])
    if not os.path.isfile(bodyPath):
        raise NonexistentBodyException(bodyPath)

    # Make master spritesheet
    outImage: np.ndarray = MakeBlank(
        COLOR_REGION[0],
        STATE_REGION[1] * (len(COLORS) + 1),
    )

    # Process each color
    for y, color in enumerate(COLORS):
        newImage: np.ndarray = MakeBlank(*COLOR_REGION)
        newData: dict = Process(
            headPath,
            bodyPath,
            [offset[0], offset[1] + HEAD_BLOCK * srcColorData[color]],
            [offset[0], offset[1] + BODY_BLOCK * srcColorData[color]],
            headOffsetData,
            bodyOffsetData,
            srcCropData,
            is_alpha,
            )

        # Composite idle frames
        PasteLayers(
            newImage,
            newData["head"]["idle"],
            newData["body"]["idle"],
            SortedSet(
                newData["head"]["idle"],
                newData["body"]["idle"],
                reverse=headOffsetData.get(body, {}).get("reverse", False),
                )
            )

        # Paste onto master spritesheet
        Paste(outImage, newImage, (0, y * STATE_REGION[1]))

        # (Optional) Make grayscale based on purple sprite
        if color == "purple":
            newGray: np.ndarray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
            newGray: np.ndarray = cv2.cvtColor(newGray, cv2.COLOR_GRAY2BGR)

            if is_alpha:
                newGray = ConvertAlpha(newGray)
                newGray = ReplaceColor(newGray, [0, 0, 0, 255], [0, 0, 0, 0])

            Paste(outImage, newGray, (0, (y + 1) * STATE_REGION[1]))

    # Save image to file
    return outImage


def CompositeFull(head: str,
                  body: str,
                  offset: tuple = (0, 0),
                  is_alpha: bool = True) -> np.ndarray:
    """
    Composites spritesheet.

    :param head:     Head spritesheet name.
    :param body:     Body spritesheet name.
    :param offset:   Manual X-Y offset onto master sheet. (Default (0,0)).
    :param is_alpha: Whether to make black pixels transparent. (Default False).

    :return: Composited image.
    """
    # Load compositing data from JSON files
    headOffsetData: dict = LoadHeadOffsets()
    bodyOffsetData: dict = LoadBodyOffsets()

    # Load filepath data from JSON
    headPathData: dict = LoadHeadPaths()
    bodyPathData: dict = LoadBodyPaths()

    # Load compositing rules from JSON
    srcColorData: dict = LoadSourceImgColors()
    srcCropData: dict = LoadSourceImgCropping()

    # Check path to head spritesheet
    headPath: str = os.path.join(ROOT_INPUT_DIR, *headPathData[head]["path"])
    if not os.path.isfile(headPath):
        raise NonexistentHeadException(headPath)

    # Check path to body spritesheet
    bodyPath: str = os.path.join(ROOT_INPUT_DIR, *bodyPathData[body]["path"])
    if not os.path.isfile(bodyPath):
        raise NonexistentBodyException(bodyPath)

    # Make master spritesheet
    outImage: np.ndarray = MakeBlank(
        COLOR_REGION[0],
        COLOR_REGION[1] * (len(COLORS) + 1),
    )

    # Process frames for each color
    for y, color in enumerate(COLORS):
        newImage: np.ndarray = MakeBlank(*COLOR_REGION)
        newData: dict = Process(
            headPath,
            bodyPath,
            [offset[0], offset[1] + HEAD_BLOCK * srcColorData[color]],
            [offset[0], offset[1] + BODY_BLOCK * srcColorData[color]],
            headOffsetData,
            bodyOffsetData,
            srcCropData,
            is_alpha,
            )

        # Composite idle frames
        PasteLayers(
            newImage,
            newData["head"]["idle"],
            newData["body"]["idle"],
            SortedSet(
                newData["head"]["idle"],
                newData["body"]["idle"],
                reverse=headOffsetData.get(body, {}).get("reverse", False),
                )
            )

        # Composite left-moving frames
        PasteLayers(
            newImage,
            newData["head"]["left"],
            newData["body"]["left"],
            SortedSet(newData["head"]["left"], newData["body"]["left"]),
            )

        # Composite right-moving frames
        PasteLayers(
            newImage,
            newData["head"]["right"],
            newData["body"]["right"],
            SortedSet(newData["head"]["right"], newData["body"]["right"]),
            )

        # Place onto master spritesheet
        Paste(outImage, newImage, (0, y * COLOR_REGION[1]))

        # (Optional) Make grayscale based on purple
        if color == "purple":
            newGray: np.ndarray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
            newGray: np.ndarray = cv2.cvtColor(newGray, cv2.COLOR_GRAY2BGR)

            if is_alpha:
                newGray = ConvertAlpha(newGray)
                newGray = ReplaceColor(newGray, [0, 0, 0, 255], [0, 0, 0, 0])

            Paste(outImage, newGray, (0, (y + 1) * COLOR_REGION[1]))

    # Save image to file
    return outImage


def SaveImage(image: np.ndarray,
              path: str) -> None:
    """
    Saves a CV2-format image to file.

    :param image: CV2 image to save.
    :param path:  Relative path to save to.

    :return: None.
    """
    cv2.imwrite(path, image)
