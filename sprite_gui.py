#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.

"""
import cv2
import psutil
import random
# import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

import sprite_imaging
import sprite_splitter
from gui import EasyGUI
from sprite_prepare import *
from sprite_utils import *


class EmptyFilenameException(Exception):
    """
    Exception thrown upon attempted spritesheet saving without a filename.
    """
    pass


class InvalidFilenameException(Exception):
    """
    Exception thrown upon providing an invalid file extension.
    """
    pass


class InvalidBodyException(sprite_splitter.NonexistentBodyException):
    """
    Exception thrown upon referencing an invalid body spritesheet.
    """

    def __init__(self, name):
        super().__init__(name)


class InvalidHeadException(sprite_splitter.NonexistentHeadException):
    """
    Exception thrown upon referencing an invalid head spritesheet.
    """

    def __init__(self, name):
        super().__init__(name)


class UnspecifiedBodyException(Exception):
    """
    Exception thrown upon attempted sprite composition with a body.
    """
    pass


class UnspecifiedHeadException(Exception):
    """
    Exception thrown when sprite composition is attempted while no head is
    selected.
    """
    pass


class App(EasyGUI):
    # Composition tag(s)
    DEFAULT_NAME = "None"
    DEFAULT_PROFILE = PROFILES.echoes, str()

    # Dimensions for sprite previews
    RECTS = {
        "idle":  [0, 0, 128, 32],
        "left":  [0, 32, 128, 32],
        "right": [0, 64, 128, 32],
    }

    # Constants for animation slider
    SPEED_SCALE_MIN = 0
    SPEED_SCALE_MAX = 12

    @property
    def colors(self) -> dict:
        return {
            "head":                 {"fg": [0, 0, 0], "bg": [200, 224, 255]},
            "body":                 {"fg": [0, 0, 0], "bg": [255, 200, 200]},
            "preview-static":       {"fg": [0, 0, 0], "bg": [128, 128, 128]},
            "preview-anim":         {"fg": [0, 0, 0], "bg": [128, 128, 128]},

            # Icon-based buttons
            "play-button":          {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "pause-button":         {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "skip-right-button":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "skip-left-button":     {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "shuffle-button":       {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "shuffle-head-button":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "shuffle-body-button":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "clear-body-button":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "clear-head-button":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "reload-button":        {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "preview-idle-button":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "preview-left-button":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "preview-right-button": {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "ping-pong-button":     {"fg": [0, 0, 0], "bg": [222, 222, 222]},
            "layers-button":        {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        }

    @property
    def event_lock_delay(self) -> int:
        return 333

    @property
    def grid(self) -> dict:
        return {
            # Frames
            "a-y1x0":               [1, 0],
            "a-y2x0":               [2, 0],
            "b-y0x3":               [0, 3],
            "b-y1x0":               [1, 0],
            "b-y1x1":               [1, 1],
            "c-y0x0a":              [4, 0],
            "c-y1x0a":              [5, 0],
            "c-y7x0":               [7, 0],
            "c-y0x0b":              [0, 0],
            "c-y0x1":               [0, 1],
            "d-y0x0":               [0, 0],
            "d-y1x0":               [1, 0],
            "pad-a-y1x0":           [1, 0],
            "pad-a-y2x0a":          [6, 0],
            "pad-a-y2x0b":          [24, 0],
            "pad-b-y0x3":           [0, 0],
            "pad-b-y1x0":           [2, 0],
            "pad-c-y1x0a":          [0, 1],
            "pad-d-y1x0":           [0, 0],
            "pad-master-y0x0":      [0, 0],

            # Preview canvases
            "preview-static":       [0, 1],
            "preview-anim":         [0, 2],
            "preview-frames-label": [1, 1],
            "preview-anim-label":   [1, 2],

            # Speed slider
            "speed-slider":         [0, 0],

            # Left column
            "head":                 [0, 0],
            "body":                 [1, 0],

            "offset-body":          [0, 0],
            "body-x-label":         [0, 2],
            "body-x":               [0, 3],
            "body-y-label":         [0, 4],
            "body-y":               [0, 5],
            "body-size":            [0, 6],

            "offset-head":          [0, 0],
            "head-x-label":         [0, 2],
            "head-x":               [0, 3],
            "head-y-label":         [0, 4],
            "head-y":               [0, 5],
            "head-size":            [0, 6],

            "speed-anim":           [6, 0],
            "frame-label":          [7, 0],
            "frame-0":              [7, 1],
            "frame-1":              [7, 2],
            "frame-2":              [7, 3],
            "frame-3":              [7, 4],

            # Right column
            "reload-button":        [0, 1],
            "play-button":          [0, 2],
            "pause-button":         [0, 3],
            "skip-left-button":     [0, 4],
            "skip-right-button":    [0, 5],
            "preview-idle-button":  [1, 1],
            "preview-left-button":  [1, 2],
            "preview-right-button": [1, 3],
            "ping-pong-button":     [1, 4],
            "layers-button":        [1, 5],
            "shuffle-button":       [2, 1],
            "shuffle-body-button":  [2, 2],
            "shuffle-head-button":  [2, 3],
            "clear-body-button":    [2, 4],
            "clear-head-button":    [2, 5],

            "prioritize-label":     [16, 1],
            "prioritize-1":         [17, 1],
            "prioritize-2":         [18, 1],
        }

    @property
    def images(self) -> dict:
        return {
            "play-button":          os.path.join("misc", "play.png"),
            "pause-button":         os.path.join("misc", "pause.png"),
            "skip-right-button":    os.path.join("misc", "forward.png"),
            "skip-left-button":     os.path.join("misc", "backward.png"),
            "shuffle-button":       os.path.join("misc", "shuffle.png"),
            "shuffle-body-button":  os.path.join("misc", "shuffle-body.png"),
            "shuffle-head-button":  os.path.join("misc", "shuffle-head.png"),
            "clear-body-button":    os.path.join("misc", "clear-body.png"),
            "clear-head-button":    os.path.join("misc", "clear-head.png"),
            "reload-button":        os.path.join("misc", "reload.png"),
            "preview-idle-button":  os.path.join("misc", "idle.png"),
            "preview-left-button":  os.path.join("misc", "left.png"),
            "preview-right-button": os.path.join("misc", "right.png"),
            "ping-pong-button":     os.path.join("misc", "ping-pong.png"),
            "layers-button":        os.path.join("misc", "layers.png"),
        }

    @property
    def labels(self) -> dict:
        return {
            # Menus
            "head-menu":            "Head",
            "body-menu":            "Body",
            "export-menu":          "Export",
            "profile-menu":         "Profile",

            # Profiles
            "menu-radio-echoes":    "Echoes",
            "menu-radio-fates":     "Fates",

            # Canvas captions
            "preview-frames-label": "Static frame preview",
            "preview-anim-label":   "Animated preview",

            # Export options
            "export-full":          "Export all frames",
            "export-idle":          "Export idle frames",

            # Body options
            "body":                 "Select body",
            "rebuild-body-images":  "Remake body sources",
            "rebuild-body-data":    "Refresh body listing",
            "rebuild-body-offsets": "Refresh body offsets",
            "destroy-body-images":  "Clean body sources",

            # Head options
            "head":                 "Select head",
            "rebuild-head-images":  "Remake head sources",
            "rebuild-head-data":    "Refresh head listing",
            "rebuild-head-offsets": "Refresh head offsets",
            "destroy-head-images":  "Clean head sources",

            # Frame data readout
            "offset-body":          "Body:",
            "offset-head":          "Head:",
            "body-x-label":         "X",
            "body-y-label":         "Y",
            "head-x-label":         "X",
            "head-y-label":         "Y",
            "speed-anim":           "Speed:  {0:d}",
            "frame-label":          "Frame:",
            "frame-0":              "0",
            "frame-1":              "1",
            "frame-2":              "2",
            "frame-3":              "3",

            # Layer collision resolution
            "prioritize-label":     "On layer collision",
            "prioritize-1":         "Paste head first",
            "prioritize-2":         "Paste body first",

            # Icon-based buttons
            "play-button":          "",
            "pause-button":         "",
            "skip-right-button":    "",
            "skip-left-button":     "",
            "shuffle-button":       "",
            "shuffle-body-button":  "",
            "shuffle-head-button":  "",
            "clear-body-button":    "",
            "clear-head-button":    "",
            "reload-button":        "",
            "preview-idle-button":  "",
            "preview-left-button":  "",
            "preview-right-button": "",
            "ping-pong-button":     "",
            "layers-button":        "",
        }

    @property
    def messages(self) -> dict:
        return {
            "confirm": {
                "rebuild": {
                    "data":   {
                        "body": "Refresh list of available bodies?",
                        "head": "Refresh list of available heads?",
                    },
                    "image":  {
                        "body": "Remake source images for body sprites?",
                        "head": "Remake source images for head sprites?",
                    },
                    "offset": {
                        "body": "Refresh body sprite offsets?",
                        "head": "Refresh head sprite offsets?",
                    },
                },
                "destroy": {
                    "head": "Delete source images for head sprites?",
                    "body": "Delete source images for body sprites?",
                }
            },
            "message": {
                "destroy": {
                    "head": "Completely deleted all head sources.",
                    "body": "Completely deleted all body sources.",
                },
                "failure": {
                    "body": "Error: Body not specified!",
                    "head": "Error: Head not specified!",
                    "type": "Error: Invalid image format specified!",
                },
                "invalid": {
                    "body": "Error: Body spritesheet {} does not exist!",
                    "head": "Error: Head spritesheet {} does not exist!",
                },
                "rebuild": {
                    "image":  {
                        "body": "Succssfully reconstructed "
                                "body source images.",
                        "head": "Successfully reconstructed "
                                "head source images.",
                    },
                    "data":   {
                        "body": "Reassembled list of available bodies.",
                        "head": "Reassembled list of available heads.",
                    },
                    "offset": {
                        "body": "Successfully reloaded "
                                "per-frame body offsets.",
                        "head": "Successfully reloaded "
                                "per-frame head offsets.",
                    },
                },
                "success": {
                    "full": "Sprite frames saved to {}!",
                    "idle": "Idle frames saved to {}!",
                }
            }
        }

    @property
    def pad(self) -> dict:
        return {
            # Frames
            "a-y1x0":               [0, 0],
            "a-y2x0":               [0, 0],
            "b-y0x3":               [0, 0],
            "b-y1x0":               [0, 0],
            "b-y1x1":               [0, 0],
            "c-y0x0a":              [0, 0],
            "c-y1x0a":              [0, 0],
            "c-y7x0":               [0, 0],
            "c-y0x0b":              [0, 0],
            "c-y0x1":               [0, 0],
            "d-y0x0":               [0, 0],
            "d-y1x0":               [0, 0],
            "pad-a-y1x0":           [0, 0],
            "pad-a-y2x0a":          [0, 0],
            "pad-a-y2x0b":          [0, 0],
            "pad-b-y0x3":           [0, 0],
            "pad-b-y1x0":           [0, 0],
            "pad-d-y1x0":           [0, 0],
            "pad-master-y0x0":      [0, 0],

            # Preview canvases
            "preview-frames-label": [0, 0],
            "preview-anim-label":   [0, 0],
            "preview-static":       [0, 0],
            "preview-anim":         [0, 0],

            # Frame data readout
            "speed-anim":           [0, 0],
            "offset-head":          [0, 0],
            "offset-body":          [0, 0],
            "head-x-label":         [0, 0],
            "head-x":               [0, 0],
            "head-y-label":         [0, 0],
            "head-y":               [0, 0],
            "head-size":            [0, 0],
            "body-x-label":         [0, 0],
            "body-x":               [0, 0],
            "body-y-label":         [0, 0],
            "body-y":               [0, 0],
            "body-size":            [0, 0],
            "frame-label":          [0, 0],
            "frame-0":              [0, 0],
            "frame-1":              [0, 0],
            "frame-2":              [0, 0],
            "frame-3":              [0, 0],

            # Layer collision resolution
            "prioritize-label":     [4, 4],
            "prioritize-1":         [0, 0],
            "prioritize-2":         [0, 0],

            # Preview options
            "head":                 [4, 4],
            "body":                 [4, 4],

            # Icon-based buttons
            "play-button":          [0, 0],
            "pause-button":         [0, 0],
            "skip-left-button":     [0, 0],
            "skip-right-button":    [0, 0],
            "shuffle-button":       [0, 0],
            "shuffle-body-button":  [0, 0],
            "shuffle-head-button":  [0, 0],
            "clear-body-button":    [0, 0],
            "clear-head-button":    [0, 0],
            "reload-button":        [0, 0],
            "preview-idle-button":  [0, 0],
            "preview-left-button":  [0, 0],
            "preview-right-button": [0, 0],
            "ping-pong-button":     [0, 0],
            "layers-button":        [0, 0],
        }

    @property
    def sizes(self) -> dict:
        sizes = {
            # Frames
            "a-y1x0":               [0, 0],
            "a-y2x0":               [0, 0],
            "b-y0x3":               [0, 0],
            "b-y1x0":               [0, 0],
            "b-y1x1":               [0, 0],
            "c-y0x0a":              [0, 0],
            "c-y1x0a":              [0, 0],
            "c-y7x0":               [0, 0],
            "c-y0x0b":              [0, 0],
            "c-y0x1":               [0, 0],
            "d-y0x0":               [0, 0],
            "d-y1x0":               [0, 0],
            "pad-a-y1x0":           [0, 10],
            "pad-a-y2x0a":          [0, 10],
            "pad-a-y2x0b":          [0, 10],
            "pad-b-y0x3":           [1, 10],
            "pad-b-y1x0":           [0, 16],
            "pad-c-y1x0a":          [1 if self.is_osx() else 2, 16],
            "pad-d-y1x0":           [0, 16],
            "pad-master-y0x0":      [0, 10],

            # Preview canvases (pixels)
            "preview-anim":         [96, 96],
            "preview-resize":       [384, 96],
            "preview-static":       [384, 96],

            # Entry widgets (characters)
            "body-x":               [5, 1],
            "body-y":               [5, 1],
            "body-size":            [7, 1],
            "head-x":               [5, 1],
            "head-y":               [5, 1],
            "head-size":            [7, 1],

            # Icon-based buttons (pixels)
            "play-button":          [32, 32],
            "pause-button":         [32, 32],
            "skip-right-button":    [32, 32],
            "skip-left-button":     [32, 32],
            "shuffle-button":       [32, 32],
            "shuffle-body-button":  [32, 32],
            "shuffle-head-button":  [32, 32],
            "clear-body-button":    [32, 32],
            "clear-head-button":    [32, 32],
            "reload-button":        [32, 32],
            "preview-idle-button":  [32, 32],
            "preview-left-button":  [32, 32],
            "preview-right-button": [32, 32],
            "ping-pong-button":     [32, 32],
            "layers-button":        [32, 32],
        }
        if self.is_windows():
            # Windows
            sizes["default-button"] = [36, 0]
            sizes["default-menu"] = [37, 0]
            sizes["default-slider"] = [200, 0]
            sizes["FONTSIZE_MONOS"] = 10
            sizes["CANVAS_BORDERS"] = 13
            sizes["FONTSIZE_SMALL"] = 9
            sizes["FONTSIZE_VAR_W"] = 13
        else:
            # OS X / Linux
            sizes["default-button"] = [28, 0]
            sizes["default-menu"] = [25, 0]
            sizes["default-slider"] = [200, 0]
            sizes["FONTSIZE_MONOS"] = 14
            sizes["CANVAS_BORDERS"] = 13
            sizes["FONTSIZE_SMALL"] = 13
            sizes["FONTSIZE_VAR_W"] = 14

        return sizes

    @property
    def resize_x(self) -> bool:
        return False

    @property
    def resize_y(self) -> bool:
        return False

    @property
    def title(self) -> str:
        return "Fire Emblem 3DS Sprite Tool"

    @staticmethod
    def ms_from_min(minutes):
        """
        Converts minutes to milliseconds.

        :param minutes: Minutes to convert.

        :return: Number of milliseconds equivalent to given number of minutes.
        """
        return minutes * 60 * 1000

    def draw_text(self, canvas: tk.Canvas, x: int, y: int, text: str) -> None:
        """
        Draws text to a given canvas.

        :param canvas: Canvas to modify.
        :param x:      Topleft x-coordinate to draw at.
        :param y:      Topleft y-coordinate to draw at.
        :param text:   Text to render.

        :return: None.
        """
        font = "calibri {}".format(self.sizes["FONTSIZE_VAR_W"])
        canvas.create_text(
            x, y,
            font=font,
            fill="white",
            text=text,
            anchor=tk.NW,
        )

    def kill_itunes(self) -> None:
        """
        Kills any running iTunes instance. Checks periodically.

        :return: None.
        """
        found = False
        zombie = False

        for proc in psutil.process_iter():
            try:
                if proc.name() == "iTunes":
                    found = True
                    proc.kill()
            except psutil.ZombieProcess:
                zombie = True
                break

        if zombie:
            # Process was already killed; check again in 15 minutes
            print("iTunes has already been reaped.")
            timeout = App.ms_from_min(15)
        elif found:
            # iTunes was found; check again in 1 minute
            print("iTunes has been put in its place.")
            timeout = App.ms_from_min(1)
        else:
            # iTunes not found; check again in 10 minutes
            print("iTunes is inactive. Good!")
            timeout = App.ms_from_min(10)

        self.set_pending("kill-itunes", self.kill_itunes, timeout)

    def __init__(self, root, *args, **kwargs):
        """
        GUI layer over sprite composition tool.

        :param root:   Tkinter application instance.
        :param args:   Optional arguments to tk.Frame.
        :param kwargs: Keyword arguments to tk.Frame.
        """
        # Pre-initialization processing:

        # Initialize animation data
        self._Animation = {
            "image":   None,
            "init":    False,
            "forward": True,
            "playing": False,
            "objects": [],
            "frame":   0,
            "speed":   6,
            "state":   STATES.idle,
        }

        # Initialize per-frame data
        self._Data = {
            "profile": "",
            "body":    {
                "current": {},
                "data":    {},
                "list":    [self.DEFAULT_NAME],
                "offset":  {},
            },
            "head":    {
                "current": {},
                "data":    {},
                "list":    [self.DEFAULT_NAME],
                "offset":  {},
            },
        }

        # Sliders
        self._ScaleAnimationRate = tk.Scale()

        super().__init__(root, *args, **kwargs)

        # Post-initialization processing:

        # Kill iTunes and set icon image if on Mac
        if self.is_osx():
            image = tk.Image("photo", file="misc/icon.png")
            # noinspection PyProtectedMember
            root.tk.call("wm", "iconphoto", root._w, image)
            self.kill_itunes()

        # Repeat callback jobs
        self._PendingJobs["animate"] = None
        self._PendingJobs["kill-itunes"] = None

        # Complete widget initialization
        self.init_all_data()
        self.init_rate_slider()

    def clear_body(self) -> bool:
        """
        Clears body selection.

        :return: True.
        """
        self.get_string_var("body").set(App.DEFAULT_NAME)
        self.do_make_preview()

        return True

    def clear_head(self) -> bool:
        """
        Clears head selection.

        :return: True.
        """
        self.get_string_var("head").set(App.DEFAULT_NAME)
        self.do_make_preview()

        return True

    def destroy_images(self, key) -> bool:
        """
        Callback function. Destroys intermediate spritesheets.

        :param key: Either of "head" or "body".

        :return: True on success; False on failure.
        """
        title = self.title
        query = self.messages["confirm"]["destroy"][key]
        alert = self.messages["message"]["destroy"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushInputs(key)
            tk.messagebox.showinfo(title, alert)
            return True
        else:
            return False

    def do_animate(self, update=True) -> bool:
        """
        Local animation callback function.

        :return: True on success; False on failure.
        """
        if self._Animation["playing"]:
            if update:
                self.update_current_frame(1)
            else:
                self.update_current_frame(0)

            self.cancel_pending("animate")
            self.schedule_animate()

        self.update_offset_labels()
        self.update_animation_image()
        self.select_anim_radiobutton()

        return True

    def do_composite(self, callback, **kwargs) -> tuple:
        """
        Performs a general-purpose image composition routine.

        :param callback: Compositing function (CompositeIdle or CompositeFull)

        :return: Tuple of head key, body key, and numpy image.
        """
        head = ""
        body = ""
        image = None
        profile = self._Data["profile"]

        try:
            # Perform sprite composition
            head = self.get_key("head")
            body = self.get_key("body")
            image = callback(profile, head, body, **kwargs)

        except sprite_splitter.NonexistentHeadException as e:
            # Head spritesheet does not exist
            title = self.title
            alert: str = self.messages["message"]["invalid"]["head"]
            tk.messagebox.showinfo(title, alert.format(e.filename))

        except sprite_splitter.NonexistentBodyException as e:
            # Body spritesheet does not exist
            title = self.title
            alert: str = self.messages["message"]["invalid"]["body"]
            tk.messagebox.showinfo(title, alert.format(e.filename))

        except cv2.error:
            # CV2 image processing error
            raise InvalidFilenameException

        return head, body, image

    def do_export(self, callback, message, **kwargs) -> bool:
        """
        Composites and exports animation frames to file.

        :param callback: Frame compositing callback function.
        :param message:  Success message to display.

        :return: True on success; False on failure.
        """
        try:
            # Perform sprite composition
            head, body, image = self.do_composite(callback, **kwargs)

            if image is not None:
                if not head and not body:
                    head = "blank"
                    body = "sheet"
                elif not head:
                    head = "body"
                elif not body:
                    body = "head"

                # Prompt user for destination filename
                FixPath(ROOT_OUTPUT_DIR)
                path = filedialog.asksaveasfilename(
                    initialfile="{}_{}.png".format(head, body),
                    initialdir=ROOT_OUTPUT_DIR,
                    title="Save As",
                    filetypes=FILETYPES,
                )

                # Save image if path is valid
                if path:
                    sprite_splitter.SaveImage(image, path)
                    title = self.title
                    alert = message.format(os.path.basename(path))
                    tk.messagebox.showinfo(title, alert)

            return True

        except InvalidFilenameException:
            # Image format not recognized
            title = self.title
            alert = self.messages["message"]["failure"]["type"]
            tk.messagebox.showinfo(title, alert)
            return False

        except EmptyFilenameException:
            # Filename not specified
            return False

    def do_make_preview(self, *, state="") -> bool:
        """
        Creates an animated preview.

        :param state: State to preview. (Default empty).

        :return: True on success; False on failure.
        """
        self.turn_playback_off()

        callback = sprite_splitter.Composite
        state = state or str(self._Animation["state"])
        color = self.colors["preview-static"]["bg"]
        headfirst = self.get_string_var("prioritize").get() == "Head"
        reverse = self.get_boolean_var("reverse-layers").get()

        self.make_preview(
            callback,
            state,
            color=color,
            headfirst=headfirst,
            reverse=reverse,
        )

        return True

    def do_pause(self) -> bool:
        """
        Presses "pause" button, effectively.

        :return: True.
        """
        self.cancel_pending("animate")

        if self._Animation["objects"]:
            self._Animation["playing"] = False
            self.do_press_button("pause-button")
            self.do_unpress_button("play-button")

        return True

    def do_play(self) -> bool:
        """
        Presses "play" button, effectively.

        :return: True on success; False on failure.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = True
            self.do_press_button("play-button")
            self.do_unpress_button("pause-button")
            self.do_animate(False)

        return True

    def do_rebuild_data(self, key) -> bool:
        """
        Rebuilds head or body listings.

        :param key: Either of "head" or "body".

        :return: True.
        """
        CreateInputJSON(key, self._Data["profile"])
        self.init_data(key)
        self.init_option_menu(
            self.get_frame("b-y1x0"), key, self._Data[key]["list"],
        )

        return True

    def do_remake_offset(self, key) -> bool:
        """
        Rebuilds per-frame offsets.

        :param key: Either of "head" or "body".

        :return: True.
        """
        self._Data[key]["offset"] = LoadOffsets(key, self._Data["profile"])
        self.update_offset_labels()
        self.do_make_preview()

        return True

    def do_skip_frame(self, skip) -> bool:
        """
        Skips a specific number of animation frames.

        :param skip: Number (and direction) of frames to skip.

        :return: True.
        """
        frame = self._Animation["frame"] + skip
        if frame < 0:
            frame = 3
        elif frame >= 4:
            frame = 0

        self._Animation["frame"] = frame
        self.select_anim_radiobutton()

        return True

    def draw_frame_labels(self) -> bool:
        """
        Draw frame labels to animation preview canvas.
        TODO: Currently unused!

        :return: True on success; False on failure.
        """
        draw_text = self.draw_text
        canvas = self._Canvases["preview-static"]
        for n in range(4):
            draw_text(canvas, 18 + 96 * n, 92, "({})".format(n))

        return True

    def export_frames(self, *, idle_only=False) -> bool:
        """
        Composites and exports all frames to file.

        :param idle_only: Whether to export only idle frames. (Default False).

        :return: True on success; False on failure.
        """
        if idle_only:
            message = self.messages["message"]["success"]["idle"]
        else:
            message = self.messages["message"]["success"]["full"]

        callback = sprite_splitter.Composite
        reverse = self.get_boolean_var("reverse-layers").get()
        headfirst = self.get_string_var("prioritize").get() == "Head"

        self.do_export(
            callback,
            message,
            headfirst=headfirst,
            reverse=reverse,
            idle_only=idle_only,
        )

        return True

    def frame_skip(self, skip) -> bool:
        """
        Skips any number of frames forward or backward.

        Implements wrapping at bounds.

        :param skip: Number (and direction) of frames to skip.

        :return: True.
        """
        if self._Animation["objects"]:
            self.do_pause()
            self.do_skip_frame(skip)
            self.update_offset_labels()
            self.update_animation_image()

        return True

    def get_key(self, key) -> str:
        """
        Gets a dict key associated with a named body or head.

        :param key: Either of "body" or "head".

        :return: Name's associated dictionary key.
        """
        name = self.get_string_var(key).get()
        if name != self.DEFAULT_NAME:
            return self._Data[key].get("data", {}).get(name, "")
        else:
            return ""

    def init_all_buttons(self) -> bool:
        """
        Initializes all required buttons.

        :return: True.
        """
        init_button = self.init_button
        thread_it = self.thread_it
        get_frame = self.get_frame

        # Initialize "play animation" button
        init_button(
            get_frame("d-y0x0"),
            "play-button",
            thread_it(self.turn_playback_on),
        )

        # Initialize "pause animation" button
        init_button(
            get_frame("d-y0x0"),
            "pause-button",
            thread_it(self.turn_playback_off),
            pressed=True,
        )

        # Initialize "skip frame right" button
        init_button(
            get_frame("d-y0x0"),
            "skip-right-button",
            thread_it(lambda: self.frame_skip(1)),
        )

        # Initialize "skip frame left" button
        init_button(
            get_frame("d-y0x0"),
            "skip-left-button",
            thread_it(lambda: self.frame_skip(-1)),
        )

        # Initialize "shuffle" button
        init_button(
            get_frame("d-y0x0"),
            "shuffle-button",
            thread_it(lambda: self.shuffle_all() and self.jump_frame(0)),
        )

        # Initialize "shuffle body" button
        init_button(
            get_frame("d-y0x0"),
            "shuffle-body-button",
            thread_it(lambda: self.shuffle_body() and self.jump_frame(0)),
        )

        # Initialize "shuffle head" button
        init_button(
            get_frame("d-y0x0"),
            "shuffle-head-button",
            thread_it(lambda: self.shuffle_head() and self.jump_frame(0)),
        )

        # Initialize "clear body" button
        init_button(
            get_frame("d-y0x0"),
            "clear-body-button",
            thread_it(lambda: self.clear_body() and self.jump_frame(0)),
        )

        # Initialize "clear head" button
        init_button(
            get_frame("d-y0x0"),
            "clear-head-button",
            thread_it(lambda: self.clear_head() and self.jump_frame(0)),
        )

        # Initialize "reload" button
        init_button(
            get_frame("d-y0x0"),
            "reload-button",
            thread_it(
                lambda: self.do_remake_offset("head")
                        and self.do_remake_offset("body")
                        and self.jump_frame(0)
            ),

        )

        # Initialize "idle preview" button
        init_button(
            get_frame("d-y0x0"),
            "preview-idle-button",
            thread_it(
                lambda: self.do_make_preview(state="idle")
                        and self.do_press_button("preview-idle-button")
                        and self.do_unpress_button("preview-left-button")
                        and self.do_unpress_button("preview-right-button")
                        and self.jump_frame(0)
            ),
            pressed=True,
        )

        # Initialize "left preview" button
        init_button(
            get_frame("d-y0x0"),
            "preview-left-button",
            thread_it(
                lambda: self.do_make_preview(state="left")
                        and self.do_press_button("preview-left-button")
                        and self.do_unpress_button("preview-idle-button")
                        and self.do_unpress_button("preview-right-button")
                        and self.jump_frame(0)
            ),
        )

        # Initialize "right preview" button
        init_button(
            get_frame("d-y0x0"),
            "preview-right-button",
            thread_it(
                lambda: self.do_make_preview(state="right")
                        and self.do_press_button("preview-right-button")
                        and self.do_unpress_button("preview-left-button")
                        and self.do_unpress_button("preview-idle-button")
                        and self.jump_frame(0)
            ),
        )

        # Initialize "ping-pong" button
        init_button(
            get_frame("d-y0x0"),
            "ping-pong-button",
            thread_it(self.toggle_pingpong),
        )

        # Initialize "reverse layers" button
        init_button(
            self.get_frame("d-y0x0"),
            "layers-button",
            thread_it(self.toggle_reverse_layers),
        )

        return True

    def init_all_canvases(self) -> bool:
        """
        Initializes all required canvases.

        :return: True on success; False on failure.
        """
        # Initialize "static preview" canvas
        self.init_canvas(
            self.get_frame("a-y1x0"),
            "preview-static",
            self.sizes["CANVAS_BORDERS"],
        )

        # Initialize "animated preview" canvas
        self.init_canvas(
            self.get_frame("a-y1x0"),
            "preview-anim",
            self.sizes["CANVAS_BORDERS"],
        )

        self.draw_text(
            self.get_canvas("preview-static"), 24, 24,
            "Please select a profile."
        )

        return True

    def init_all_checkboxes(self) -> bool:
        """
        Initializes all required checkboxes.

        :return: True on success; False on failure.
        """
        assert self

        return True

    def init_all_data(self) -> bool:
        """
        Initializes all required data.

        :return: True on success; False on failure.
        """
        self.init_data("head", empty=True)
        self.init_data("body", empty=True)
        return True

    def init_all_entries(self) -> bool:
        """
        Initializes all required entry widgets.

        :return: True
        """
        # Initialize "body x-coordinate" entry
        self.init_entry(
            self.get_frame("c-y1x0a"),
            "body-x",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )

        # Initialize "body y-coordinate" entry
        self.init_entry(
            self.get_frame("c-y1x0a"),
            "body-y",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )

        # Initialize "head x-coordinate" entry
        self.init_entry(
            self.get_frame("c-y0x0a"),
            "head-x",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )

        # Initialize "head y-coordinate" entry
        self.init_entry(
            self.get_frame("c-y0x0a"),
            "head-y",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )

        # Initialize "head size" entry
        self.init_entry(
            self.get_frame("c-y0x0a"),
            "head-size",
            tk.W,
            text="Large",
            justify=tk.CENTER,
        )

        # Initialize "body size" entry (unused)
        self.init_entry(
            self.get_frame("c-y1x0a"),
            "body-size",
            tk.W,
            text="",
            justify=tk.CENTER,
        )

        return True

    def init_all_frames(self) -> bool:
        """
        Initializes all required frames.

        :return: True.
        """
        # Main frames
        self.init_frame(self._Master, "a-y1x0")
        self.init_frame(self._Master, "a-y2x0")

        # Container frames
        self.init_frame(self.get_frame("a-y1x0"), "b-y0x3")
        self.init_frame(self.get_frame("a-y2x0"), "b-y1x0")
        self.init_frame(self.get_frame("a-y2x0"), "b-y1x1")
        self.init_frame(self.get_frame("b-y1x0"), "c-y0x0a")
        self.init_frame(self.get_frame("b-y1x0"), "c-y1x0a")
        self.init_frame(self.get_frame("b-y1x0"), "c-y7x0")
        self.init_frame(self.get_frame("b-y1x1"), "c-y0x0b")
        self.init_frame(self.get_frame("b-y1x1"), "c-y0x1")
        self.init_frame(self.get_frame("c-y0x1"), "d-y0x0")
        self.init_frame(self.get_frame("c-y0x1"), "d-y1x0")

        # Padding frames
        self.init_frame(self.get_frame("a-y1x0"), "pad-a-y1x0")
        self.init_frame(self.get_frame("a-y2x0"), "pad-a-y2x0a")
        self.init_frame(self.get_frame("a-y2x0"), "pad-a-y2x0b")
        self.init_frame(self.get_frame("b-y0x3"), "pad-b-y0x3")
        self.init_frame(self.get_frame("b-y1x0"), "pad-b-y1x0")
        self.init_frame(self.get_frame("c-y1x0a"), "pad-c-y1x0a")
        self.init_frame(self.get_frame("d-y1x0"), "pad-d-y1x0")
        self.init_frame(self._Master, "pad-master-y0x0")

        return True

    def init_all_labels(self) -> bool:
        """
        Initializes all required labels.

        :return: True on success; False on failure.
        """
        # Initialize "animation speed" label
        self.init_label(
            self.get_frame("b-y1x0"),
            "speed-anim",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W, 0,
        )

        # Initialize "current frame" label
        self.init_label(
            self.get_frame("b-y1x0"),
            "frame-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.SW,
        )

        # Initialize "static frames preview" label
        self.init_label(
            self.get_frame("a-y1x0"),
            "preview-frames-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
        )

        # Initialize "animated preview" label
        self.init_label(
            self._Frames["a-y1x0"],
            "preview-anim-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
        )

        # Initialize "head offset" label
        self.init_label(
            self._Frames["c-y0x0a"],
            "offset-head",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W, 0, 0,
        )

        # Initialize "body offset" label
        self.init_label(
            self._Frames["c-y1x0a"],
            "offset-body",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
            0, 0,
        )

        # Initialize "body x-coordinate" label
        self.init_label(
            self._Frames["c-y1x0a"],
            "body-x-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
        )
        # Initialize "body y-coordinate" label
        self.init_label(
            self._Frames["c-y1x0a"],
            "body-y-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
        )
        # Initialize "head x-coordinate" label
        self.init_label(
            self._Frames["c-y0x0a"],
            "head-x-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
        )
        # Initialize "head y-coordinate" label
        self.init_label(
            self._Frames["c-y0x0a"],
            "head-y-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.W,
        )

        # Initialize "prioritize" label
        self.init_label(
            self._Frames["d-y1x0"],
            "prioritize-label",
            ("calibri", self.sizes["FONTSIZE_SMALL"]),
            tk.NS,
        )

        return True

    def init_all_menus(self) -> bool:
        """
        Initializes all required menus.

        :return: True.
        """
        # Initialize main menu bar
        self._Master.config(menu=self._Menus["main-menu"])

        thread_it = self.thread_it
        init_menu = self.init_menu
        labels = self.labels
        root_menu = self._Menus["main-menu"]

        # Initialize "profiles" menu
        init_menu(
            root_menu,
            "profile-menu",
            radio={
                "menu-radio-echoes": {
                    "value":    "echoes",
                    "variable": "profile-variable",
                    "command":  thread_it(lambda: self.set_profile("echoes")),
                },
                "menu-radio-fates":  {
                    "value":    "fates",
                    "variable": "profile-variable",
                    "command":  thread_it(lambda: self.set_profile("fates")),
                },

            }
        )

        # Initialize "head" menu
        init_menu(
            root_menu,
            "head-menu",
            {
                "label":   labels["rebuild-head-data"],
                "command": thread_it(lambda: self.rebuild_data("head")),
            },
            {
                "label":   labels["rebuild-head-images"],
                "command": thread_it(lambda: self.rebuild_images("head")),
            },
            {
                "label":   labels["rebuild-head-offsets"],
                "command": thread_it(lambda: self.rebuild_offsets("head")),
            },
            {
                "label":   labels["destroy-head-images"],
                "command": thread_it(lambda: self.destroy_images("head")),
            },
        )

        # Initialize "body" menu
        init_menu(
            root_menu,
            "body-menu",
            {
                "label":   labels["rebuild-body-data"],
                "command": thread_it(lambda: self.rebuild_data("body")),
            },
            {
                "label":   labels["rebuild-body-images"],
                "command": thread_it(lambda: self.rebuild_images("body")),
            },
            {
                "label":   labels["rebuild-body-offsets"],
                "command": thread_it(lambda: self.rebuild_offsets("body")),
            },
            {
                "label":   labels["destroy-body-images"],
                "command": thread_it(lambda: self.destroy_images("body")),
            },
        )

        # Initialize "export" menu
        init_menu(
            root_menu,
            "export-menu",
            {
                "label":   labels["export-idle"],
                "command": thread_it(
                    lambda: self.export_frames(idle_only=True)),
            },
            {
                "label":   labels["export-full"],
                "command": thread_it(self.export_frames),
            },
        )

        return True

    def init_all_optionmenus(self) -> bool:
        """
        Initializes all required option menus.

        :return: True.
        """
        init_optionmenu = self.init_option_menu
        frames = self._Frames
        data = self._Data

        # Initialize "select head" dropdown menu
        init_optionmenu(frames["b-y1x0"], "head", data["head"]["list"])

        # Initialize "select body" dropdown menu
        init_optionmenu(frames["b-y1x0"], "body", data["body"]["list"])

        return True

    def init_all_radiobuttons(self) -> bool:
        """
        Initializes all required radio buttons.

        :return: True.
        """
        init_radio = self.init_radio
        get_string_var = self.get_string_var
        thread_it = self.thread_it
        frames = self._Frames

        # Initialize "prioritize head" radio button
        init_radio(
            frames["d-y1x0"],
            "prioritize-1",
            get_string_var("prioritize"),
            "Head",
            tk.W,
            select=True,
        )

        # Initialize "prioritize body" radio button
        init_radio(
            frames["d-y1x0"],
            "prioritize-2",
            get_string_var("prioritize"),
            "Body",
            tk.W,
        )

        # Initialize "frame #1" radio button
        init_radio(
            frames["c-y7x0"],
            "frame-0",
            get_string_var("frame"),
            "0",
            tk.W,
            select=True,
            command=thread_it(lambda: self.jump_frame(0)),
        )

        # Initialize "frame #2" radio button
        init_radio(
            self._Frames["c-y7x0"],
            "frame-1",
            get_string_var("frame"),
            "1",
            tk.W,
            command=thread_it(lambda: self.jump_frame(1)),
        )

        # Initialize "frame #3" radio button
        init_radio(
            frames["c-y7x0"],
            "frame-2",
            get_string_var("frame"),
            "2",
            tk.W,
            command=thread_it(lambda: self.jump_frame(2)),
        )

        # Initialize "frame #4" radio button
        init_radio(
            frames["c-y7x0"],
            "frame-3",
            get_string_var("frame"),
            "3",
            tk.W,
            command=thread_it(lambda: self.jump_frame(3)),
        )

        return True

    def init_data(self, key, *, empty=False) -> bool:
        """
        Completes initialization of data from file.

        :param key:   Either of "head" or "body".
        :param empty: Whether to keep field empty. (Default False).

        :return: True.
        """
        paths = LoadPaths(key)
        data = self._Data
        offsets = LoadOffsets(key, data["profile"])

        names = data[key]["data"] = {
            v.get("name", "---"): k for k, v in paths.items()
        }

        data[key]["list"] = [self.DEFAULT_NAME]
        if not empty:
            data[key]["list"] += sorted(list(names))

        data[key]["offset"] = offsets

        return True

    def init_rate_slider(self) -> bool:
        """
        Completes initialization of framerate slider.

        :return: True.
        """
        scale = tk.Scale(
            self._Frames["c-y0x0b"],
            from_=self.SPEED_SCALE_MAX,
            to=self.SPEED_SCALE_MIN,
            orient=tk.VERTICAL,
            length=self.sizes["default-slider"][0],
            showvalue=0,
            command=self.update_speed,
        )

        scale.set(self._Animation["speed"])

        scale.grid(
            row=self.grid["speed-slider"][0],
            column=self.grid["speed-slider"][1],
            sticky=tk.W,
            padx=16,
            pady=4,
        )

        self._ScaleAnimationRate.destroy()
        self._ScaleAnimationRate = scale

        return True

    def jump_frame(self, frame) -> bool:
        """
        Jumps to a specific animation frame.

        :param frame: Frame to jump to.

        :return: True.
        """
        self._Animation["playing"] = False
        self._Animation["frame"] = frame

        self.do_press_button("pause-button")
        self.do_unpress_button("play-button")

        self.update_animation_image()
        self.update_offset_labels()
        self.select_anim_radiobutton()

        return True

    def make_animation_frames(self, image, reset) -> bool:
        """
        Populates local animation buffer.

        :param image: Spritesheet to crop frames from.
        :param reset: Whether to reset animation counters.

        :return: True
        """
        animation = self._Animation

        # Get animation frames
        w, h = self.sizes["preview-anim"]
        animation["objects"] = [
            sprite_imaging.ToPILToTkinter(
                sprite_imaging.Crop(image, [w * n, 0], [w, h])
            ) for n in range(4)
        ]

        # Reset animation counters
        if reset:
            animation["frame"] = 0
            animation["forward"] = True
        animation["speed"] = self._ScaleAnimationRate.get()

        # Create animated preview
        self._Canvases["preview-anim"].create_image(
            (16, 16),
            anchor=tk.NW,
            image=animation["objects"][0],
        )

        # Update labels
        self.update_offset_labels()

        return True

    def make_animation_preview(self, image) -> bool:
        """
        Displays static preview frames.

        :param image: Image to display.

        :return: True.
        """
        # Paste image onto canvas
        image = sprite_imaging.ToTkinter(sprite_imaging.ToPIL(image))
        self._Animation["image"] = image
        self._Canvases["preview-static"].create_image(
            (16, 16),
            anchor=tk.NW,
            image=image,
        )

        # self.DrawFrameLabels()

        return True

    def make_preview(self, func, state, reset=False, **kwargs) -> bool:
        """
        Generates a static preview image.

        :param func:  Compositing callback function to use.
        :param state: Named state of preview to generate.
        :param reset: Whether to reset animation frame. (Default False).

        :return: True.
        """
        try:
            data = self._Data
            profile = data["profile"]

            # Perform sprite composition
            self._Animation["state"] = state
            data["head"]["offset"] = LoadOffsets("head", profile)

            head, body, image = self.do_composite(func, **kwargs)
            if image is not None:
                try:
                    # Crop idle frames from source spritesheet
                    image = cv2.resize(
                        cv2.cvtColor(
                            sprite_imaging.Crop(
                                image,
                                App.RECTS[state][0:2],
                                App.RECTS[state][2:4],
                            ),
                            cv2.COLOR_BGR2RGB,
                        ),
                        dsize=tuple(self.sizes["preview-resize"]),
                        interpolation=cv2.INTER_NEAREST,
                    )

                    # Set static and animated previews
                    self.make_animation_preview(image)
                    self.make_animation_frames(image, reset)

                    try:
                        # Populate per-frame head offset data
                        data["head"]["current"] = data["head"]["offset"][body]
                    except KeyError:
                        data["head"]["current"] = {}

                    try:
                        # Populate per-frame body offset data
                        data["body"]["current"] = data["body"]["offset"][body]
                    except KeyError:
                        data["body"]["current"] = {}

                    self.update_offset_labels()

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            title = self.title
            message = self.messages["message"]["failure"]["type"]
            tk.messagebox.showinfo(title, message)

        return True

    def rebuild_data(self, key) -> bool:
        """
        Callback function. Rebuilds a given JSON database.

        :param key: Either of "head" or "body".

        :return: True.
        """
        title = self.title
        query = self.messages["confirm"]["rebuild"]["data"][key]
        alert = self.messages["message"]["rebuild"]["data"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            self.do_rebuild_data(key)
            tk.messagebox.showinfo(title, alert)

        return True

    def rebuild_images(self, key) -> bool:
        """
        Callback function. Rebuilds intermediate body spritesheets.

        :param key: Either of "head" or "body".

        :return: True.
        """
        title = self.title
        query = self.messages["confirm"]["rebuild"]["image"][key]
        alert = self.messages["message"]["rebuild"]["image"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            Prepare(key, self._Data["profile"])
            tk.messagebox.showinfo(title, alert)

        return True

    def rebuild_offsets(self, key) -> bool:
        """
        Callback function. Rebuilds offset database.

        :param key: Either of "head" or "body".

        :return: True.
        """
        title = self.title
        query = self.messages["confirm"]["rebuild"]["offset"][key]
        alert = self.messages["message"]["rebuild"]["offset"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            self.do_remake_offset(key)
            tk.messagebox.showinfo(title, alert)

        return True

    def schedule_animate(self) -> bool:
        """
        Schedules an animation callback routine.

        :return: True.
        """
        speed = self._Animation["speed"]
        if speed > 0:
            self.set_pending("animate", self.do_animate, 1000 // speed)

        return True

    def select_anim_radiobutton(self) -> bool:
        """
        Selects the appropriate animation frame radio button.

        :return: True.
        """
        frame = self._Animation["frame"]
        for n in range(4):
            key = "frame-{}".format(n)
            self.toggle_radio(self._RadioButtons[key], n == frame)

        return True

    def set_profile(self, profile) -> bool:
        """
        hhh

        :param profile:

        :return: True
        """
        if profile != self._Data["profile"]:
            self._Data["profile"] = profile

            self.do_rebuild_data("head")
            self.do_rebuild_data("body")
            self.do_remake_offset("head")
            self.do_remake_offset("body")

            self.get_button("preview-idle-button").invoke()

        return True

    def shuffle_all(self) -> bool:
        """
        Shuffles currently-selected bodies and heads.

        :return: True.
        """
        self.shuffle_body()
        self.shuffle_head()
        self.do_make_preview()

        return True

    def shuffle_body(self) -> bool:
        """
        Shuffles body selection.

        :return: True.
        """
        self.get_string_var("body").set(
            random.choice(self._Data["body"]["list"])
        )
        self.do_make_preview()

        return True

    def shuffle_head(self) -> bool:
        """
        Shuffles head selection.

        :return: True.
        """
        self.get_string_var("head").set(
            random.choice(self._Data["head"]["list"])
        )
        self.do_make_preview()

        return True

    def toggle_pingpong(self) -> bool:
        """
        Turns animation ping-ponging on or off.

        :return: True
        """
        is_pingpong = self.get_boolean_var("pingpong-animation")

        if is_pingpong.get():
            self.do_unpress_button("ping-pong-button")
            is_pingpong.set(False)
        else:
            self.do_press_button("ping-pong-button")
            is_pingpong.set(True)

        return True

    def toggle_reverse_layers(self) -> bool:
        """
        Turns layer reversal on or off.

        :return: True
        """
        is_reverse_layers = self.get_boolean_var("reverse-layers")

        if is_reverse_layers.get():
            self.do_unpress_button("layers-button")
            is_reverse_layers.set(False)
        else:
            self.do_press_button("layers-button")
            is_reverse_layers.set(True)

        return True

    def turn_playback_on(self) -> bool:
        """
        Turns animation playback on.

        :return: True.
        """
        if not self._Animation["playing"]:
            self.do_make_preview()
            self.do_play()

        return True

    def turn_playback_off(self) -> bool:
        """
        Turns animation playing off.

        :return: True.
        """
        self.do_pause()
        return True

    def update_current_frame(self, increment) -> bool:
        """
        Increments current animation frame.

        :return: True.
        """
        animation = self._Animation

        # Check frame iteration type
        is_forwards = animation["forward"]
        is_pingpong = self.get_boolean_var("pingpong-animation").get()
        if not is_pingpong:
            is_forwards = True

        # Increment frame
        frame = animation["frame"]

        if animation["objects"]:
            if is_forwards:
                # Forwards iteration
                frame += increment
                if frame < 0:
                    if not is_pingpong:
                        frame = 3
                        is_forwards = True
                    else:
                        frame = 1
                        is_forwards = True

                elif frame >= 4:
                    if not is_pingpong:
                        frame = 0
                        is_forwards = True
                    else:
                        frame = 2
                        is_forwards = False

            else:
                # Backwards iteration
                frame -= increment
                if frame < 0:
                    if not is_pingpong:
                        frame = 3
                        is_forwards = True
                    else:
                        frame = 1
                        is_forwards = True

                elif frame >= 4:
                    if not is_pingpong:
                        frame = 0
                        is_forwards = True
                    else:
                        frame = 2
                        is_forwards = False

        # Update references to current frame
        animation["forward"] = is_forwards
        animation["frame"] = frame

        return True

    def update_offset_label(self, key, state, frame):
        """
        Updates labels for current frame's (x, y) offsets.

        :param key:   Either of "head" or "body".
        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: True.
        """
        strvarx = "{}-x".format(key)
        strvary = "{}-y".format(key)
        try:
            xy = self._Data[key]["current"]["offset"][state][frame]
            self.get_string_var(strvarx).set("{0:+d}".format(xy[0]))
            self.get_string_var(strvary).set("{0:+d}".format(xy[1]))

        except (KeyError, IndexError):
            self.get_string_var(strvarx).set("{0:+d}".format(0))
            self.get_string_var(strvary).set("{0:+d}".format(0))

        return True

    def update_size_label(self, key) -> bool:
        """
        Updates labels for current frame's size (e.g. "small" or "large").

        :param key: Either of "head" or "body".

        :return: True.
        """
        strvar = "{}-size".format(key)
        try:
            size = self._Data[key]["current"]["size"]
            self.get_string_var(strvar).set(size.capitalize())

        except (KeyError, IndexError):
            self.get_string_var(strvar).set("Large")

        return True

    def update_animation_image(self) -> bool:
        """
        Updates currently-previewed animation frame.

        :return: True.
        """
        try:
            # Draw frame to canvas
            anim_objects = self._Animation["objects"]
            anim_frame = self._Animation["frame"]
            anim_image = anim_objects[anim_frame]

            self._Canvases["preview-anim"].create_image(
                (16, 16),
                anchor=tk.NW,
                image=anim_image,
            )

        except IndexError:
            # Current frame is invalid
            pass

        return True

    def update_offset_labels(self) -> bool:
        """
        Updates per-frame (x,y) head and body offset labels.

        :return: True.
        """
        state = self._Animation["state"]
        frame = self._Animation["frame"]

        self.update_offset_label("head", state, frame)
        self.update_offset_label("body", state, frame)
        self.update_size_label("head")

        return True

    def update_speed(self, speed) -> bool:
        """
        Updates current animation speed.

        :param speed: New framerate.

        :return: True.
        """
        speed = int(speed)
        text = self.labels["speed-anim"].format(speed)

        self._Labels["speed-anim"].config(text=text)
        self._Animation["speed"] = speed

        # Play animation
        self.cancel_pending("animate")
        self.schedule_animate()

        return True


def GUIMain():
    """
    Entrypoint for GUI version of Sprite Compositing Tool.

    :return: None
    """
    root = tk.Tk()
    app = App(root)
    app.mainloop()


if __name__ == "__main__":
    GUIMain()
