#! usr/bin/env python3
"""
------------------------------------------------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Intended for Fire Emblem Fates and Fire Emblem Echoes sprites. Map sprites in
Fire Emblem Fates and Echoes store head and body sprites separately, and store
layer information using grayscale masks. This program puts them together.

------------------------------------------------------------------------------------------------------------------------
"""
import itertools
from sprite_json import *
from sprite_imaging import *
from sprite_utils import *


class NonexistentHeadException(Exception):
    __slots__ = [
        "filename",
        ]

    def __init__(self, name):
        super().__init__()
        self.filename = name


class NonexistentBodyException(Exception):
    __slots__ = [
        "filename",
        ]

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
    out_list = sorted(list(set(itertools.chain(*[list(x) for x in lists]))))
    if reverse:
        out_list.reverse()
    return out_list


def PasteLayers(dest: np.ndarray,
                head: dict,
                body: dict,
                layers: list) -> None:
    """
    Pastes head and body subregions in proper layering order. (In-place).

    :param dest:   Destination image to paste to.
    :param head:   Head compositing data.
    :param body:   Body compositing data.
    :param layers: List of layers to process.

    :return: None.
    """
    for layer in layers:
        try:
            Paste(dest, head[layer], (0, 0))
        except KeyError:
            pass
        try:
            Paste(dest, body[layer], (0, 0))
        except KeyError:
            pass


