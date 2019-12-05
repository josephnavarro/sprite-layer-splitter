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


def sorted_set(*lists, reverse=False):
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


def paste_layers(dest,
                 head,
                 body,
                 layers,
                 *,
                 headfirst=True,
                 reverse=False,
                 ):
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


def split(image):
    """
    Isolates irregular regions on an image, then sorts by luminosity.

    :param image: Image to extract regions from.

    :return: Dictionary mapping luminosity to sprite layers.
    """
    h, w, channels = image.shape
    base = Crop(image, [0, 0], [w >> 1, h])

    # Mask is right half of image
    mask = ReplaceColor(
        Crop(
            image,
            [w >> 1, 0],
            [w >> 1, h],
        ),
        # Replace white with off-white so it doesn't get erased
        [255, 255, 255],
        [252, 252, 252],
    )

    # Isolate regions and sort into layers
    return {
        p: ConvertAlpha(ApplyMask(base, MakeMask(mask, p)))
        for p in [
            q for q in GetUniqueColors(ToGrayscale(mask))
            if q not in IGNORED_COLORS
        ]}


def get_body_offsets(name, data):
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


def get_body_order(name, data):
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


def get_head_offsets(name, data):
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


def get_head_order(name, data):
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


def process_body(name, image, where, body_data, source_data, is_alpha):
    """
    Processes a unit's body sprite.

    :param name:        Source spritesheet's base name.
    :param image:       Source image to crop from.
    :param where:       X-Y offset to colored region on source spritesheet.
    :param body_data:   Body compositing data from file.
    :param source_data: Source referencing data from file.
    :param is_alpha:    Whether to replace black with transparency.

    :return: Dictionary mapping luminosities to image layers.
    """
    layers = split(Crop(image, where, REGION_FULL_BODY))
    if is_alpha:
        layers = {
            k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0])
            for k, v in layers.items()
        }

    data = get_body_offsets(name, body_data)
    order = get_body_order(name, body_data)
    size = source_data["body"]["size"]
    where = source_data["body"]["where"]

    output = {}
    for state in STATES:
        dx = +0

        # Vertical order: Idle -> Left -> Right
        if state == "right":
            dy = +32 * 2
        elif state == "left":
            dy = +32 * 1
        else:
            dy = +32 * 0

        output[state] = {}
        for layer, image in layers.items():
            # Make blank image 4 frames wide
            shape = (COLOR_REGION[1], COLOR_REGION[0], 4)
            frame = np.zeros(shape, np.uint8)

            for n in range(4):
                at_x = where[state][0] + (size[0] * order[state][n])
                at_y = where[state][1]
                new = Crop(image, [at_x, at_y], size)
                x = dx + data[state][n][0] + (32 * n)
                y = dy - data[state][n][1]
                Paste(frame, new, (x, y))

            output[state][layer] = frame

    return output


def process_head(name, image, where, head_data, source_data, is_alpha):
    """
    Processes a unit's head sprite.

    :param name:        Source spritesheet's base name.
    :param image:       Source image to crop from.
    :param where:       X-Y offset to colored region on source spritesheet.
    :param head_data:   Head compositing data from file.
    :param source_data: Source referencing data from file.
    :param is_alpha:    Whether to replace black with transparency.

    :return: Dictionary mapping luminosities to image layers.
    """
    layers = split(Crop(image, where, REGION_FULL_HEAD))
    if is_alpha:
        layers = {
            k: ReplaceColor(v, [0, 0, 0, 255], [0, 0, 0, 0])
            for k, v in layers.items()
        }

    data = get_head_offsets(name, head_data)
    order = get_head_order(name, head_data)
    type = data["size"]
    size = source_data["head"][type]["size"]
    where = source_data["head"][type]["where"]

    output = {}
    for state in STATES:
        # "Small" heads have to be centered
        if type == "small":
            dx = +8
        else:
            dx = +0

        # Vertical order: Idle -> Left -> Right
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
                at_x = where[state][0] + (size[0] * order[state][n])
                at_y = where[state][1]
                new = Crop(image, [at_x, at_y], size)
                x = dx + data[state][n][0] + (32 * n)
                y = dy - data[state][n][1]
                Paste(frame, new, (x, y))

            output[state][layer] = frame

    return output


