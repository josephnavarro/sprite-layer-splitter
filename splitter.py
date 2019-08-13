#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool

Intended for Fire Emblem Fates and Fire Emblem Echoes sprites. Map sprites in
Fire Emblem Fates and Echoes store head and body sprites separately, and store
layer information using grayscale masks. This program puts them together.

(Currently only composites the idle frames).

"""
import sys
from constant import *
from imaging import *
from paths import *


def split(image, alpha=True) -> dict:
    """
    Splits an image using grayscale layering data.
    """
    h, w, color = image.shape
    color = crop(image, (0x0, 0x0), (w >> 1, h))  # Fully-colored sprite
    mask = crop(image, (w >> 1, 0), (w >> 1, h))  # Grayscale masking data

    # Sort irregular subregions by grayscale value
    out = {}
    for layer in [_ for _ in get_colors(grayscale(mask)) if _ not in IGNORE]:
        new = apply_mask(color, make_mask(mask, layer))
        if alpha:
            new = convert_alpha(new)
        out[layer] = new

    return out


def process_body(base: str, src, region, alpha: bool) -> dict:
    """

    :param base:    Spritesheet base name
    :param src:     Source image to crop from
    :param region:  X-Y offset to colored region on source spritesheet
    :param alpha:   Whether to replace black with transparency

    :return:
    """
    replace_color(src)

    # Get framewise X-Y offsets (if any)
    idle_offset: list = BASE_OFFSET_ARRAY[:]
    left_offset: list = BASE_OFFSET_ARRAY[:]
    right_offset: list = BASE_OFFSET_ARRAY[:]

    try:
        body_params = BODY_PARAMS[base]
        try:
            idle_offset = body_params["offset"]["idle"][:]
        except KeyError:
            pass
        try:
            left_offset = body_params["offset"]["left"][:]
        except KeyError:
            pass
        try:
            right_offset = body_params["offset"]["right"][:]
        except KeyError:
            pass
    except KeyError:
        pass

    idle_offset = idle_offset[1:4] + [idle_offset[0]]
    left_offset = left_offset[1:4] + [left_offset[0]]
    right_offset = right_offset[1:4] + [right_offset[0]]

    # Crop out two-sided color region on source image, then extract layers
    x, y = 0, 0  # CROP["body"]["start"]
    dims = CROP["body"]["sub"]
    w, h = COLOR_REGION_SIZE
    img = crop(src, (x + region[0], y + region[1]), CROP["body"]["size"])
    layers: dict = split(img, alpha)
    out: dict = {}

    # (Optional) Replace black pixels with transparent ones
    if alpha:
        for layer in layers:
            replace_color(layers[layer], [0, 0, 0, 255], [0, 0, 0, 0])

    # Assemble idle, left, and right layers for body sprite
    for key in ["idle", "left", "right"]:
        out[key] = {}

        if key == "left":
            offset = left_offset
            y = dims[1] * 1
        elif key == "right":
            offset = right_offset
            y = dims[1] * 2
        else:
            offset = idle_offset
            y = 0

        for layer in layers:
            new = np.zeros((h, w, 4), np.uint8)

            for n in range(4):
                img = crop(layers[layer], (n * dims[0], y), dims)
                pos = (n * dims[0] + offset[n][0], y - offset[n][1])
                paste(img, new, pos)

            out[key][layer] = new

    return out


def process_head(base: str, src, region, alpha: bool) -> dict:
    """
    Processes a unit's head sprite.

    :param base:    Spritesheet base name
    :param src:     Source image to crop from
    :param region:  X-Y offset to colored region on source spritesheet
    :param alpha:   Whether to replace black with transparency

    :return:
    """
    replace_color(src)

    idle_offset: list = BASE_OFFSET_ARRAY[:]
    left_offset: list = BASE_OFFSET_ARRAY[:]
    right_offset: list = BASE_OFFSET_ARRAY[:]
    size: str = "large"

    try:
        head_params = HEAD_PARAMS[base]
        try:
            size = head_params["size"]
        except KeyError:
            pass
        try:
            idle_offset = head_params["offset"]["idle"][:]
        except KeyError:
            pass
        try:
            left_offset = head_params["offset"]["left"][:]
        except KeyError:
            pass
        try:
            right_offset = head_params["offset"]["right"][:]
        except KeyError:
            pass
    except KeyError:
        pass

    # Crop out two-sided color region on source image, then extract layers
    x, y = 0, 0  # CROP["head"][size]["start"]
    dims = CROP["head"][size]["sub"]
    w, h = COLOR_REGION_SIZE
    img = crop(src, (x + region[0], y + region[1]), (256, 192))
    layers: dict = split(img, alpha)
    out: dict = {}

    # (Optional) Replace black pixels with transparent ones
    if alpha:
        for layer in layers:
            replace_color(layers[layer], [0, 0, 0, 255], [0, 0, 0, 0])

    # Assemble idle, left, and right layers for body sprite
    for key in ["idle", "left", "right"]:
        out[key] = {}
        y = CROP["head"][size]["start"][key][1]

        if key == "left":
            offset = left_offset
            dy = 32
        elif key == "right":
            offset = right_offset
            dy = 64
        else:
            offset = idle_offset
            dy = 0

        if size == "large":
            for layer in layers:
                new = np.zeros((h, w, 4), np.uint8)

                for n in range(4):
                    img = crop(layers[layer], (n * dims[0], y), dims)
                    pos = (offset[n][0] + n * dims[0], dy - offset[n][1])
                    paste(img, new, pos)

                out[key][layer] = new

        elif size == "small":
            for layer in layers:
                new = np.zeros((h, w, 4), np.uint8)

                for n in range(4):
                    img = crop(layers[layer], (n * dims[0], y), dims)
                    pos = (offset[n][0] + n * 32 - 24, dy - offset[n][1])
                    paste(img, new, pos)

                out[key][layer] = new

    return out


def process(head_path: str, body_path: str, head_offset: tuple, body_offset: tuple, alpha: bool) -> dict:
    """
    Assembles sprite data for both head and body images.
    """
    # Load head image from file
    try:
        head_im = cv2.imread(os.path.join(HEAD_DIR, head_path))
    except:
        print("Error! Head source {} not found! Aborting...".format(head_path))
        raise SystemExit

    # Load body image from file
    try:
        body_im = cv2.imread(os.path.join(BODY_DIR, body_path))
    except:
        print("Error! Body source {} not found! Aborting...".format(body_path))
        raise SystemExit

    body_base, ext = os.path.splitext(os.path.basename(body_path))

    return {
        "head": process_head(body_base, head_im, head_offset, alpha),
        "body": process_body(body_base, body_im, body_offset, alpha),
        }


def main_idle(head: str, body: str, name, offset=(0, 0), alpha=True, outdir=OUTDIR):
    """
    Image processor entrypoint. Only assembles idle frames.

    :param head:
    :param body:
    :param name:
    :param offset:
    :param alpha:
    :param outdir:
    """
    w = COLOR_REGION_SIZE[0]
    h = STATE_REGION_SIZE[1] * (len(COLORS) + 1)
    y = 0
    out = make_blank(w, h)

    # Check whether specified character class (body sprite) exists
    base = os.path.splitext(os.path.basename(body))[0]
    if base not in HEAD_PARAMS:
        print("Error! Undefined character class! Continuing with defaults...")

    # Generate 1 sprite block per color region
    for color in COLORS:
        # Offset to specific color
        head_offset: tuple = (offset[0], offset[1] + HEAD_BLOCK * COLOR_OFFSETS[color])
        body_offset: tuple = (offset[0], offset[1] + BODY_BLOCK * COLOR_OFFSETS[color])

        # Process head and body
        data: dict = process(head, body, head_offset, body_offset, alpha)
        head_data: dict = data["head"]
        body_data: dict = data["body"]

        new = make_blank(*COLOR_REGION_SIZE)
        idle_layers: list = sorted(list(set(list(head_data["idle"].keys()) + list(body_data["idle"].keys()))))

        try:
            if HEAD_PARAMS[body]["reverse"]:
                idle_layers = idle_layers[::-1]
        except KeyError:
            pass

        # Composite head and body (idle)
        for layer in idle_layers:
            try:
                paste(head_data["idle"][layer], new, (0, 0))
            except KeyError:
                pass

            try:
                paste(body_data["idle"][layer], new, (0, 0))
            except KeyError:
                pass

        paste(new, out, (0, y * STATE_REGION_SIZE[1]))

        # Generate grayscale image based on purple sprite
        y += 1
        if color == "purple":
            grey = new.copy()
            grey = cv2.cvtColor(grey, cv2.COLOR_BGR2GRAY)
            grey = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
            grey = convert_alpha(grey)
            replace_color(grey, [0, 0, 0, 255], [0, 0, 0, 0])
            paste(grey, out, (0, y * STATE_REGION_SIZE[1]))

    path = fix_paths(os.path.join(outdir, name))
    cv2.imwrite(path + '/sheet.png', out)


def main(head: str, body: str, name, offset=(0, 0), alpha=True, outdir=OUTDIR):
    """
    Image processor entrypoint.

    :param head:
    :param body:
    :param name:
    :param offset:
    :param alpha:
    :param outdir:
    """
    w = COLOR_REGION_SIZE[0]
    h = COLOR_REGION_SIZE[1] * (len(COLORS) + 1)
    y = 0
    out = make_blank(w, h)

    # Check whether specified character class (body sprite) exists
    base = os.path.splitext(os.path.basename(body))[0]
    if base not in HEAD_PARAMS:
        print("Error! Undefined character class! Continuing with defaults...")

    # Generate 1 sprite block per color region
    for color in COLORS:
        # Offset to specific color
        head_offset: tuple = (offset[0], offset[1] + HEAD_BLOCK * COLOR_OFFSETS[color])
        body_offset: tuple = (offset[0], offset[1] + BODY_BLOCK * COLOR_OFFSETS[color])

        # Process head and body
        data: dict = process(head, body, head_offset, body_offset, alpha)
        head_data: dict = data["head"]
        body_data: dict = data["body"]

        new = make_blank(*COLOR_REGION_SIZE)
        idle_layers: list = sorted(list(set(list(head_data["idle"].keys()) + list(body_data["idle"].keys()))))
        left_layers: list = sorted(list(set(list(head_data["left"].keys()) + list(body_data["left"].keys()))))
        right_layers: list = sorted(list(set(list(head_data["right"].keys()) + list(body_data["right"].keys()))))

        try:
            if HEAD_PARAMS[body]["reverse"]:
                idle_layers = idle_layers[::-1]
        except KeyError:
            pass

        # Composite head and body (idle)
        for layer in idle_layers:
            try:
                paste(head_data["idle"][layer], new, (0, 0))
            except KeyError:
                pass

            try:
                paste(body_data["idle"][layer], new, (0, 0))
            except KeyError:
                pass

        # Composite head and body (left)
        for layer in left_layers:
            try:
                paste(head_data["left"][layer], new, (0, 0))
            except KeyError:
                pass

            try:
                paste(body_data["left"][layer], new, (0, 0))
            except KeyError:
                pass

        # Composite head and body (right)
        for layer in right_layers:
            try:
                paste(head_data["right"][layer], new, (0, 0))
            except KeyError:
                pass

            try:
                paste(body_data["right"][layer], new, (0, 0))
            except KeyError:
                pass

        paste(new, out, (0, y * COLOR_REGION_SIZE[1]))

        # Generate grayscale image based on purple sprite
        y += 1
        if color == "purple":
            grey = new.copy()
            grey = cv2.cvtColor(grey, cv2.COLOR_BGR2GRAY)
            grey = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)
            grey = convert_alpha(grey)
            replace_color(grey, [0, 0, 0, 255], [0, 0, 0, 0])
            paste(grey, out, (0, y * COLOR_REGION_SIZE[1]))

    path = fix_paths(os.path.join(outdir, name))
    cv2.imwrite(path + '/sheet.png', out)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
