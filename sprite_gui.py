#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.

"""
import psutil
import random
import cv2
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

import sprite_imaging
import sprite_splitter
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


class App(tk.Frame):
    WINDOW_TITLE = "Fire Emblem 3DS Sprite Tool"

    # Compositing tags
    DEFAULT_NAME = "None"

    # Popup message text content
    MESSAGES = {
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
                    "body": "Succssfully reconstructed body source images.",
                    "head": "Successfully reconstructed head source images.",
                },
                "data":   {
                    "body": "Reassembled list of available bodies.",
                    "head": "Reassembled list of available heads.",
                },
                "offset": {
                    "body": "Successfully reloaded per-frame body offsets.",
                    "head": "Successfully reloaded per-frame head offsets.",
                },
            },
            "success": {
                "full": "Sprite frames saved to {}!",
                "idle": "Idle frames saved to {}!",
            }
        }
    }

    # Default widget dimensions
    SIZES = {
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
        "pad-d-y1x0":           [0, 16],
        "pad-master-y0x0":      [0, 10],

        # Preview canvases (pixels)
        "preview-anim":         [96, 96],
        "preview-resize":       [384, 96],
        "preview-static":       [384, 96],

        # Entry widgets (characters)
        "body-x":               [3, 1],
        "body-y":               [3, 1],
        "head-x":               [3, 1],
        "head-y":               [3, 1],

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

    if IsWindows():
        # Windows
        SIZES["default-button"] = [36, 0]
        SIZES["default-menu"] = [37, 0]
        SIZES["default-slider"] = [200, 0]

        FONTSIZE_VAR_W = 13
        FONTSIZE_MONOS = 10
        FONTSIZE_SMALL = 9
        CANVAS_BORDERS = 13

    else:
        # OS X / Linux
        SIZES["default-button"] = [28, 0]
        SIZES["default-menu"] = [25, 0]
        SIZES["default-slider"] = [200, 0]

        FONTSIZE_VAR_W = 14
        FONTSIZE_MONOS = 14
        FONTSIZE_SMALL = 13
        CANVAS_BORDERS = 13

    GRID = {
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
        "body-x-label":         [0, 1],
        "body-x":               [0, 2],
        "body-y-label":         [0, 3],
        "body-y":               [0, 4],

        "offset-head":          [0, 0],
        "head-x-label":         [0, 1],
        "head-x":               [0, 2],
        "head-y-label":         [0, 3],
        "head-y":               [0, 4],

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

    # Padding for widgets
    PAD = {
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
        "body-x-label":         [0, 0],
        "body-x":               [0, 0],
        "body-y-label":         [0, 0],
        "body-y":               [0, 0],
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

    # Preview composition dimensions
    RECTS = {
        "idle":  [0, 0, 128, 32],
        "left":  [0, 32, 128, 32],
        "right": [0, 64, 128, 32],
    }

    # Button and menu text labels
    LABELS = {
        # Menus
        "head-menu":            "Head",
        "body-menu":            "Body",
        "export-menu":          "Export",

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

    # Button icon images
    IMAGES = {
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

    # Widget colors (RGB, foreground + background)
    COLORS = {
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

    # Animation speed slider
    SPEED_SCALE_MIN = 0
    SPEED_SCALE_MAX = 12

    @staticmethod
    def MinutesToMilliseconds(minutes):
        """
        Converts minutes to milliseconds.

        :param minutes: Minutes to convert.

        :return: Number of milliseconds equivalent to given number of minutes.
        """
        return minutes * 60 * 1000

    @staticmethod
    def DrawText(canvas, x, y, text):
        """
        Draws text to a given canvas.

        :param canvas: Canvas to modify.
        :param x:      Topleft x-coordinate to draw at.
        :param y:      Topleft y-coordinate to draw at.
        :param text:   Text to render.

        :return: None.
        """
        font = "Courier {} bold".format(App.FONTSIZE_MONOS)
        for m in range(-2, 3):
            for n in range(-2, 3):
                canvas.create_text(
                    x + m,
                    y + n,
                    font=font,
                    fill="black",
                    text=text,
                    anchor=tk.NW,
                )

        canvas.create_text(
            x, y,
            font=font,
            fill="white",
            text=text,
            anchor=tk.NW,
        )

    def KillITunes(self):
        """
        Kills any iTunes instance. Checks periodically.

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
            timeout = App.MinutesToMilliseconds(15)
        elif found:
            # iTunes was found; check again in 1 minute
            print("iTunes has been put in its place.")
            timeout = App.MinutesToMilliseconds(1)
        else:
            # iTunes not found; check again in 10 minutes
            print("iTunes is inactive. Good!")
            timeout = App.MinutesToMilliseconds(10)

        self.SetPending("kill-itnes", self.KillITunes, timeout)

    @staticmethod
    def FromRGB(r, g, b):
        """
        Returns a Tkinter-friendly color code from an RGB color tuple.

        :param r: Red channel (0-255)
        :param g: Green channel (0-255)
        :param b: Blue channel (0-255)

        :return: Color string.
        """
        return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)

    def __init__(self, root, *args, **kwargs):
        """
        GUI layer over sprite composition tool.

        :param root:   Tkinter application instance.
        :param args:   Optional arguments to tk.Frame.
        :param kwargs: Keyword arguments to tk.Frame.
        """
        super().__init__(root, *args, **kwargs)

        # Maintain reference to root Frame
        self._Master = root
        self._Master.resizable(False, False)
        self.winfo_toplevel().title(App.WINDOW_TITLE)

        # Repeat callback jobs
        self._PendingJobs = {
            "event-lock":  None,
            "animate":     None,
            "kill-itunes": None,
        }

        self._EventLock = False

        # Set icon for Mac OS X (and kill iTunes)
        if IsOSX():
            image = tk.Image("photo", file="misc/icon.png")
            # noinspection PyProtectedMember
            root.tk.call("wm", "iconphoto", root._w, image)
            self.KillITunes()

        # Initialize local non-widget data
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

        # Initialize per-frame body and head data
        self._Data = {
            "body": {
                "current": {},
                "data":    {},
                "list":    [""],
                "offset":  {},
            },
            "head": {
                "current": {},
                "data":    {},
                "list":    [""],
                "offset":  {},
            },
        }

        # Menu bar
        self._Menus = {
            "main-menu":   tk.Menu(self._Master),
            "head-menu":   tk.Menu(),
            "body-menu":   tk.Menu(),
            "export-menu": tk.Menu(),
        }

        self._Master.config(menu=self._Menus["main-menu"])

        # Boolean variables
        self._BooleanVars = {
            "pingpong-animation": tk.BooleanVar(),
            "reverse-layers":     tk.BooleanVar(),
        }

        # String variables
        self._StringVars = {
            "head":       tk.StringVar(self._Master),
            "body":       tk.StringVar(self._Master),
            "head-x":     tk.StringVar(self._Master),
            "head-y":     tk.StringVar(self._Master),
            "body-x":     tk.StringVar(self._Master),
            "body-y":     tk.StringVar(self._Master),
            "state":      tk.StringVar(self._Master),
            "frame":      tk.StringVar(self._Master),
            "prioritize": tk.StringVar(self._Master),
        }

        # Buttons
        self._Buttons = {
            # Export buttons
            "export-idle":          tk.Button(),
            "export-full":          tk.Button(),

            # Previewing buttons
            "preview-idle":         tk.Button(),
            "preview-left":         tk.Button(),
            "preview-right":        tk.Button(),

            # Body-related buttons
            "rebuild-body-data":    tk.Button(),
            "rebuild-body-images":  tk.Button(),
            "rebuild-body-offsets": tk.Button(),
            "destroy-body-images":  tk.Button(),

            # Head-related buttons
            "rebuild-head-data":    tk.Button(),
            "rebuild-head-images":  tk.Button(),
            "rebuild-head-offsets": tk.Button(),
            "destroy-head-images":  tk.Button(),

            # Icon-based buttons
            "play-button":          tk.Button(),
            "pause-button":         tk.Button(),
            "skip-right-button":    tk.Button(),
            "skip-left-button":     tk.Button(),
            "shuffle-button":       tk.Button(),
            "shuffle-head-button":  tk.Button(),
            "shuffle-body-button":  tk.Button(),
            "clear-body-button":    tk.Button(),
            "clear-head-button":    tk.Button(),
            "reload-button":        tk.Button(),
            "preview-idle-button":  tk.Button(),
            "preview-left-button":  tk.Button(),
            "preview-right-button": tk.Button(),
            "ping-pong-button":     tk.Button(),
            "layers-button":        tk.Button(),
        }

        # Canvases
        self._Canvases = {
            "preview-static": tk.Canvas(self._Master),
            "preview-anim":   tk.Canvas(self._Master),
        }

        # Check buttons
        self._Checkboxes = {
            "pingpong-animation": tk.Checkbutton(),
            "reverse-layers":     tk.Checkbutton(),
        }

        # Entry widgets
        self._Entries = {
            "head-x": tk.Entry(),
            "head-y": tk.Entry(),
            "body-x": tk.Entry(),
            "body-y": tk.Entry(),
        }

        # Frames
        self._Frames = {
            "a-y1x0":          tk.Frame(),
            "a-y2x0":          tk.Frame(),
            "b-y0x3":          tk.Frame(),
            "b-y1x0":          tk.Frame(),
            "b-y1x1":          tk.Frame(),
            "c-y0x0a":         tk.Frame(),
            "c-y0x0b":         tk.Frame(),
            "c-y1x0a":         tk.Frame(),
            "c-y7x0":          tk.Frame(),
            "c-y0x1":          tk.Frame(),
            "d-y0x0":          tk.Frame(),
            "d-y1x0":          tk.Frame(),
            "pad-a-y1x0":      tk.Frame(),
            "pad-a-y2x0a":     tk.Frame(),
            "pad-a-y2x0b":     tk.Frame(),
            "pad-b-y0x3":      tk.Frame(),
            "pad-b-y1x0":      tk.Frame(),
            "pad-d-y1x0":      tk.Frame(),
            "pad-master-y0x0": tk.Frame(),
        }

        # Radio buttons
        self._RadioButtons = {
            "prioritize-1": tk.Radiobutton(),
            "prioritize-2": tk.Radiobutton(),
            "frame-0":      tk.Radiobutton(),
            "frame-1":      tk.Radiobutton(),
            "frame-2":      tk.Radiobutton(),
            "frame-3":      tk.Radiobutton(),
        }

        # Menus
        self._OptionMenus = {
            "head":  tk.OptionMenu(
                None,
                self._StringVars["head"],
                *self._Data["head"]["list"]
            ),
            "body":  tk.OptionMenu(
                None,
                self._StringVars["body"],
                *self._Data["body"]["list"]
            ),
            "state": tk.OptionMenu(
                None,
                self._StringVars["state"],
                *STATES
            )
        }

        # Labels
        self._Labels = {
            "body-options":         tk.Label(),
            "export-options":       tk.Label(),
            "frame-label":          tk.Label(),
            "head-options":         tk.Label(),
            "offset-head":          tk.Label(),
            "offset-body":          tk.Label(),
            "preview-anim-label":   tk.Label(),
            "preview-frames-label": tk.Label(),
            "preview-options":      tk.Label(),
            "prioritize-label":     tk.Label(),
            "speed-anim":           tk.Label(),
            "body-x-label":         tk.Label(),
            "body-y-label":         tk.Label(),
            "head-x-label":         tk.Label(),
            "head-y-label":         tk.Label(),
        }

        # Sliders
        self._ScaleAnimSpeed = tk.Scale()

        # Complete widget initialization
        self.InitAllFrames(

        )
        self.InitAllData()
        self.InitAllButtons()
        self.InitAllCanvases()
        self.InitAllCheckboxes()
        self.InitAllEntries()
        self.InitAllLabels()
        self.InitAllMenus()
        self.InitAllOptionMenus()
        self.InitAllRadioButtons()

        self.InitSliderFramerate()

    def AcquireEventLock(self):
        """
        Acquires the event lock.

        :return: True on success; False on failure.
        """
        if not self._EventLock:
            self._EventLock = True
            return True
        else:
            print("locked")
            return False

    def ReleaseEventLock(self):
        """
        Releases the event lock.

        :return: True on success; False on failure.
        """
        self.CancelPending("event-lock")
        self.SetPending("event-lock", self.DoReleaseEventLock, 333)

        return True

    def CancelPending(self, key):
        """
        Cancels a pending scheduled event.

        :param key: Key of event to cancel.

        :return: True
        """
        job = self._PendingJobs.get(key, None)
        if job is not None:
            self.after_cancel(job)

        return True

    def ClearBody(self):
        """
        Clears body selection.

        :return: True.
        """
        self._StringVars["body"].set(App.DEFAULT_NAME)
        self.DoMakePreview()

        return True

    def ClearHead(self):
        """
        Clears head selection.

        :return: True.
        """
        self._StringVars["head"].set(App.DEFAULT_NAME)
        self.DoMakePreview()

        return True

    # noinspection PyMethodMayBeStatic
    def DestroyImages(self, key):
        """
        Callback function. Destroys intermediate spritesheets.

        :param key: Either of "head" or "body".

        :return: True on success; False on failure.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["destroy"][key]
        alert = App.MESSAGES["message"]["destroy"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushInputs(key)
            tk.messagebox.showinfo(title, alert)
            return True
        else:
            return False

    def DoAnimate(self, update=True):
        """
        Local animation callback function.

        :return: True on success; False on failure.
        """
        if self._Animation["playing"]:
            if update:
                self.UpdateCurrentFrame(1)
            else:
                self.UpdateCurrentFrame(0)

            self.ScheduleAnimate()

        self.UpdateOffsetLabels()
        self.UpdateAnimationImage()
        self.SelectAnimRadioButton()

        return True

    def DoComposite(self, func, **kwargs):
        """
        Performs a general-purpose image composition routine.

        :param func: Compositing function (CompositeIdle or CompositeFull)

        :return: Tuple of head key, body key, and numpy image.
        """
        head = ""
        body = ""
        im = None

        try:
            # Perform sprite composition
            head = self.GetKey("head")
            body = self.GetKey("body")
            im = func(head, body, **kwargs)

        except sprite_splitter.NonexistentHeadException as e:
            # Head spritesheet does not exist
            title = App.WINDOW_TITLE
            alert: str = App.MESSAGES["message"]["invalid"]["head"]
            tk.messagebox.showinfo(title, alert.format(e.filename))

        except sprite_splitter.NonexistentBodyException as e:
            # Body spritesheet does not exist
            title = App.WINDOW_TITLE
            alert: str = App.MESSAGES["message"]["invalid"]["body"]
            tk.messagebox.showinfo(title, alert.format(e.filename))

        except cv2.error:
            # CV2 image processing error
            raise InvalidFilenameException

        return head, body, im

    def DoExport(self, callback, message, **kwargs):
        """
        Composites and exports animation frames to file.

        :param callback: Frame compositing callback function.
        :param message:  Success message to display.

        :return: True on success; False on failure.
        """
        try:
            # Perform sprite composition
            head, body, im = self.DoComposite(callback, **kwargs)

            if im is not None:
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
                    sprite_splitter.SaveImage(im, path)
                    title = App.WINDOW_TITLE
                    alert = message.format(os.path.basename(path))
                    tk.messagebox.showinfo(title, alert)

            return True

        except InvalidFilenameException:
            # Image format not recognized
            title = App.WINDOW_TITLE
            alert = App.MESSAGES["message"]["failure"]["type"]
            tk.messagebox.showinfo(title, alert)
            return False

        except EmptyFilenameException:
            # Filename not specified
            return False

    def DoMakePreview(self, *, state=""):
        """
        Creates an animated preview.

        :param state: State to preview. (Default empty).

        :return: True on success; False on failure.
        """
        self.TurnPlaybackOff()

        callback = sprite_splitter.Composite
        state = state or str(self._Animation["state"])
        color = App.COLORS["preview-static"]["bg"]
        headfirst = self._StringVars["prioritize"].get() == "Head"
        reverse = self._BooleanVars["reverse-layers"].get()

        self.MakePreview(
            callback,
            state,
            color=color,
            headfirst=headfirst,
            reverse=reverse,
        )

        return True

    def DoPause(self):
        """
        Presses "pause" button, effectively.

        :return: True.
        """
        self.CancelPending("animate")

        if self._Animation["objects"]:
            self._Animation["playing"] = False
            self.DoPressButton("pause-button")
            self.DoUnpressButton("play-button")

        return True

    def DoPlay(self):
        """
        Presses "play" button, effectively.

        :return: True on success; False on failure.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = True
            self.DoPressButton("play-button")
            self.DoUnpressButton("pause-button")
            self.DoAnimate(False)

        return True

    def DoPressButton(self, key):
        """
        Visibly presses a button.

        :param key: Key of button to press.

        :return: True.
        """
        try:
            button = self._Buttons[key]
            if IsOSX():
                button.config(
                    highlightbackground=App.FromRGB(*App.COLORS[key]["fg"])
                )
            else:
                button.config(relief=tk.SUNKEN)
        except KeyError:
            pass

        return True

    def DoReleaseEventLock(self):
        """
        Releases local event lock.

        :return: True.
        """
        self._EventLock = False
        return True

    def DoRebuildData(self, key):
        """
        Rebuilds head or body listings.

        :param key: Either of "head" or "body".

        :return: True.
        """
        CreateInputJSON(key)
        self.InitData(key)
        self.InitOptionMenu(
            self._Frames["b-y1x0"],
            key,
            self._Data[key]["list"],
        )

        return True

    def DoRemakeOffset(self, key):
        """
        Rebuilds per-frame offsets.

        :param key: Either of "head" or "body".

        :return: True.
        """
        self._Data[key]["offset"] = LoadOffsets(key)
        self.UpdateOffsetLabels()
        self.DoMakePreview()

        return True

    def DoSkipFrame(self, skip):
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
        self.SelectAnimRadioButton()

        return True

    def DoUnpressButton(self, key):
        """
        Visibly unpresses a button.

        :param key: Key of button to unpress.

        :return: True.
        """
        try:
            button = self._Buttons[key]
            if IsOSX():
                button.config(
                    highlightbackground=App.FromRGB(*App.COLORS[key]["bg"])
                )
            else:
                button.config(relief=tk.RAISED)
        except KeyError:
            pass

        return True

    def DrawFrameLabels(self):
        """
        Draw frame labels to animation preview canvas.

        :return: True on success; False on failure.
        """
        canvas = self._Canvases["preview-static"]
        for n in range(4):
            App.DrawText(canvas, 18 + 96 * n, 92, "({})".format(n))

        return True

    def ExportFrames(self, *, idle_only=False):
        """
        Composites and exports all frames to file.

        :param idle_only: Whether to export only idle frames. (Default False).

        :return: True on success; False on failure.
        """

        if idle_only:
            message = App.MESSAGES["message"]["success"]["idle"]
        else:
            message = App.MESSAGES["message"]["success"]["full"]

        callback = sprite_splitter.Composite
        reverse = self._BooleanVars["reverse-layers"].get()
        headfirst = self._StringVars["prioritize"].get() == "Head"

        self.DoExport(
            callback,
            message,
            headfirst=headfirst,
            reverse=reverse,
            idle_only=idle_only,
        )

        return True

    def FrameSkip(self, skip):
        """
        Skips any number of frames forward or backward.

        Implements wrapping at bounds.

        :param skip: Number (and direction) of frames to skip.

        :return: True.
        """
        if self._Animation["objects"]:
            self.DoPause()
            self.DoSkipFrame(skip)
            self.UpdateOffsetLabels()
            self.UpdateAnimationImage()

        return True

    def GetKey(self, key):
        """
        Gets a dict key associated with a named body or head.

        :param key: Either of "body" or "head".

        :return: Name's associated dictionary key.
        """
        name = self._StringVars[key].get()
        if name != App.DEFAULT_NAME:
            return self._Data[key].get("data", {}).get(name, "")
        else:
            return ""

    def InitAllButtons(self):
        """
        Initializes all required buttons.

        :return: True.
        """
        # Initialize "play animation" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "play-button",
            lambda: self.AcquireEventLock()
                    and self.TurnPlaybackOn()
                    and self.ReleaseEventLock(),
        )

        # Initialize "pause animation" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "pause-button",
            lambda: self.AcquireEventLock()
                    and self.TurnPlaybackOff()
                    and self.ReleaseEventLock(),
            relief=tk.SUNKEN,
        )

        # Initialize "skip frame right" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "skip-right-button",
            lambda: self.AcquireEventLock()
                    and self.FrameSkip(1)
                    and self.ReleaseEventLock(),
        )

        # Initialize "skip frame left" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "skip-left-button",
            lambda: self.AcquireEventLock()
                    and self.FrameSkip(-1)
                    and self.ReleaseEventLock(),
        )

        # Initialize "shuffle" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "shuffle-button",
            lambda: self.AcquireEventLock()
                    and self.ShuffleAll()
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "shuffle body" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "shuffle-body-button",
            lambda: self.AcquireEventLock()
                    and self.ShuffleBody()
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "shuffle head" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "shuffle-head-button",
            lambda: self.AcquireEventLock()
                    and self.ShuffleHead()
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "clear body" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "clear-body-button",
            lambda: self.AcquireEventLock()
                    and self.ClearBody()
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "clear head" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "clear-head-button",
            lambda: self.AcquireEventLock()
                    and self.ClearHead()
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "reload" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "reload-button",
            lambda: self.AcquireEventLock()
                    and self.DoRemakeOffset("head")
                    and self.DoRemakeOffset("body")
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),

        )

        # Initialize "idle preview" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "preview-idle-button",
            lambda: self.AcquireEventLock()
                    and self.DoMakePreview(state="idle")
                    and self.DoPressButton("preview-idle-button")
                    and self.DoUnpressButton("preview-left-button")
                    and self.DoUnpressButton("preview-right-button")
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
            relief=tk.SUNKEN,
        )

        # Initialize "left preview" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "preview-left-button",
            lambda: self.AcquireEventLock()
                    and self.DoMakePreview(state="left")
                    and self.DoPressButton("preview-left-button")
                    and self.DoUnpressButton("preview-idle-button")
                    and self.DoUnpressButton("preview-right-button")
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "right preview" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "preview-right-button",
            lambda: self.AcquireEventLock()
                    and self.DoMakePreview(state="right")
                    and self.DoPressButton("preview-right-button")
                    and self.DoUnpressButton("preview-left-button")
                    and self.DoUnpressButton("preview-idle-button")
                    and self.JumpFrame(0)
                    and self.ReleaseEventLock(),
        )

        # Initialize "ping-pong" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "ping-pong-button",
            lambda: self.AcquireEventLock()
                    and self.TogglePingpong()
                    and self.ReleaseEventLock(),
        )

        # Initialize "reverse layers" button
        self.InitButton(
            self._Frames["d-y0x0"],
            "layers-button",
            lambda: self.AcquireEventLock()
                    and self.ToggleReverseLayers()
                    and self.ReleaseEventLock(),
        )

        return 0

    def InitAllCanvases(self):
        """
        Initializes all required canvases.

        :return: True on success; False on failure.
        """
        # Initialize "static preview" canvas
        self.InitCanvas(
            self._Frames["a-y1x0"],
            "preview-static",
            App.CANVAS_BORDERS,
        )

        # Initialize "animated preview" canvas
        self.InitCanvas(
            self._Frames["a-y1x0"],
            "preview-anim",
            App.CANVAS_BORDERS,
        )

        return True

    def InitAllCheckboxes(self):
        """
        Initializes all required checkboxes.

        :return: True on success; False on failure.
        """
        assert self

        return True

    def InitAllData(self):
        """
        Initializes all required data.

        :return: True on success; False on failure.
        """
        self.InitData("head")
        self.InitData("body")
        return True

    def InitAllEntries(self):
        """
        Initializes all required entry widgets.

        :return: True
        """
        # Initialize "body x-coordinate" entry
        self.InitEntry(
            self._Frames["c-y1x0a"],
            "body-x",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )
        # Initialize "body y-coordinate" entry
        self.InitEntry(
            self._Frames["c-y1x0a"],
            "body-y",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )
        # Initialize "head x-coordinate" entry
        self.InitEntry(
            self._Frames["c-y0x0a"],
            "head-x",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )
        # Initialize "head y-coordinate" entry
        self.InitEntry(
            self._Frames["c-y0x0a"],
            "head-y",
            tk.W,
            text="+0",
            justify=tk.CENTER,
        )

        return True

    def InitAllFrames(self):
        """
        Initializes all required frames.

        :return: True.
        """
        # Main frames
        self.InitFrame(self._Master, "a-y1x0")
        self.InitFrame(self._Master, "a-y2x0")

        # Container frames
        self.InitFrame(self._Frames["a-y1x0"], "b-y0x3")
        self.InitFrame(self._Frames["a-y2x0"], "b-y1x0")
        self.InitFrame(self._Frames["a-y2x0"], "b-y1x1")
        self.InitFrame(self._Frames["b-y1x0"], "c-y0x0a")
        self.InitFrame(self._Frames["b-y1x0"], "c-y1x0a")
        self.InitFrame(self._Frames["b-y1x0"], "c-y7x0")
        self.InitFrame(self._Frames["b-y1x1"], "c-y0x0b")
        self.InitFrame(self._Frames["b-y1x1"], "c-y0x1")
        self.InitFrame(self._Frames["c-y0x1"], "d-y0x0")
        self.InitFrame(self._Frames["c-y0x1"], "d-y1x0")

        # Padding frames
        self.InitFrame(self._Frames["a-y1x0"], "pad-a-y1x0")
        self.InitFrame(self._Frames["a-y2x0"], "pad-a-y2x0a")
        self.InitFrame(self._Frames["a-y2x0"], "pad-a-y2x0b")
        self.InitFrame(self._Frames["b-y0x3"], "pad-b-y0x3")
        self.InitFrame(self._Frames["b-y1x0"], "pad-b-y1x0")
        self.InitFrame(self._Frames["d-y1x0"], "pad-d-y1x0")
        self.InitFrame(self._Master, "pad-master-y0x0")

        return True

    def InitAllLabels(self):
        """
        Initializes all required labels.

        :return: True on success; False on failure.
        """
        # Initialize "animation speed" label
        self.InitLabel(
            self._Frames["b-y1x0"],
            "speed-anim",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W, 0,
        )

        # Initialize "current frame" label
        self.InitLabel(
            self._Frames["b-y1x0"],
            "frame-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.SW,
        )

        # Initialize "static frames preview" label
        self.InitLabel(
            self._Frames["a-y1x0"],
            "preview-frames-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W,
        )

        # Initialize "animated preview" label
        self.InitLabel(
            self._Frames["a-y1x0"],
            "preview-anim-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W,
        )

        # Initialize "head offset" label
        self.InitLabel(
            self._Frames["c-y0x0a"],
            "offset-head",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W, 0, 0,
        )

        # Initialize "body offset" label
        self.InitLabel(
            self._Frames["c-y1x0a"],
            "offset-body",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W, 0, 0,
        )

        # Initialize "body x-coordinate" label
        self.InitLabel(
            self._Frames["c-y1x0a"],
            "body-x-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W,
        )
        # Initialize "body y-coordinate" label
        self.InitLabel(
            self._Frames["c-y1x0a"],
            "body-y-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W,
        )
        # Initialize "head x-coordinate" label
        self.InitLabel(
            self._Frames["c-y0x0a"],
            "head-x-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W,
        )
        # Initialize "head y-coordinate" label
        self.InitLabel(
            self._Frames["c-y0x0a"],
            "head-y-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.W,
        )

        # Initialize "prioritize" label
        self.InitLabel(
            self._Frames["d-y1x0"],
            "prioritize-label",
            ("calibri", App.FONTSIZE_SMALL),
            tk.NS,
        )

        return True

    def InitAllMenus(self):
        """
        Initializes all required menus.

        :return: True.
        """
        # Initialize "head" menu
        self.InitMenu(
            self._Menus["main-menu"],
            "head-menu",
            {
                "label":   App.LABELS["rebuild-head-data"],
                "command": lambda: self.AcquireEventLock()
                                   and self.RebuildData("head")
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["rebuild-head-images"],
                "command": lambda: self.AcquireEventLock()
                                   and self.RebuildImages("head")
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["rebuild-head-offsets"],
                "command": lambda: self.AcquireEventLock()
                                   and self.RebuildOffsets("head")
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["destroy-head-images"],
                "command": lambda: self.AcquireEventLock()
                                   and self.DestroyImages("head")
                                   and self.ReleaseEventLock(),
            },
        )

        # Initialize "body" menu
        self.InitMenu(
            self._Menus["main-menu"],
            "body-menu",
            {
                "label":   App.LABELS["rebuild-body-data"],
                "command": lambda: self.AcquireEventLock()
                                   and self.RebuildData("body")
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["rebuild-body-images"],
                "command": lambda: self.AcquireEventLock()
                                   and self.RebuildImages("body")
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["rebuild-body-offsets"],
                "command": lambda: self.AcquireEventLock()
                                   and self.RebuildOffsets("body")
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["destroy-body-images"],
                "command": lambda: self.AcquireEventLock()
                                   and self.DestroyImages("body")
                                   and self.ReleaseEventLock(),
            },
        )

        # Initialize "export" menu
        self.InitMenu(
            self._Menus["main-menu"],
            "export-menu",
            {
                "label":   App.LABELS["export-idle"],
                "command": lambda: self.AcquireEventLock()
                                   and self.ExportFrames(idle_only=True)
                                   and self.ReleaseEventLock(),
            },
            {
                "label":   App.LABELS["export-full"],
                "command": lambda: self.AcquireEventLock()
                                   and self.ExportFrames()
                                   and self.ReleaseEventLock(),
            },
        )

        return True

    def InitAllOptionMenus(self):
        """
        Initializes all required option menus.

        :return: True.
        """
        # Initialize "select head" dropdown menu
        self.InitOptionMenu(
            self._Frames["b-y1x0"],
            "head",
            self._Data["head"]["list"],
        )

        # Initialize "select body" dropdown menu
        self.InitOptionMenu(
            self._Frames["b-y1x0"],
            "body",
            self._Data["body"]["list"],
        )

        return True

    def InitAllRadioButtons(self):
        """
        Initializes all required radio buttons.

        :return: True.
        """
        # Initialize "prioritize head" radio button
        self.InitRadio(
            self._Frames["d-y1x0"],
            "prioritize-1",
            self._StringVars["prioritize"],
            "Head",
            tk.W,
            select=True,
        )

        # Initialize "prioritize body" radio button
        self.InitRadio(
            self._Frames["d-y1x0"],
            "prioritize-2",
            self._StringVars["prioritize"],
            "Body",
            tk.W,
        )

        # Initialize "frame #1" radio button
        self.InitRadio(
            self._Frames["c-y7x0"],
            "frame-0",
            self._StringVars["frame"],
            "0",
            tk.W,
            select=True,
            command=lambda: self.AcquireEventLock()
                            and self.JumpFrame(0)
                            and self.ReleaseEventLock(),
        )

        # Initialize "frame #2" radio button
        self.InitRadio(
            self._Frames["c-y7x0"],
            "frame-1",
            self._StringVars["frame"],
            "1",
            tk.W,
            command=lambda: self.AcquireEventLock()
                            and self.JumpFrame(1)
                            and self.ReleaseEventLock(),
        )

        # Initialize "frame #3" radio button
        self.InitRadio(
            self._Frames["c-y7x0"],
            "frame-2",
            self._StringVars["frame"],
            "2",
            tk.W,
            command=lambda: self.AcquireEventLock()
                            and self.JumpFrame(2)
                            and self.ReleaseEventLock(),
        )

        # Initialize "frame #4" radio button
        self.InitRadio(
            self._Frames["c-y7x0"],
            "frame-3",
            self._StringVars["frame"],
            "3",
            tk.W,
            command=lambda: self.AcquireEventLock()
                            and self.JumpFrame(3)
                            and self.ReleaseEventLock(),
        )

        return True

    def InitButton(self, master, tag, command, relief=tk.RAISED):
        """
        Initializes a local button.

        :param master:  Tkinter root frame for button.
        :param tag:     Tag of button to initialize.
        :param command: Callback function for button.
        :param relief:  Initial button relief. (Default tk.RAISED).

        :return: None.
        """
        w, h = App.SIZES.get(tag, App.SIZES["default-button"])
        fg = App.FromRGB(*App.COLORS[tag]["fg"])  # FG color
        bg = App.FromRGB(*App.COLORS[tag]["bg"])  # BG color

        # Image object
        path = App.IMAGES.get(tag, "")
        if path:
            image = sprite_imaging.OpenTkinter(path, w, h)
        else:
            image = None

        # Create button
        button = tk.Button(
            master,
            text=App.LABELS[tag],
            command=command,
        )

        # Configure button
        button.image = image
        button.config(
            width=w,
            height=h,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
            image=image,
            relief=relief,
        )

        # Simulate "raised" and "sunken" on OS X
        if IsOSX():
            if relief == tk.RAISED:
                button.config(
                    highlightbackground=bg,
                    highlightcolor=fg,
                )
            else:
                button.config(
                    highlightbackground=fg,
                    highlightcolor=fg,
                )

        # Position button
        button.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        # Replace local button
        self._Buttons[tag].destroy()
        self._Buttons[tag] = button

        return True

    def InitCanvas(self, master, tag, border):
        """
        Locally initializes a canvas.

        :param master: Widget root.
        :param tag:    Name of canvas to initialize.
        :param border: Border size for canvas.

        :return: True.
        """
        # Create canvas
        canvas = tk.Canvas(
            master,
            width=App.SIZES[tag][0],
            height=App.SIZES[tag][1],
            background=App.FromRGB(*App.COLORS[tag]["bg"]),
            relief=tk.SUNKEN,
            borderwidth=border,
        )

        # Position canvas
        canvas.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        # Replace local canvas
        self._Canvases[tag].destroy()
        self._Canvases[tag] = canvas

        return True

    def InitCheckbox(self, master, tag, sticky, command=None):
        """
        Initializes a checkbox.

        :param master:  Widget root.
        :param tag:     Tag of checkbox to initialize.
        :param sticky:  Anchoring string.
        :param command: Callback function. (Default None).

        :return: True.
        """
        # Create checkbox
        checkbox = tk.Checkbutton(
            master,
            text=App.LABELS[tag],
            variable=self._BooleanVars[tag],
        )

        # Position checkbox
        checkbox.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
            sticky=sticky,
        )

        if command is not None:
            checkbox.config(command=command)

        # Replace local checkbox
        self._Checkboxes[tag].destroy()
        self._Checkboxes[tag] = checkbox

        return True

    def InitData(self, key):
        """
        Completes initialization of data from file.

        :param key: Either of "head" or "body".

        :return: True.
        """
        data = self._Data[key]["data"] = {
            v.get("name", "---"): k
            for k, v in LoadPaths(key).items()
        }

        self._Data[key]["list"] = [App.DEFAULT_NAME] + sorted(list(data))
        self._Data[key]["offset"] = LoadOffsets(key)

        return True

    def InitEntry(self, master, tag, sticky, text="", disabled=True,
                  justify=tk.LEFT):
        """
        Initializes an entry widget.

        :param master:
        :param tag:

        :return: True
        """
        stringVar = self._StringVars[tag]
        stringVar.set(str(text))
        entry = tk.Entry(
            master,
            textvariable=stringVar,
            width=App.SIZES[tag][0],
            justify=justify
        )
        entry.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        if disabled:
            entry.config(state="readonly")

        # Replace local entry
        self._Entries[tag].destroy()
        self._Entries[tag] = entry

        return True

    def InitFrame(self, master, tag):
        """
        Initializes a frame.

        :param master: Widget root.
        :param tag:    Tag of frame to initialize.

        :return: True.
        """
        frame = tk.Frame(
            master,
            width=App.SIZES[tag][0],
            height=App.SIZES[tag][1],
        )

        frame.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
        )

        # Replace local frame
        self._Frames[tag].destroy()
        self._Frames[tag] = frame

        return True

    def InitLabel(self, master, tag, font, sticky, *args):
        """
        Initializes a label.

        :param master: Widget root.
        :param tag:    Tag of label to initialize.
        :param font:   Font of label to initialize.
        :param sticky: Anchoring string.
        :param args:   Zero or more formatting arguments for string.

        :return: True.
        """
        try:
            text = App.LABELS[tag].format(*args)
        except IndexError:
            text = App.LABELS[tag]

        label = tk.Label(master, font=font, text=text)
        label.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        # Replace local label
        self._Labels[tag].destroy()
        self._Labels[tag] = label

        return True

    def InitMenu(self, master, tag, *commands):
        """

        :param master:
        :param command:

        :return: True.
        """
        assert tag != "main-menu"

        menu = tk.Menu(master, tearoff=0)

        for command in commands:
            commandTag = command.get("label", "")
            commandFnc = command.get("command", lambda: print())
            menu.add_command(
                label=commandTag,
                command=commandFnc,
            )

        # Replace local menu
        self._Menus[tag].destroy()
        self._Menus[tag] = menu

        # Add to main menu
        self._Menus["main-menu"].add_cascade(
            label=App.LABELS[tag],
            menu=menu,
        )

    def InitOptionMenu(self, master, tag, options):
        """
        Initializes a menu.

        :param master:  Root of widget.
        :param tag:     Tag of menu to initialize.
        :param options: Options to populate menu with.

        :return: True.
        """
        width = App.SIZES["default-menu"][0]
        foreground = App.FromRGB(*App.COLORS[tag]["fg"])
        background = App.FromRGB(*App.COLORS[tag]["bg"])

        self._StringVars[tag].set(App.LABELS[tag])

        optionmenu = tk.OptionMenu(master, self._StringVars[tag], *options)
        optionmenu.config(
            width=width,
            foreground=foreground,
            background=background,
            activebackground=background,
            activeforeground=foreground,
        )

        # Position OptionMenu
        optionmenu.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        # Replace local OptionMenu
        self._OptionMenus[tag].destroy()
        self._OptionMenus[tag] = optionmenu

        return True

    def InitRadio(self,
                  master,
                  tag,
                  variable,
                  value,
                  sticky,
                  *,
                  select=False,
                  command=None,
                  ):
        """
        Initializes a radio button.

        :param master:
        :param tag:
        :param variable:
        :param value:
        :param sticky:
        :param select:
        :param command:

        :return: True.
        """
        # Create radio button
        radio = tk.Radiobutton(
            master,
            text=App.LABELS[tag],
            variable=variable,
            value=value,
            command=command,
        )

        # Position radio button
        radio.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        # (Optional) Select button
        if select:
            radio.select()
        else:
            radio.deselect()

        # Replace local button
        self._RadioButtons[tag].destroy()
        self._RadioButtons[tag] = radio

        return True

    def InitSliderFramerate(self):
        """
        Completes initialization of framerate slider.

        :return: True.
        """
        scale = tk.Scale(
            self._Frames["c-y0x0b"],
            from_=App.SPEED_SCALE_MAX,
            to=App.SPEED_SCALE_MIN,
            orient=tk.VERTICAL,
            length=App.SIZES["default-slider"][0],
            showvalue=0,
            command=self.UpdateSpeed,
        )

        scale.set(self._Animation["speed"])

        scale.grid(
            row=App.GRID["speed-slider"][0],
            column=App.GRID["speed-slider"][1],
            sticky=tk.W,
            padx=16,
            pady=4,
        )

        self._ScaleAnimSpeed.destroy()
        self._ScaleAnimSpeed = scale

        return True

    def JumpFrame(self, frame):
        """
        Jumps to a specific animation frame.

        :param frame: Frame to jump to.

        :return: True.
        """
        self._Animation["playing"] = False
        self._Animation["frame"] = frame

        self.DoPressButton("pause-button")
        self.DoUnpressButton("play-button")

        self.UpdateAnimationImage()
        self.UpdateOffsetLabels()
        self.SelectAnimRadioButton()

        return True

    def MakeAnimationFrames(self, image, reset):
        """
        Populates local animation buffer.

        :param image: Spritesheet to crop frames from.
        :param reset: Whether to reset animation counters.

        :return: True
        """
        # Get animation frames
        w, h = App.SIZES["preview-anim"]
        self._Animation["objects"] = [
            sprite_imaging.ToPILToTkinter(
                sprite_imaging.Crop(image, [w * n, 0], [w, h])
            ) for n in range(4)
        ]

        # Reset animation counters
        if reset:
            self._Animation["frame"] = 0
            self._Animation["forward"] = True
        self._Animation["speed"] = self._ScaleAnimSpeed.get()

        # Create animated preview
        self._Canvases["preview-anim"].create_image(
            (16, 16),
            anchor=tk.NW,
            image=self._Animation["objects"][0],
        )

        # Update labels
        self.UpdateOffsetLabels()

        return True

    def MakeAnimationPreview(self, image):
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

        self.DrawFrameLabels()

        return True

    def MakePreview(self, func, state, reset=False, **kwargs):
        """
        Generates a static preview image.

        :param func:  Compositing callback function to use.
        :param state: Named state of preview to generate.
        :param reset: Whether to reset animation frame. (Default False).

        :return: True.
        """
        try:
            # Perform sprite composition
            self._Animation["state"] = state
            self._Data["head"]["offset"] = LoadOffsets("head")

            head, body, image = self.DoComposite(func, **kwargs)
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
                        dsize=tuple(App.SIZES["preview-resize"]),
                        interpolation=cv2.INTER_NEAREST,
                    )

                    # Set static and animated previews
                    self.MakeAnimationPreview(image)
                    self.MakeAnimationFrames(image, reset)

                    try:
                        # Populate per-frame head offset data
                        self._Data["head"]["current"] = \
                            self._Data["head"]["offset"][body]
                    except KeyError:
                        self._Data["head"]["current"] = {}

                    try:
                        # Populate per-frame body offset data
                        self._Data["body"]["current"] = \
                            self._Data["body"]["offset"][body]
                    except KeyError:
                        self._Data["body"]["current"] = {}

                    self.UpdateOffsetLabels()

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["failure"]["type"],
            )

        return True

    def RebuildData(self, key):
        """
        Callback function. Rebuilds a given JSON database.

        :param key: Either of "head" or "body".

        :return: True.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["data"][key]
        alert = App.MESSAGES["message"]["rebuild"]["data"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            self.DoRebuildData(key)
            tk.messagebox.showinfo(title, alert)

        return True

    # noinspection PyMethodMayBeStatic
    def RebuildImages(self, key):
        """
        Callback function. Rebuilds intermediate body spritesheets.

        :param key: Either of "head" or "body".

        :return: True.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["image"][key]
        alert = App.MESSAGES["message"]["rebuild"]["image"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            Prepare(key)
            tk.messagebox.showinfo(title, alert)

        return True

    def RebuildOffsets(self, key):
        """
        Callback function. Rebuilds offset database.

        :param key: Either of "head" or "body".

        :return: True.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["offset"][key]
        alert = App.MESSAGES["message"]["rebuild"]["offset"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            self.DoRemakeOffset(key)
            tk.messagebox.showinfo(title, alert)

        return True

    def ScheduleAnimate(self):
        """
        Schedules an animation callback routine.

        :return: True.
        """
        speed = self._Animation["speed"]
        if speed > 0:
            self.SetPending("animate", self.DoAnimate, 1000 // speed)

        return True

    def SelectAnimRadioButton(self):
        """
        Selects the appropriate animation frame radio button.

        :return: True.
        """
        frame = self._Animation["frame"]

        for n in range(4):
            key = "frame-{}".format(n)
            if n == frame:
                self._RadioButtons[key].select()
            else:
                self._RadioButtons[key].deselect()

        return True

    def SetPending(self, key, callback, delay):
        """
        Schedules a callback function to run after a time delay.

        :param key:      Key of callback to flag.
        :param callback: Callback function to trigger.
        :param delay:    Time delay (milliseconds).

        :return: True
        """
        self._PendingJobs[key] = self.after(delay, callback)

        return True

    def ShuffleAll(self):
        """
        Shuffles bodies and heads.

        :return: True.
        """
        self._StringVars["body"].set(random.choice(self._Data["body"]["list"]))
        self._StringVars["head"].set(random.choice(self._Data["head"]["list"]))
        self.DoMakePreview()

        return True

    def ShuffleBody(self):
        """
        Shuffles bodies.

        :return: True.
        """
        self._StringVars["body"].set(random.choice(self._Data["body"]["list"]))
        self.DoMakePreview()

        return True

    def ShuffleHead(self):
        """
        Shuffles heads.

        :return: True.
        """
        self._StringVars["head"].set(random.choice(self._Data["head"]["list"]))
        self.DoMakePreview()

        return True

    def TogglePingpong(self):
        """
        hhh

        :return: True
        """
        isPingpong = self._BooleanVars["pingpong-animation"]
        if isPingpong.get():
            self.DoUnpressButton("ping-pong-button")
            isPingpong.set(False)
        else:
            self.DoPressButton("ping-pong-button")
            isPingpong.set(True)

        return True

    def ToggleReverseLayers(self):
        """
        hhh

        :return: True
        """
        isReverseLayers = self._BooleanVars["reverse-layers"]
        if isReverseLayers.get():
            self.DoUnpressButton("layers-button")
            isReverseLayers.set(False)
        else:
            self.DoPressButton("layers-button")
            isReverseLayers.set(True)

        return True

    def TurnPlaybackOn(self):
        """
        Turns animation playback on.

        :return: True.
        """
        if not self._Animation["playing"]:
            self.DoMakePreview()
            self.DoPlay()

        return True

    def TurnPlaybackOff(self):
        """
        Turns animation playing off.

        :return: True.
        """
        self.DoPause()
        return True

    def UpdateCurrentFrame(self, increment):
        """
        Increments current animation frame.

        :return: True.
        """
        # Check frame iteration type
        isForwards = self._Animation["forward"]
        isPingpong = self._BooleanVars["pingpong-animation"].get()
        if not isPingpong:
            isForwards = True

        # Increment frame
        frame = self._Animation["frame"]

        if self._Animation["objects"]:
            if isForwards:
                # Forwards iteration
                frame += increment
                if frame < 0:
                    if not isPingpong:
                        frame = 3
                        isForwards = True
                    else:
                        frame = 1
                        isForwards = True

                elif frame >= 4:
                    if not isPingpong:
                        frame = 0
                        isForwards = True
                    else:
                        frame = 2
                        isForwards = False

            else:
                # Backwards iteration
                frame -= increment
                if frame < 0:
                    if not isPingpong:
                        frame = 3
                        isForwards = True
                    else:
                        frame = 1
                        isForwards = True

                elif frame >= 4:
                    if not isPingpong:
                        frame = 0
                        isForwards = True
                    else:
                        frame = 2
                        isForwards = False

        # Update references to current frame
        self._Animation["forward"] = isForwards
        self._Animation["frame"] = frame

        return True

    def UpdateOffsetLabel(self, key, state, frame):
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
            self._StringVars[strvarx].set("{0:+d}".format(xy[0]))
            self._StringVars[strvary].set("{0:+d}".format(xy[1]))

        except (KeyError, IndexError):
            self._StringVars[strvarx].set("{0:+d}".format(0))
            self._StringVars[strvary].set("{0:+d}".format(0))

        return True

    def UpdateAnimationImage(self):
        """
        Updates currently-previewed animation frame.

        :return: True.
        """
        try:
            # Draw frame to canvas
            animObjects = self._Animation["objects"]
            animFrame = self._Animation["frame"]
            animImage = animObjects[animFrame]

            self._Canvases["preview-anim"].create_image(
                (16, 16),
                anchor=tk.NW,
                image=animImage,
            )

        except IndexError:
            # Current frame is invalid
            pass

        return True

    def UpdateOffsetLabels(self):
        """
        Updates per-frame (x,y) head and body offset labels.

        :return: True.
        """
        state = self._Animation["state"]
        frame = self._Animation["frame"]

        self.UpdateOffsetLabel("head", state, frame)
        self.UpdateOffsetLabel("body", state, frame)

        return True

    def UpdateSpeed(self, speed):
        """
        Updates current animation speed.

        :param speed: New framerate.

        :return: True.
        """
        speed = int(speed)
        text = App.LABELS["speed-anim"].format(speed)

        self._Labels["speed-anim"].config(text=text)
        self._Animation["speed"] = speed

        # Play animation
        self.CancelPending("animate")
        self.ScheduleAnimate()

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