def Split(image: np.ndarray) -> dict:
    """
    Isolates irregular regions on an image, then sorts regions by their luminosities.

    :param image: Image to extract regions from.

    :return: Layers sorted by luminosity.
    """
    h, w, channels = image.shape

    # Generate `base` and `mask` images
    base = Crop(image, [0, 0], [w >> 1, h])
    mask = ReplaceColor(Crop(image, [w >> 1, 0], [w >> 1, h]), [255, 255, 255], [252, 252, 252])

    # Isolate regions and sort into layers
    out_data = {}
    values = [value for value in GetUniqueColors(ToGrayscale(mask)) if value not in IGNORED_COLORS]

    for v in values:
        out_data[v] = ConvertAlpha(ApplyMask(base, MakeMask(mask, v)))

    # Return ordered layers
    return out_data


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

    :return: ...
    """
    new_body_data: dict = GetBodyOffsets(name, body_data)
    body_size: list = source_data["body"]["size"]
    body_where: list = source_data["body"]["where"]

    layers: dict = Split(Crop(image, where, REGION_FULL_BODY))
    if is_alpha:
        layers = {k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0]) for k, v in layers.items()}

    out_data: dict = {}

    for state in STATES:
        dx: int = 0
        dy: int = 32 * (2 if state == "right" else (1 if state == "left" else 0))

        out_data[state] = {}
        for key, img in layers.items():
            new_frame: np.ndarray = np.zeros((COLOR_REGION[1], COLOR_REGION[0], 4), np.uint8)

            for n in range(len(COLORS)):
                off_x: int = new_body_data[state][n][0]
                off_y: int = new_body_data[state][n][1]

                where_x: int = body_where[state][0] + (body_size[0] * n)
                where_y: int = body_where[state][1]

                new_img: np.ndarray = Crop(img, [where_x, where_y], body_size)
                new_pos: tuple = (dx + off_x + (32 * n), dy - off_y)

                Paste(new_frame, new_img, new_pos)

            out_data[state][key] = new_frame

    return out_data


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

    :return:
    """
    new_head_data: dict = GetHeadOffsets(name, head_data)
    head_type: str = new_head_data["size"]
    head_size: list = source_data["head"][head_type]["size"]
    head_where: list = source_data["head"][head_type]["where"]

    layers: dict = Split(Crop(image, where, REGION_FULL_HEAD))
    if is_alpha:
        layers = {k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0]) for k, v in layers.items()}

    out_data: dict = {}

    for state in STATES:
        dx: int = -24 if head_type == "small" else 0
        dy: int = +32 * (2 if state == "right" else (1 if state == "left" else 0))

        out_data[state] = {}
        for key, img in layers.items():
            new_frame: np.ndarray = np.zeros((COLOR_REGION[1], COLOR_REGION[0], 4), np.uint8)

            for n in range(len(COLORS)):
                off_x: int = new_head_data[state][n][0]
                off_y: int = new_head_data[state][n][1]

                where_x: int = head_where[state][0] + (head_size[0] * n)
                where_y: int = head_where[state][1]

                new_img: np.ndarray = Crop(img, [where_x, where_y], head_size)
                new_pos: tuple = (dx + off_x + (32 * n), dy - off_y)

                Paste(new_frame, new_img, new_pos)

            out_data[state][key] = new_frame

    return out_data


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
    head_image: np.ndarray = cv2.imread(head_path)
    if head_image.size == 0:
        print("Error! Head source image {} not found! Aborting...".format(head_path))
        raise SystemExit

    # Load body spritesheet from file
    body_image = cv2.imread(body_path)
    if body_image.size == 0:
        print("Error! Body source image {} not found! Aborting...".format(body_path))
        raise SystemExit

    base_name = os.path.splitext(os.path.basename(body_path))[0]
    return {
        "head": ProcessHead(base_name, head_image, head_offset, head_data, source_data, is_alpha),
        "body": ProcessBody(base_name, body_image, body_offset, body_data, source_data, is_alpha),
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
    offset_head_data = GetOffsetHeadData()
    offset_body_data = GetOffsetBodyData()

    # Load filepaths from JSON
    path_chara_data = GetHeadPathData()
    path_class_data = GetBodyPathData()

    # Load compositing rules from JSON
    source_color_data = GetSourceColorData()
    source_crop_data = GetSourceCropData()

    # Make master spritesheet
    out_image = MakeBlank(COLOR_REGION[0], STATE_REGION[1] * (len(COLORS) + 1))

    # Assemble sprites for each color
    head_path = os.path.join(ROOT_INPUT_DIRECTORY, *path_chara_data[head]["path"])
    if not os.path.isfile(head_path):
        raise NonexistentHeadException(head_path)

    body_path = os.path.join(ROOT_INPUT_DIRECTORY, *path_class_data[body]["path"])
    if not os.path.isfile(body_path):
        raise NonexistentBodyException(body_path)

    for y, color in enumerate(COLORS):
        new_image = MakeBlank(*COLOR_REGION)
        new_data = Process(
            head_path,
            body_path,
            [offset[0], offset[1] + HEAD_BLOCK * source_color_data[color]],
            [offset[0], offset[1] + BODY_BLOCK * source_color_data[color]],
            offset_head_data,
            offset_body_data,
            source_crop_data,
            is_alpha
            )

        # Composite idle frames
        PasteLayers(
            new_image,
            new_data["head"]["idle"],
            new_data["body"]["idle"],
            SortedSet(
                new_data["head"]["idle"],
                new_data["body"]["idle"],
                reverse=offset_head_data.get(body, {}).get("reverse", False),
                )
            )

        # Paste onto master spritesheet
        Paste(out_image, new_image, (0, y * STATE_REGION[1]))

        # (Optional) Make grayscale based on purple
        if color == "purple":
            new_gray = cv2.cvtColor(cv2.cvtColor(new_image.copy(), cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
            if is_alpha:
                new_gray = ReplaceColor(ConvertAlpha(new_gray), [0, 0, 0, 255], [0, 0, 0, 0])
            Paste(out_image, new_gray, (0, (y + 1) * STATE_REGION[1]))

    # Save image to file
    return out_image


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
    offset_head_data: dict = GetOffsetHeadData()
    offset_body_data: dict = GetOffsetBodyData()

    # Load filepath data from JSON
    path_chara_data: dict = GetHeadPathData()
    path_class_data: dict = GetBodyPathData()

    # Load compositing rules from JSON
    source_color_data: dict = GetSourceColorData()
    source_crop_data: dict = GetSourceCropData()

    # Make master spritesheet
    out_image: np.ndarray = MakeBlank(COLOR_REGION[0], COLOR_REGION[1] * (len(COLORS) + 1))

    # Assemble sprites for each color
    head_path: str = os.path.join(ROOT_INPUT_DIRECTORY, *path_chara_data[head]["path"])
    if not os.path.isfile(head_path):
        raise NonexistentHeadException(head_path)

    body_path: str = os.path.join(ROOT_INPUT_DIRECTORY, *path_class_data[body]["path"])
    if not os.path.isfile(body_path):
        raise NonexistentBodyException(body_path)

    for y, color in enumerate(COLORS):
        new_image: np.ndarray = MakeBlank(*COLOR_REGION)
        new_data: dict = Process(
            head_path,
            body_path,
            [offset[0], offset[1] + HEAD_BLOCK * source_color_data[color]],
            [offset[0], offset[1] + BODY_BLOCK * source_color_data[color]],
            offset_head_data,
            offset_body_data,
            source_crop_data,
            is_alpha
            )

        # Composite idle frames
        PasteLayers(
            new_image,
            new_data["head"]["idle"],
            new_data["body"]["idle"],
            SortedSet(
                new_data["head"]["idle"],
                new_data["body"]["idle"],
                reverse=offset_head_data.get(body, {}).get("reverse", False),
                )
            )

        # Composite left-moving frames
        PasteLayers(
            new_image,
            new_data["head"]["left"],
            new_data["body"]["left"],
            SortedSet(new_data["head"]["left"], new_data["body"]["left"]),
            )

        # Composite right-moving frames
        PasteLayers(
            new_image,
            new_data["head"]["right"],
            new_data["body"]["right"],
            SortedSet(new_data["head"]["right"], new_data["body"]["right"]),
            )

        # Place onto master spritesheet
        Paste(out_image, new_image, (0, y * COLOR_REGION[1]))

        # (Optional) Make grayscale based on purple
        if color == "purple":
            new_gray = cv2.cvtColor(cv2.cvtColor(new_image.copy(), cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
            if is_alpha:
                new_gray = ReplaceColor(ConvertAlpha(new_gray), [0, 0, 0, 255], [0, 0, 0, 0])
            Paste(out_image, new_gray, (0, (y + 1) * COLOR_REGION[1]))

    # Save image to file
    return out_image


def SaveImage(image: np.ndarray, path: str) -> None:
    """
    Saves a CV2-format image to file.

    :param image: CV2 image to save.
    :param path:  Relative path to save to.

    :return: None.
    """
    cv2.imwrite(path, image)