def process(head_path,
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
    if not head_path:
        # Create blank for head
        head_image = np.zeros([256, 384, 3], dtype=np.uint8)
        head_image[:, :] = (0, 0, 0)
    else:
        # Load head spritesheet from file
        head_image = cv2.imread(head_path)
        if head_image.size == 0:
            print(HEAD_SRC_NOT_FOUND.format(head_path))
            raise SystemExit

    if not body_path:
        # Create blank for body
        body_image = np.zeros([256, 384, 3], dtype=np.uint8)
        body_image[:, :] = (0, 0, 0)
    else:
        # Load body spritesheet from file
        body_image = cv2.imread(body_path)
        if body_image.size == 0:
            print(BODY_SRC_NOT_FOUND.format(body_path))
            raise SystemExit

    base_name = os.path.splitext(os.path.basename(body_path))[0]
    return {
        "head": process_head(
            base_name,
            head_image,
            head_offset,
            head_data,
            source_data,
            is_alpha,
        ),
        "body": process_body(
            base_name,
            body_image,
            body_offset,
            body_data,
            source_data,
            is_alpha,
        )
    }


def composite(profile,
              head,
              body,
              offset=(0, 0),
              *,
              color=(0, 0, 0, 0),
              is_alpha=True,
              headfirst=True,
              reverse=False,
              idle_only=False,
              ):
    """
    Composites spritesheet.

    :param profile:   Profile key.
    :param head:      Head spritesheet name.
    :param body:      Body spritesheet name.
    :param offset:    Manual X-Y offset onto master sheet. (Default (0,0)).
    :param is_alpha:  Whether to make black pixels transparent. (Default True).
    :param headfirst: Whether to paste heads before bodies. (Default True).
    :param reverse:   Whether to invert layering order. (Default False).
    :param idle_only: Whether to only composite idle frames. (Default False).

    :return: Composited image.
    """
    # Load head composition data from JSON
    head_offsets = load_offsets("head", profile)
    head_paths = load_paths("head")
    if not head:
        head_path = ""
    else:
        head_path = os.path.join(
            DIRECTORIES["input"]["root"],
            *head_paths[head]["path"]
        )
        if not os.path.isfile(head_path):
            raise NonexistentHeadException(head_path)

    # Load body composition data from JSON
    body_offsets = load_offsets("body", profile)
    body_paths = load_paths("body")
    if not body:
        body_path = ""
    else:
        body_path = os.path.join(
            DIRECTORIES["input"]["root"],
            *body_paths[body]["path"]
        )
        if not os.path.isfile(body_path):
            raise NonexistentBodyException(body_path)

    # Load miscellaneous composition rules from JSON
    src_color_data = load_source_coloring()
    src_crop_data = load_source_cropping()

    # Make master spritesheet
    if idle_only:
        w, h = COLOR_REGION[0], STATE_REGION[1] * (len(COLORS) + 1)
    else:
        w, h = COLOR_REGION[0], COLOR_REGION[1] * (len(COLORS) + 1)

    out_image = MakeBlank(w, h, color=color)

    # Process each color
    for y, color in enumerate(COLORS):
        new_image = MakeBlank(*COLOR_REGION)
        new_data = process(
            head_path,
            body_path,
            [offset[0], offset[1] + HEAD_BLOCK * src_color_data[color]],
            [offset[0], offset[1] + BODY_BLOCK * src_color_data[color]],
            head_offsets,
            body_offsets,
            src_crop_data,
            is_alpha,
        )

        # Compose idle frames
        paste_layers(
            new_image,
            new_data["head"]["idle"],
            new_data["body"]["idle"],
            sorted_set(
                new_data["head"]["idle"],
                new_data["body"]["idle"],
                reverse=head_offsets.get(body, {}).get("reverse", False),
            ),
            headfirst=headfirst,
            reverse=reverse,
        )

        if idle_only:
            # Paste idle frames onto master spritesheet
            Paste(
                out_image,
                new_image,
                (0, y * STATE_REGION[1]),
            )
        else:
            # Compose left movement frames
            paste_layers(
                new_image,
                new_data["head"]["left"],
                new_data["body"]["left"],
                sorted_set(
                    new_data["head"]["left"],
                    new_data["body"]["left"],
                ),
                headfirst=headfirst,
                reverse=reverse,
            )

            # Compose right movement frames
            paste_layers(
                new_image,
                new_data["head"]["right"],
                new_data["body"]["right"],
                sorted_set(
                    new_data["head"]["right"],
                    new_data["body"]["right"],
                ),
                headfirst=headfirst,
                reverse=reverse,
            )

            # Paste onto master spritesheet
            Paste(
                out_image,
                new_image,
                (0, y * COLOR_REGION[1]),
            )

        # (Optional) Make grayscale based on purple sprite
        if color == "purple":
            new_gray = cv2.cvtColor(
                cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY),
                cv2.COLOR_GRAY2BGR,
            )

            if is_alpha:
                new_gray = ReplaceColor(
                    ConvertAlpha(new_gray),
                    [0, 0, 0, 255],
                    [0, 0, 0, 0],
                )

            if idle_only:
                Paste(out_image, new_gray, (0, (y + 1) * STATE_REGION[1]))
            else:
                Paste(out_image, new_gray, (0, (y + 1) * COLOR_REGION[1]))

    # Return newly composed image
    return out_image


def save_image(image, path):
    """
    Saves a CV2-format image to file.

    :param image: CV2 image to save.
    :param path:  Relative path to save to.

    :return: None.
    """
    cv2.imwrite(path, image)
