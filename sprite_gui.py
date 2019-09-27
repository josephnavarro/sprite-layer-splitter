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
        # Preview canvases
        "preview-anim":         [96, 96],
        "preview-resize":       [384, 96],
        "preview-static":       [384, 96],

        # Icon-based buttons
        "play-button":          [32, 32],
        "pause-button":         [32, 32],
        "skip-right-button":    [32, 32],
        "skip-left-button":     [32, 32],
        "shuffle-button":       [32, 32],
        "shuffle-body-button":  [32, 32],
        "shuffle-head-button":  [32, 32],
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
        SIZES["default-slider"] = [256, 0]

        FONTSIZE_VAR_W = 13
        FONTSIZE_MONOS = 10
        FONTSIZE_SMALL = 9
        CANVAS_BORDERS = 13

    else:
        # OS X / Linux
        SIZES["default-button"] = [28, 0]
        SIZES["default-menu"] = [25, 0]
        SIZES["default-slider"] = [248, 0]

        FONTSIZE_VAR_W = 13
        FONTSIZE_MONOS = 14
        FONTSIZE_SMALL = 13
        CANVAS_BORDERS = 13

    GRID = {
        # Preview canvases
        "preview-static":       [0, 1],
        "preview-anim":         [0, 2],
        "preview-frames-label": [1, 1],
        "preview-anim-label":   [1, 2],

        # Left column
        "head-options":         [7, 0],
        "head":                 [8, 0],
        "rebuild-head-images":  [9, 0],
        "rebuild-head-data":    [10, 0],
        "rebuild-head-offsets": [11, 0],
        "destroy-head-images":  [12, 0],

        "body-options":         [13, 0],
        "body":                 [14, 0],
        "rebuild-body-images":  [15, 0],
        "rebuild-body-data":    [16, 0],
        "rebuild-body-offsets": [17, 0],
        "destroy-body-images":  [18, 0],

        # Right column
        "preview-options":      [7, 1],
        "state":                [7, 1],
        "preview-idle":         [8, 1],
        "preview-left":         [9, 1],
        "preview-right":        [10, 1],
        "pingpong-animation":   [11, 1],
        "reverse-layers":       [12, 1],

        "export-options":       [13, 1],
        "export-full":          [14, 1],
        "export-idle":          [15, 1],
        "prioritize-label":     [16, 1],
        "prioritize-1":         [17, 1],
        "prioritize-2":         [18, 1],

        # Frame data readout
        "speed-slider":         [1, 0],
        "speed-anim":           [2, 0],
        "offset-head":          [4, 0],
        "offset-body":          [5, 0],

        "frame-0":              [6, 0],
        "frame-1":              [6, 1],
        "frame-2":              [6, 2],
        "frame-3":              [6, 3],

        # Icon-based buttons
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
    }

    # Padding for widgets
    PAD = {
        # Preview canvases
        "preview-frames-label": [0, 0],
        "preview-anim-label":   [0, 0],
        "preview-static":       [0, 0],
        "preview-anim":         [0, 0],

        # Export options
        "export-full":          [4, 4],
        "export-idle":          [4, 4],
        "export-options":       [4, 4],

        # Frame data readout
        "speed-anim":           [12, 0],
        "offset-head":          [12, 0],
        "offset-body":          [12, 0],
        "frame-0":              [0, 0],
        "frame-1":              [0, 0],
        "frame-2":              [0, 0],
        "frame-3":              [0, 0],

        # Preview options
        "preview-options":      [4, 4],
        "body-options":         [4, 4],
        "head-options":         [4, 4],

        # Layer collision resolution
        "prioritize-label":     [4, 4],
        "prioritize-1":         [0, 0],
        "prioritize-2":         [0, 0],

        # Preview options
        "state":                [4, 4],
        "preview-idle":         [4, 4],
        "preview-left":         [4, 4],
        "preview-right":        [4, 4],
        "pingpong-animation":   [4, 0],
        "reverse-layers":       [4, 0],

        # Head options
        "head":                 [4, 4],
        "rebuild-head-data":    [4, 4],
        "rebuild-head-images":  [4, 4],
        "rebuild-head-offsets": [4, 4],
        "destroy-head-images":  [4, 4],

        # Body options
        "body":                 [4, 4],
        "rebuild-body-data":    [4, 4],
        "rebuild-body-images":  [4, 4],
        "rebuild-body-offsets": [4, 4],
        "destroy-body-images":  [4, 4],

        # Icon-based buttons
        "play-button":          [0, 0],
        "pause-button":         [0, 0],
        "skip-left-button":     [0, 0],
        "skip-right-button":    [0, 0],
        "shuffle-button":       [0, 0],
        "shuffle-body-button":  [0, 0],
        "shuffle-head-button":  [0, 0],
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
        # Canvas captions
        "preview-frames-label": "Static frame preview",
        "preview-anim-label":   "Animated preview",

        # Export options
        "export-options":       "Export options",
        "export-full":          "Export all frames",
        "export-idle":          "Export idle frames",

        # Preview options
        "preview-options":      "Preview options",
        "state":                "Select state",
        "preview-idle":         "Preview idle frames",
        "preview-left":         "Preview left frames",
        "preview-right":        "Preview right frames",
        "pingpong-animation":   "Ping-pong animation",
        "reverse-layers":       "Reverse layering order",

        # Body options
        "body-options":         "Body options",
        "body":                 "Select body",
        "rebuild-body-images":  "Remake body sources",
        "rebuild-body-data":    "Refresh body listing",
        "rebuild-body-offsets": "Refresh body offsets",
        "destroy-body-images":  "Clean body sources",

        # Head options
        "head-options":         "Head options",
        "head":                 "Select head",
        "rebuild-head-images":  "Remake head sources",
        "rebuild-head-data":    "Refresh head listing",
        "rebuild-head-offsets": "Refresh head offsets",
        "destroy-head-images":  "Clean head sources",

        # Frame data readout
        "offset-body":          "Body  :=  x: {0:+d} / y: {1:+d}",
        "offset-head":          "Head  :=  x: {0:+d} / y: {1:+d}",
        "speed-anim":           "Speed :=  {0:d}",
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
        "reload-button":        os.path.join("misc", "reload.png"),
        "preview-idle-button":  os.path.join("misc", "idle.png"),
        "preview-left-button":  os.path.join("misc", "left.png"),
        "preview-right-button": os.path.join("misc", "right.png"),
        "ping-pong-button":     os.path.join("misc", "ping-pong.png"),
        "layers-button":        os.path.join("misc", "layers.png"),
    }

    # Widget colors (RGB, foreground + background)
    COLORS = {
        "export-full":          {"fg": [0, 0, 0], "bg": [244, 212, 248]},
        "export-idle":          {"fg": [0, 0, 0], "bg": [244, 212, 248]},
        "preview-idle":         {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "preview-left":         {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "preview-right":        {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "rebuild-body-data":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "rebuild-body-images":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "rebuild-body-offsets": {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "destroy-body-images":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "rebuild-head-data":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "rebuild-head-images":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "rebuild-head-offsets": {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "destroy-head-images":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "head":                 {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "body":                 {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "state":                {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "preview-static":       {"fg": [0, 0, 0], "bg": [128, 128, 128]},
        "preview-anim":         {"fg": [0, 0, 0], "bg": [128, 128, 128]},

        # Icon-based buttons
        "play-button":          {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "pause-button":         {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "skip-right-button":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "skip-left-button":     {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "shuffle-button":       {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "shuffle-body-button":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "shuffle-head-button":  {"fg": [0, 0, 0], "bg": [222, 222, 222]},
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

        self.after(timeout, self.KillITunes)

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

        self._AfterJob = None

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

        # Widget-containing frames
        self._FrameGroupTop = tk.Frame(self._Master)
        self._FrameGroupTop.grid(row=1, column=0)

        self._FrameGroupBot = tk.Frame(self._Master)
        self._FrameGroupBot.grid(row=2, column=0)

        self._FrameTopRight = tk.Frame(self._FrameGroupTop)
        self._FrameTopRight.grid(row=0, column=3)

        self._FrameBotLeft = tk.Frame(self._FrameGroupBot)
        self._FrameBotLeft.grid(column=0, row=1)

        self._FrameBotRight = tk.Frame(self._FrameGroupBot)
        self._FrameBotRight.grid(column=1, row=1)

        self._FrameBotLeftBot = tk.Frame(self._FrameBotLeft)
        self._FrameBotLeftBot.grid(column=0, row=7)

        # Padding frames
        self._FramePadMidTop = tk.Frame(self._FrameTopRight, width=1, height=10)
        self._FramePadMidTop.grid(row=0, column=0)

        self._FramePadBorder = tk.Frame(self._FrameGroupBot, height=10)
        self._FramePadBorder.grid(row=6)

        self._FramePadBottom = tk.Frame(self._FrameGroupBot, height=10)
        self._FramePadBottom.grid(row=24)

        self._FramePadTopleft = tk.Frame(self._FrameGroupTop, height=10)
        self._FramePadTopleft.grid(row=1)

        self._FramePadTopleft = tk.Frame(self._FrameGroupTop, height=10)
        self._FramePadTopleft.grid(row=2)

        self._FramePadTop = tk.Frame(self._Master, height=10)
        self._FramePadTop.grid(row=0)

        # Boolean variables
        self._BooleanVars = {
            "pingpong-animation": tk.BooleanVar(),
            "reverse-layers":     tk.BooleanVar(),
        }

        # String variables
        self._StringVars = {
            "head":       tk.StringVar(self._Master),
            "body":       tk.StringVar(self._Master),
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
        self._Menus = {
            "head":  tk.OptionMenu(
                self._FrameGroupBot,
                self._StringVars["head"],
                *self._Data["head"]["list"]
            ),
            "body":  tk.OptionMenu(
                self._FrameGroupBot,
                self._StringVars["body"],
                *self._Data["body"]["list"]
            ),
            "state": tk.OptionMenu(
                self._FrameGroupBot,
                self._StringVars["state"],
                *STATES
            )
        }

        # Labels
        self._Labels = {
            "preview-frames-label": tk.Label(),
            "preview-anim-label":   tk.Label(),
            "offset-head":          tk.Label(),
            "offset-body":          tk.Label(),
            "speed-anim":           tk.Label(),
            "prioritize-label":     tk.Label(),
            "head-options":         tk.Label(),
            "body-options":         tk.Label(),
            "preview-options":      tk.Label(),
            "export-options":       tk.Label(),
        }

        # Sliders
        self._ScaleAnimSpeed = tk.Scale()

        # Complete widget initialization
        self.InitData("head")
        self.InitData("body")

        self.InitAllButtons()
        self.InitAllCanvases()
        self.InitAllCheckboxes()
        self.InitAllLabels()
        self.InitAllMenus()
        self.InitAllRadioButtons()

        self.InitSliderFramerate()

    # noinspection PyMethodMayBeStatic
    def DestroyImages(self, key):
        """
        Callback function. Destroys intermediate spritesheets.

        :param key: Either of "head" or "body".

        :return: 0 on success; -1 on failure.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["destroy"][key]
        alert = App.MESSAGES["message"]["destroy"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushInputs(key)
            tk.messagebox.showinfo(title, alert)

        return 0

    def DoAnimate(self, update=True):
        """
        Local animation callback function.

        :return: 0 on success; -1 on failure.
        """
        if self._Animation["playing"]:
            if update:
                self.UpdateCurrentFrame(1)
            else:
                self.UpdateCurrentFrame(0)

            speed = self._Animation["speed"]
            if speed > 0:
                delay = 1000 // speed
                self._AfterJob = self.after(delay, self.DoAnimate)

        self.UpdateOffsetLabels()
        self.UpdateAnimationImage()
        self.SelectAnimRadioButton()

        return 0

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
            alert = App.MESSAGES["message"]["invalid"]["head"]  # type: str
            tk.messagebox.showinfo(title, alert.format(e.filename))

        except sprite_splitter.NonexistentBodyException as e:
            # Body spritesheet does not exist
            title = App.WINDOW_TITLE
            alert = App.MESSAGES["message"]["invalid"]["body"]  # type: str
            tk.messagebox.showinfo(title, alert.format(e.filename))

        except cv2.error:
            # CV2 image processing error
            raise InvalidFilenameException

        return head, body, im

    def DoExport(self, func, message, **kwargs):
        """
        Composites and exports animation frames to file.

        :param func:    Frame compositing callback function.
        :param message: Success message to display.

        :return: 0 on success; -1 on failure.
        """
        try:
            # Perform sprite composition
            head, body, im = self.DoComposite(func, **kwargs)

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

            return 0

        except InvalidFilenameException:
            # Image format not recognized
            title = App.WINDOW_TITLE
            alert = App.MESSAGES["message"]["failure"]["type"]
            tk.messagebox.showinfo(title, alert)
            return -1

        except EmptyFilenameException:
            # Filename not specified
            return -1

    def DoMakePreview(self, *, state=""):
        """
        Creates an animated preview.

        :param state: State to preview. (Default empty).

        :return: 0 on success; -1 on failure.
        """
        self.TurnPlaybackOff()

        state = state or str(self._Animation["state"])
        color = App.COLORS["preview-static"]["bg"]
        headfirst = self._StringVars["prioritize"].get() == "Head"
        reverse = self._BooleanVars["reverse-layers"].get()

        self.MakePreview(
            sprite_splitter.Composite,
            state,
            color=color,
            headfirst=headfirst,
            reverse=reverse,
        )

        return 0

    def DoPause(self):
        """
        Presses "pause" button, effectively.

        :return: 0 on success; -1 on failure.
        """
        if self._AfterJob is not None:
            self.after_cancel(self._AfterJob)

        if self._Animation["objects"]:
            self._Animation["playing"] = False
            self.DoPressButton("pause-button")
            self.DoUnpressButton("play-button")

        return 0

    def DoPlay(self):
        """
        Presses "play" button, effectively.

        :return: 0 on success; -1 on failure.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = True
            self.DoPressButton("play-button")
            self.DoUnpressButton("pause-button")
            self.DoAnimate(False)

        return 0

    def DoPressButton(self, key):
        """
        Visibly presses a button.

        :param key: Key of button to press.

        :return: 0 on success; -1 on failure.
        """
        try:
            self._Buttons[key].config(relief=tk.SUNKEN)
            return 0
        except KeyError:
            return -1

    def DoRemakeOffset(self, key):
        """
        Rebuilds per-frame offsets.

        :param key: Either of "head" or "body".

        :return: 0 on success, -1 on failure.
        """
        self._Data[key]["offset"] = LoadOffsets(key)
        self.UpdateOffsetLabels()
        self.DoMakePreview()

        return 0

    def DoSkipFrame(self, skip):
        """
        Skips a specific number of animation frames.

        :param skip: Number (and direction) of frames to skip.

        :return: 0 on success; -1 on failure.
        """
        frame = self._Animation["frame"] + skip
        if frame < 0:
            frame = 3
        elif frame >= 4:
            frame = 0

        self._Animation["frame"] = frame
        self.SelectAnimRadioButton()

        return 0

    def DoUnpressButton(self, key):
        """
        Visibly unpresses a button.

        :param key: Key of button to unpress.

        :return: 0 on success; -1 on failure.
        """
        try:
            self._Buttons[key].config(relief=tk.RAISED)
            return 0
        except KeyError:
            return -1

    def DrawFrameLabels(self):
        """
        Draw frame labels to animation preview canvas.

        :return: 0 on success; -1 on failure.
        """
        canvas = self._Canvases["preview-static"]
        for n in range(4):
            App.DrawText(canvas, 18 + 96 * n, 92, "({})".format(n))

        return 0

    def ExportFrames(self, *, idle_only=False):
        """
        Composites and exports all frames to file.

        :param idle_only: Whether to export only idle frames. (Default False).

        :return: 0 on success, -1 on failure.
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

        return 0

    def FrameSkip(self, skip):
        """
        Skips any number of frames forward or backward.
        Implements wrapping at bounds.

        :param skip: Number (and direction) of frames to skip.

        :return: 0 on success; -1 on failure.
        """
        if self._Animation["objects"]:
            self.DoPause()
            self.DoSkipFrame(skip)
            self.UpdateOffsetLabels()
            self.UpdateAnimationImage()

        return 0

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

        :return: 0 on success; -1 on failure.
        """
        # Initialize "rebuild head data" button
        self.InitButton(
            self._FrameGroupBot,
            "rebuild-head-data",
            lambda: self.RebuildData("head"),
        )

        # Initialize "rebuild head images" button
        self.InitButton(
            self._FrameGroupBot,
            "rebuild-head-images",
            lambda: self.RebuildImages("head"),
        )

        # Initialize "rebuild head offsets" button
        self.InitButton(
            self._FrameGroupBot,
            "rebuild-head-offsets",
            lambda: self.RebuildOffsets("head"),
        )

        # Initialize "destroy head images" button
        self.InitButton(
            self._FrameGroupBot,
            "destroy-head-images",
            lambda: self.DestroyImages("head"),
        )

        # Initialize "play animation" button
        self.InitButton(
            self._FrameBotRight,
            "play-button",
            self.TurnPlaybackOn,
        )

        # Initialize "pause animation" button
        self.InitButton(
            self._FrameBotRight,
            "pause-button",
            self.TurnPlaybackOff,
            relief=tk.SUNKEN,
        )

        # Initialize "skip frame right" button
        self.InitButton(
            self._FrameBotRight,
            "skip-right-button",
            lambda: self.FrameSkip(1),
        )

        # Initialize "skip frame left" button
        self.InitButton(
            self._FrameBotRight,
            "skip-left-button",
            lambda: self.FrameSkip(-1),
        )

        # Initialize "shuffle" button
        self.InitButton(
            self._FrameBotRight,
            "shuffle-button",
            lambda: (self.ShuffleAll() + self.JumpFrame(0)),
        )

        # Initialize "shuffle" button
        self.InitButton(
            self._FrameBotRight,
            "shuffle-body-button",
            lambda: (self.ShuffleBody() + self.JumpFrame(0)),
        )

        # Initialize "shuffle" button
        self.InitButton(
            self._FrameBotRight,
            "shuffle-head-button",
            lambda: (self.ShuffleHead() + self.JumpFrame(0)),
        )

        # Initialize "reload" button
        self.InitButton(
            self._FrameBotRight,
            "reload-button",
            lambda: (self.DoRemakeOffset("head") +
                     self.DoRemakeOffset("body") +
                     self.JumpFrame(0)),
        )

        # Initialize "idle preview" button
        self.InitButton(
            self._FrameBotRight,
            "preview-idle-button",
            lambda: (self.DoMakePreview(state="idle") +
                     self.DoPressButton("preview-idle-button") +
                     self.DoUnpressButton("preview-left-button") +
                     self.DoUnpressButton("preview-right-button") +
                     self.JumpFrame(0)),
            relief=tk.SUNKEN,
        )

        # Initialize "left preview" button
        self.InitButton(
            self._FrameBotRight,
            "preview-left-button",
            lambda: (self.DoMakePreview(state="left") +
                     self.DoPressButton("preview-left-button") +
                     self.DoUnpressButton("preview-idle-button") +
                     self.DoUnpressButton("preview-right-button") +
                     self.JumpFrame(0)),
        )

        # Initialize "right preview" button
        self.InitButton(
            self._FrameBotRight,
            "preview-right-button",
            lambda: (self.DoMakePreview(state="right") +
                     self.DoPressButton("preview-right-button") +
                     self.DoUnpressButton("preview-left-button") +
                     self.DoUnpressButton("preview-idle-button") +
                     self.JumpFrame(0)),
        )

        # Initialize "ping-pong" button
        self.InitButton(
            self._FrameBotRight,
            "ping-pong-button",
            lambda: print("Baz"),
        )

        # Initialize "reverse layers" button
        self.InitButton(
            self._FrameBotRight,
            "layers-button",
            lambda: print("Baz"),
        )

        # Initialize "rebuild body offsets" button
        self.InitButton(
            self._FrameGroupBot,
            "rebuild-body-offsets",
            lambda: self.RebuildOffsets("body"),
        )

        # Initialize "destroy body images" button
        self.InitButton(
            self._FrameGroupBot,
            "destroy-body-images",
            lambda: self.DestroyImages("body"),
        )

        # Initialize "rebuild body data" button
        self.InitButton(
            self._FrameGroupBot,
            "rebuild-body-data",
            lambda: self.RebuildData("body"),
        )

        # Initialize "rebuild body images" button
        self.InitButton(
            self._FrameGroupBot,
            "rebuild-body-images",
            lambda: self.RebuildImages("body"),
        )

        # Initialize "make idle preview" button
        self.InitButton(
            self._FrameGroupBot,
            "preview-idle",
            lambda: (self.DoMakePreview(state="idle") +
                     self.DoPressButton("preview-idle-button") +
                     self.DoUnpressButton("preview-left-button") +
                     self.DoUnpressButton("preview-right-button") +
                     self.JumpFrame(0)),
        )

        # Initialize "make left preview" button
        self.InitButton(
            self._FrameGroupBot,
            "preview-left",
            lambda: (self.DoMakePreview(state="left") +
                     self.DoPressButton("preview-left-button") +
                     self.DoUnpressButton("preview-idle-button") +
                     self.DoUnpressButton("preview-right-button") +
                     self.JumpFrame(0)),
        )

        # Initialize "make right preview" button
        self.InitButton(
            self._FrameGroupBot,
            "preview-right",
            lambda: (self.DoMakePreview(state="right") +
                     self.DoPressButton("preview-right-button") +
                     self.DoUnpressButton("preview-left-button") +
                     self.DoUnpressButton("preview-idle-button") +
                     self.JumpFrame(0)),
        )

        # Initialize "export idle frames" button
        self.InitButton(
            self._FrameGroupBot,
            "export-idle",
            lambda: self.ExportFrames(idle_only=True),
        )

        # Initialize "export all frames" button
        self.InitButton(
            self._FrameGroupBot,
            "export-full",
            lambda: self.ExportFrames(),
        )

        return 0

    def InitAllCanvases(self):
        """
        Initializes all required canvases.

        :return: 0 on success; -1 on failure.
        """
        # Initialize "static preview" canvas
        self.InitCanvas(
            self._FrameGroupTop,
            "preview-static",
            App.CANVAS_BORDERS,
        )

        # Initialize "animated preview" canvas
        self.InitCanvas(
            self._FrameGroupTop,
            "preview-anim",
            App.CANVAS_BORDERS,
        )

        return 0

    def InitAllCheckboxes(self):
        """
        Initializes all required checkboxes.

        :return: 0 on success; -1 on failure.
        """
        # Initialize "pingpong animation" checkbox
        self.InitCheckbox(
            self._FrameGroupBot,
            "pingpong-animation", tk.W,
        )

        # Initialize "reverse layers" checkbox
        self.InitCheckbox(
            self._FrameGroupBot,
            "reverse-layers", tk.W,
        )

        return 0

    def InitAllData(self):
        """
        Initializes all required data.

        :return: 0 on success; -1 on failure.
        """
        self.InitData("head")
        self.InitData("body")
        return 0

    def InitAllLabels(self):
        """
        Initializes all required labels.

        :return: 0 on success; -1 on failure.
        """
        # Initialize "export options" label
        self.InitLabel(
            self._FrameGroupBot, "export-options",
            ("sans-serif", App.FONTSIZE_VAR_W, "bold"), tk.NS,
        )

        # Initialize "animation speed" label
        self.InitLabel(
            self._FrameBotLeft, "speed-anim",
            ("Courier", App.FONTSIZE_MONOS), tk.W, 0,
        )

        # Initialize "static frames preview" label
        self.InitLabel(
            self._FrameGroupTop, "preview-frames-label",
            ("arial", App.FONTSIZE_SMALL), tk.W,
        )

        # Initialize "animated preview" label
        self.InitLabel(
            self._FrameGroupTop, "preview-anim-label",
            ("arial", App.FONTSIZE_SMALL), tk.W,
        )

        # Initialize "head offset" label
        self.InitLabel(
            self._FrameBotLeft, "offset-head",
            ("Courier", App.FONTSIZE_MONOS), tk.W,
            0, 0,
        )

        # Initialize "body offset" label
        self.InitLabel(
            self._FrameBotLeft, "offset-body",
            ("Courier", App.FONTSIZE_MONOS), tk.W,
            0, 0,
        )

        # Initialize "preview options" label
        self.InitLabel(
            self._FrameGroupBot, "preview-options",
            ("sans-serif", App.FONTSIZE_VAR_W, "bold"), tk.NS,
        )

        # Initialize "body options" label
        self.InitLabel(
            self._FrameGroupBot, "body-options",
            ("sans-serif", App.FONTSIZE_VAR_W, "bold"), tk.NS,
        )

        # Initialize "head options" label
        self.InitLabel(
            self._FrameGroupBot, "head-options",
            ("sans-serif", App.FONTSIZE_VAR_W, "bold"), tk.NS,
        )

        # Initialize "prioritize" label
        self.InitLabel(
            self._FrameGroupBot, "prioritize-label",
            ("sans-serif", App.FONTSIZE_VAR_W, "bold"), tk.NS,
        )

        return 0

    def InitAllMenus(self):
        """
        Initializes all required menus.

        :return: 0 on success; -1 on failure.
        """
        # Initialize "select head" dropdown menu
        self.InitMenu(
            self._FrameGroupBot, "head",
            self._Data["head"]["list"],
        )

        # Initialize "select body" dropdown menu
        self.InitMenu(
            self._FrameGroupBot, "body",
            self._Data["body"]["list"],
        )

        return 0

    def InitAllRadioButtons(self):
        """
        Initializes all required radio buttons.

        :return: None.
        """
        # Initialize "prioritize head" radio button
        self.InitRadio(
            self._FrameGroupBot, "prioritize-1",
            self._StringVars["prioritize"], "Head", tk.W,
            select=True,
        )

        # Initialize "prioritize body" radio button
        self.InitRadio(
            self._FrameGroupBot, "prioritize-2",
            self._StringVars["prioritize"], "Body", tk.W,
        )

        # Initialize "frame #1" radio button
        self.InitRadio(
            self._FrameBotLeftBot, "frame-0",
            self._StringVars["frame"], "0", tk.W,
            select=True,
            command=lambda: self.JumpFrame(0)
        )

        # Initialize "frame #2" radio button
        self.InitRadio(
            self._FrameBotLeftBot, "frame-1",
            self._StringVars["frame"], "1", tk.W,
            command=lambda: self.JumpFrame(1),
        )

        # Initialize "frame #3" radio button
        self.InitRadio(
            self._FrameBotLeftBot, "frame-2",
            self._StringVars["frame"], "2", tk.W,
            command=lambda: self.JumpFrame(2)
        )

        # Initialize "frame #4" radio button
        self.InitRadio(
            self._FrameBotLeftBot, "frame-3",
            self._StringVars["frame"], "3", tk.W,
            command=lambda: self.JumpFrame(3)
        )

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

    def InitCanvas(self, master, tag, border):
        """
        Locally initializes a canvas.

        :param master: Widget root.
        :param tag:    Name of canvas to initialize.
        :param border: Border size for canvas.

        :return: None.
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

    def InitCheckbox(self, master, tag, sticky, command=None):
        """
        Initializes a checkbox.

        :param master:  Widget root.
        :param tag:     Tag of checkbox to initialize.
        :param sticky:  Anchoring string.
        :param command: Callback function. (Default None).

        :return: None.
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

    def InitData(self, key):
        """
        Completes initialization of data from file.

        :param key: Either of "head" or "body".

        :return: None.
        """
        data = self._Data[key]["data"] = {
            v.get("name", "---"): k
            for k, v in LoadPaths(key).items()
        }

        self._Data[key]["list"] = [App.DEFAULT_NAME] + sorted(list(data))
        self._Data[key]["offset"] = LoadOffsets(key)

    def InitLabel(self, master, tag, font, sticky, *args):
        """
        Initializes a label.

        :param master: Widget root.
        :param tag:    Tag of label to initialize.
        :param font:   Font of label to initialize.
        :param sticky: Anchoring string.
        :param args:   Zero or more formatting arguments for string.

        :return: None.
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

        self._Labels[tag].destroy()
        self._Labels[tag] = label

    def InitMenu(self, master, tag, options):
        """
        Initializes a menu.

        :param master:  Root of widget.
        :param tag:     Tag of menu to initialize.
        :param options: Options to populate menu with.

        :return: None.
        """
        width = App.SIZES["default-menu"][0]
        foreground = App.FromRGB(*App.COLORS[tag]["fg"])
        background = App.FromRGB(*App.COLORS[tag]["bg"])

        self._StringVars[tag].set(App.LABELS[tag])

        menu = tk.OptionMenu(master, self._StringVars[tag], *options)
        menu.config(
            width=width,
            foreground=foreground,
            background=background,
            activebackground=background,
            activeforeground=foreground,
        )

        menu.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        self._Menus[tag].destroy()
        self._Menus[tag] = menu

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

        :return: None.
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

    def InitSliderFramerate(self):
        """
        Completes initialization of framerate slider.

        :return: None.
        """
        scale = tk.Scale(
            self._FrameBotLeft,
            from_=App.SPEED_SCALE_MIN,
            to=App.SPEED_SCALE_MAX,
            orient=tk.HORIZONTAL,
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

    def JumpFrame(self, frame):
        """
        Jumps to a specific animation frame.

        :param frame: Frame to jump to.

        :return: 0 on success; -1 on failure.
        """
        self._Animation["playing"] = False
        self._Animation["frame"] = frame

        self.DoPressButton("pause-button")
        self.DoUnpressButton("play-button")

        self.UpdateAnimationImage()
        self.UpdateOffsetLabels()
        self.SelectAnimRadioButton()

        return 0

    def MakeAnimationFrames(self, image, reset):
        """
        Populates local animation buffer.

        :param image: Spritesheet to crop frames from.
        :param reset: Whether to reset animation counters.

        :return: None
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

        # Create preview image
        self._Canvases["preview-anim"].create_image(
            (16, 16),
            anchor=tk.NW,
            image=self._Animation["objects"][0],
        )

        # Update labels
        self.UpdateOffsetLabels()

    def MakeAnimationPreview(self, image):
        """
        Displays static preview frames.

        :param image: Image to display.

        :return: None.
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

    def MakePreview(self, func, state, reset=False, **kwargs):
        """
        Generates a static preview image.

        :param func:  Compositing callback function to use.
        :param state: Named state of preview to generate.
        :param reset: Whether to reset animation frame. (Default False).

        :return: None.
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

    def RebuildData(self, key):
        """
        Callback function. Rebuilds a given JSON database.

        :param key: Either of "head" or "body".

        :return: 0 on success; -1 on failure.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["data"][key]
        alert = App.MESSAGES["message"]["rebuild"]["data"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateInputJSON(key)
            self.InitData(key)
            self.InitMenu(self._FrameGroupBot, key, self._Data[key]["list"])
            tk.messagebox.showinfo(title, alert)

        return 0

    # noinspection PyMethodMayBeStatic
    def RebuildImages(self, key):
        """
        Callback function. Rebuilds intermediate body spritesheets.

        :param key: Either of "head" or "body".

        :return: 0 on success; -1 on failure.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["image"][key]
        alert = App.MESSAGES["message"]["rebuild"]["image"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            Prepare(key)
            tk.messagebox.showinfo(title, alert)

        return 0

    def RebuildOffsets(self, key):
        """
        Callback function. Rebuilds offset database.

        :param key: Either of "head" or "body".

        :return: 0 on success; -1 on failure.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["offset"][key]
        alert = App.MESSAGES["message"]["rebuild"]["offset"][key]

        if tk.messagebox.askquestion(title, query) == "yes":
            self.DoRemakeOffset(key)
            tk.messagebox.showinfo(title, alert)

        return 0

    def SelectAnimRadioButton(self):
        """
        Selects the appropriate animation frame radio button.

        :return: 0 on success; -1 on failure.
        """
        frame = self._Animation["frame"]

        for n in range(4):
            key = "frame-{}".format(n)
            if n == frame:
                self._RadioButtons[key].select()
            else:
                self._RadioButtons[key].deselect()

        return 0

    def ShuffleAll(self):
        """
        Shuffles bodies and heads.

        :return: 0 on success; -1 on failure.
        """
        self._StringVars["body"].set(random.choice(self._Data["body"]["list"]))
        self._StringVars["head"].set(random.choice(self._Data["head"]["list"]))
        self.DoMakePreview()

        return 0

    def ShuffleBody(self):
        """
        Shuffles bodies.

        :return: 0 on success; -1 on failure.
        """
        self._StringVars["body"].set(random.choice(self._Data["body"]["list"]))
        self.DoMakePreview()

        return 0

    def ShuffleHead(self):
        """
        Shuffles heads.

        :return: 0 on success; -1 on failure.
        """
        self._StringVars["head"].set(random.choice(self._Data["head"]["list"]))
        self.DoMakePreview()

        return 0

    def TurnPlaybackOn(self):
        """
        Turns animation playback on.

        :return: 0 on success; -1 on failure.
        """
        if not self._Animation["playing"]:
            self.DoMakePreview()
            self.DoPlay()

        return 0

    def TurnPlaybackOff(self):
        """
        Turns animation playing off.

        :return: 0 on success; -1 on failure.
        """
        self.DoPause()
        return 0

    def UpdateCurrentFrame(self, increment):
        """
        Increments current animation frame.

        :return: None.
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

    def UpdateOffsetLabel(self, key, state, frame):
        """
        Updates label for current (x,y) head offset.

        :param key:   Either of "head" or "body".
        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        label = "offset-{}".format(key)
        try:
            xy = self._Data[key]["current"]["offset"][state][frame]
            self._Labels[label].config(text=App.LABELS[label].format(*xy))
        except (KeyError, IndexError):
            self._Labels[label].config(text=App.LABELS[label].format(0, 0))

    def UpdateAnimationImage(self):
        """
        Updates currently-previewed animation frame.

        :return: None.
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

    def UpdateOffsetLabels(self):
        """
        Updates per-frame (x,y) head and body offset labels.

        :return: 0 on success; -1 on failure.
        """
        state = self._Animation["state"]
        frame = self._Animation["frame"]

        self.UpdateOffsetLabel("head", state, frame)
        self.UpdateOffsetLabel("body", state, frame)

        return 0

    def UpdateSpeed(self, speed):
        """
        Updates current animation speed.

        :param speed: New framerate.

        :return: 0 on success; -1 on failure.
        """
        speed = int(speed)
        text = App.LABELS["speed-anim"].format(speed)

        self._Labels["speed-anim"].config(text=text)
        self._Animation["speed"] = speed

        return 0


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
