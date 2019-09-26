#! usr/bin/env python3
"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.

"""
import psutil
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
                "bdat": "Refresh list of available bodies?",
                "bimg": "Remake source images for body sprites?",
                "boff": "Refresh body sprite offsets?",
                "hdat": "Refresh list of available heads?",
                "himg": "Remake source images for head sprites?",
                "hoff": "Refresh head sprite offsets?",
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
                "bimg": "Succssfully reconstructed body source images.",
                "bdat": "Reassembled list of available bodies.",
                "boff": "Successfully reloaded per-frame body offsets.",
                "himg": "Successfully reconstructed head source images.",
                "hdat": "Reassembled list of available heads.",
                "hoff": "Successfully reloaded per-frame head offsets.",
            },
            "success": {
                "full": "Sprite frames saved to {}!",
                "idle": "Idle frames saved to {}!",
            }
        }
    }

    # Default widget dimensions
    SIZES = {
        "preview-anim":      [96, 96],
        "preview-resize":    [384, 96],
        "preview-static":    [384, 96],
        "play-button":       [32, 32],
        "pause-button":      [32, 32],
        "skip-right-button": [32, 32],
        "skip-left-button":  [32, 32],
        "shuffle-button":    [32, 32],
    }

    if IsWindows():
        # Windows
        SIZES["default-button"] = [36, 0]
        SIZES["default-menu"] = [37, 0]
        SIZES["default-slider"] = [256, 0]
        FONTSIZE_VARW = 13
        FONTSIZE_MONO = 10
        FONTSIZE_SMALL = 9
        CANVAS_BORDER = 13
    else:
        # OS X / Linux
        SIZES["default-button"] = [28, 0]
        SIZES["default-menu"] = [25, 0]
        SIZES["default-slider"] = [248, 0]
        FONTSIZE_VARW = 13
        FONTSIZE_MONO = 14
        FONTSIZE_SMALL = 9
        CANVAS_BORDER = 13

    GRID = {
        "preview-frames-label": [1, 1],
        "preview-anim-label":   [1, 2],

        "head-options":         [7, 0],
        "select-head":          [8, 0],
        "rebuild-head-images":  [9, 0],
        "rebuild-head-data":    [10, 0],
        "rebuild-head-offsets": [11, 0],
        "destroy-head-images":  [12, 0],

        "body-options":         [13, 0],
        "select-body":          [14, 0],
        "rebuild-body-images":  [15, 0],
        "rebuild-body-data":    [16, 0],
        "rebuild-body-offsets": [17, 0],
        "destroy-body-images":  [18, 0],

        "preview-options":      [7, 1],
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
        "preview-static":       [0, 1],
        "preview-anim":         [0, 2],
        "speed-slider":         [1, 0],
        "speed-anim":           [2, 0],
        "frame-anim":           [3, 0],
        "offset-head":          [4, 0],
        "offset-body":          [5, 0],

        "play-button":          [0, 1],
        "pause-button":         [0, 2],
        "skip-left-button":     [0, 3],
        "skip-right-button":    [0, 4],
        "shuffle-button":       [0, 5],
    }

    # Padding for widgets
    PAD = {
        "preview-frames-label": [0, 0],
        "preview-anim-label":   [0, 0],

        "export-full":          [4, 4],
        "export-idle":          [4, 4],
        "export-options":       [4, 4],

        "speed-anim":           [12, 0],
        "frame-anim":           [12, 0],

        "offset-head":          [12, 0],
        "offset-body":          [12, 0],

        "preview-options":      [4, 4],
        "body-options":         [4, 4],
        "head-options":         [4, 4],

        "prioritize-label":     [4, 4],
        "prioritize-1":         [0, 0],
        "prioritize-2":         [0, 0],

        "preview-idle":         [4, 4],
        "preview-left":         [4, 4],
        "preview-right":        [4, 4],

        "rebuild-body-data":    [4, 4],
        "rebuild-head-data":    [4, 4],
        "rebuild-body-images":  [4, 4],
        "rebuild-head-images":  [4, 4],
        "rebuild-body-offsets": [4, 4],
        "rebuild-head-offsets": [4, 4],

        "select-body":          [4, 4],
        "select-head":          [4, 4],

        "destroy-body-images":  [4, 4],
        "destroy-head-images":  [4, 4],

        "pingpong-animation":   [4, 0],
        "reverse-layers":       [4, 0],

        "play-button":          [0, 0],
        "pause-button":         [0, 0],
        "skip-left-button":     [0, 0],
        "skip-right-button":    [0, 0],
        "shuffle-button":       [0, 0],
    }

    # Preview composition dimensions
    RECTS = {
        "idle":  [0, 0, 128, 32],
        "left":  [0, 32, 128, 32],
        "right": [0, 64, 128, 32],
    }

    # Button and menu text labels
    LABELS = {
        "preview-frames-label": "Static frame preview",
        "preview-anim-label":   "Animated preview",

        "export-options":       "Export options",
        "export-full":          "Export all frames",
        "export-idle":          "Export idle frames",

        "preview-options":      "Preview options",
        "preview-idle":         "Preview idle frames",
        "preview-left":         "Preview left frames",
        "preview-right":        "Preview right frames",
        "pingpong-animation":   "Ping-pong animation",
        "reverse-layers":       "Reverse layering order",

        "body-options":         "Body options",
        "select-body":          "Select body",
        "rebuild-body-images":  "Remake body sources",
        "rebuild-body-data":    "Refresh body listing",
        "rebuild-body-offsets": "Refresh body offsets",
        "destroy-body-images":  "Clean body sources",

        "head-options":         "Head options",
        "select-head":          "Select head",
        "rebuild-head-images":  "Remake head sources",
        "rebuild-head-data":    "Refresh head listing",
        "rebuild-head-offsets": "Refresh head offsets",
        "destroy-head-images":  "Clean head sources",

        "frame-anim":           "Frame := ({0:d})  {1:d}   {2:d}   {3:d}",
        "offset-body":          "Body  :=  x: {0:+d} / y: {1:+d}",
        "offset-head":          "Head  :=  x: {0:+d} / y: {1:+d}",
        "speed-anim":           "Speed :=  {0:d}",

        "prioritize-label":     "On layer collision",
        "prioritize-1":         "Paste head first",
        "prioritize-2":         "Paste body first",

        "play-button":          "",
        "pause-button":         "",
        "skip-right-button":    "",
        "skip-left-button":     "",
        "shuffle-button":       "",
    }

    IMAGES = {
        "play-button":       os.path.join("misc", "play.png"),
        "pause-button":      os.path.join("misc", "pause.png"),
        "skip-right-button": os.path.join("misc", "forward.png"),
        "skip-left-button":  os.path.join("misc", "backward.png"),
        "shuffle-button":    os.path.join("misc", "shuffle.png"),
    }

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
        "select-head":          {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "select-body":          {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "preview-static":       {"fg": [0, 0, 0], "bg": [128, 128, 128]},
        "preview-anim":         {"fg": [0, 0, 0], "bg": [128, 128, 128]},
        "play-button":          {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "pause-button":         {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "skip-right-button":    {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "skip-left-button":     {"fg": [0, 0, 0], "bg": [222, 222, 222]},
        "shuffle-button":       {"fg": [0, 0, 0], "bg": [222, 222, 222]},
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
        font = "Courier {} bold".format(App.FONTSIZE_MONO)
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

        # Set icon for Mac OS X
        if IsOSX():
            image = tk.Image("photo", file="misc/icon.png")
            # noinspection PyProtectedMember
            root.tk.call("wm", "iconphoto", root._w, image)

        # Initialize local non-widget data
        self._ImageObject = None

        self._Animation = {
            "init":    False,
            "forward": True,
            "playing": False,
            "objects": [],
            "frame":   0,
            "speed":   6,
            "state":   STATES.idle,

        }

        self._Body = {
            "current": {},
            "data":    {},
            "list":    [""],
            "offsets": {},
        }

        self._Head = {
            "current": {},
            "data":    {},
            "list":    [""],
            "offsets": {},
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
            "select-head": tk.StringVar(self._Master),
            "select-body": tk.StringVar(self._Master),
            "prioritize":  tk.StringVar(self._Master),
        }

        # Buttons
        self._Buttons = {
            "export-idle":          tk.Button(),
            "export-full":          tk.Button(),
            "preview-idle":         tk.Button(),
            "preview-left":         tk.Button(),
            "preview-right":        tk.Button(),
            "rebuild-body-data":    tk.Button(),
            "rebuild-body-images":  tk.Button(),
            "rebuild-body-offsets": tk.Button(),
            "destroy-body-images":  tk.Button(),
            "rebuild-head-data":    tk.Button(),
            "rebuild-head-images":  tk.Button(),
            "rebuild-head-offsets": tk.Button(),
            "destroy-head-images":  tk.Button(),
            "play-button":          tk.Button(),
            "pause-button":         tk.Button(),
            "skip-right-button":    tk.Button(),
            "skip-left-button":     tk.Button(),
            "shuffle-button":       tk.Button(),
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
        }

        # Menus
        self._Menus = {
            "select-head": tk.OptionMenu(
                self._FrameGroupBot,
                self._StringVars["select-head"],
                *self._Head["list"]
            ),
            "select-body": tk.OptionMenu(
                self._FrameGroupBot,
                self._StringVars["select-body"],
                *self._Body["list"]
            ),
        }

        # Labels
        self._Labels = {
            "preview-frames-label": tk.Label(),
            "preview-anim-label":   tk.Label(),
            "offset-head":          tk.Label(),
            "offset-body":          tk.Label(),
            "speed-anim":           tk.Label(),
            "frame-anim":           tk.Label(),
            "prioritize-label":     tk.Label(),
            "head-options":         tk.Label(),
            "body-options":         tk.Label(),
            "preview-options":      tk.Label(),
            "export-options":       tk.Label(),
        }

        # Sliders
        self._ScaleAnimSpeed = tk.Scale()

        # Complete widget initialization
        self.InitDataHead()
        self.InitDataBody()

        self.InitLabel(
            self._FrameGroupBot,
            "export-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )

        self.InitButton(
            self._FrameGroupBot,
            "export-idle",
            lambda: self.ExportFrames(idle_only=True),
        )

        self.InitButton(
            self._FrameGroupBot,
            "export-full",
            lambda: self.ExportFrames(),
        )

        self.InitPreviewStatic()
        self.InitPreviewAnim()
        self.InitSliderFramerate()

        self.InitLabel(
            self._FrameBotLeft,
            "speed-anim",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0,
        )

        self.InitLabel(
            self._FrameGroupTop,
            "preview-frames-label",
            ("arial", App.FONTSIZE_SMALL),
            tk.W
        )

        self.InitLabel(
            self._FrameGroupTop,
            "preview-anim-label",
            ("arial", App.FONTSIZE_SMALL),
            tk.W
        )

        self.InitLabel(
            self._FrameBotLeft,
            "frame-anim",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0, 1, 2, 3,
        )

        self.InitLabel(
            self._FrameBotLeft,
            "offset-head",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0, 0,
        )

        self.InitLabel(
            self._FrameBotLeft,
            "offset-body",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0, 0,
        )

        self.InitLabel(
            self._FrameGroupBot,
            "preview-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )

        self.InitButton(
            self._FrameGroupBot,
            "preview-idle",
            self.MakeIdlePreview,
        )

        self.InitButton(
            self._FrameGroupBot,
            "preview-left",
            self.MakeLeftPreview,
        )

        self.InitButton(
            self._FrameGroupBot,
            "preview-right",
            self.MakeRightPreview,
        )

        self.InitLabel(
            self._FrameGroupBot,
            "body-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )

        self.InitButton(
            self._FrameGroupBot,
            "rebuild-body-data",
            self.RebuildBodyData,
        )

        self.InitButton(
            self._FrameGroupBot,
            "rebuild-body-images",
            self.RebuildBodyImages,
        )

        self.InitButton(
            self._FrameGroupBot,
            "rebuild-body-offsets",
            self.RebuildBodyOffsets,
        )

        self.InitButton(
            self._FrameGroupBot,
            "destroy-body-images",
            self.DestroyBodyImages,
        )

        self.InitLabel(
            self._FrameGroupBot,
            "head-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )

        self.InitButton(
            self._FrameGroupBot,
            "rebuild-head-data",
            self.RebuildHeadData,
        )

        self.InitButton(
            self._FrameGroupBot,
            "rebuild-head-images",
            self.RebuildHeadImages,
        )

        self.InitButton(
            self._FrameGroupBot,
            "rebuild-head-offsets",
            self.RebuildHeadOffsets,
        )

        self.InitButton(
            self._FrameGroupBot,
            "destroy-head-images",
            self.DestroyHeadImages,
        )

        self.InitButton(
            self._FrameBotRight,
            "play-button",
            self.TurnPlaybackOn,
        )

        self.InitButton(
            self._FrameBotRight,
            "pause-button",
            self.TurnPlaybackOff,
            relief=tk.SUNKEN,
        )

        self.InitButton(
            self._FrameBotRight,
            "skip-right-button",
            self.FrameForward,
        )

        self.InitButton(
            self._FrameBotRight,
            "skip-left-button",
            self.FrameBackward,
        )

        self.InitButton(
            self._FrameBotRight,
            "shuffle-button",
            None,
        )

        self.InitMenu(
            self._FrameGroupBot,
            "select-head",
            self._Head["list"],
        )

        self.InitMenu(
            self._FrameGroupBot,
            "select-body",
            self._Body["list"],
        )

        self.InitCheckbox(
            self._FrameGroupBot,
            "pingpong-animation",
            tk.W,
        )

        self.InitCheckbox(
            self._FrameGroupBot,
            "reverse-layers",
            tk.W,
        )

        self.InitLabel(
            self._FrameGroupBot,
            "prioritize-label",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )

        self.InitRadio(
            self._FrameGroupBot,
            "prioritize-1",
            self._StringVars["prioritize"],
            "Head",
            tk.W,
            select=True,
        )

        self.InitRadio(
            self._FrameGroupBot,
            "prioritize-2",
            self._StringVars["prioritize"],
            "Body",
            tk.W,
        )

        # Kill iTunes instance on Mac (if any)
        if IsOSX():
            self.KillITunes()

    def DoAnimate(self):
        """
        Local animation callback function.

        :return: None
        """
        isPlaying = self._Animation["playing"]
        speed = self._Animation["speed"]

        if isPlaying:
            self.UpdateCurrentFrame()

        self.UpdateOffsetLabels()
        self.UpdateAnimationImage()

        # Repeat if animation is active
        if speed > 0 and isPlaying:
            self.after(1000 // speed, self.DoAnimate)

    def DoComposite(self, func, **kwargs):
        """
        Performs a general-purpose image composition routine.

        :param func: Compositing function (CompositeIdle or CompositeFull)

        :return: Tuple of head key, body key, and numpy image.
        """
        headKey = ""
        bodyKey = ""

        try:
            try:
                # Get head key
                headName = self._StringVars["select-head"].get()
                if headName != App.DEFAULT_NAME:
                    headKey = self._Head["data"][headName]
            except KeyError:
                # raise UnspecifiedHeadException
                pass

            try:
                # Get body key
                bodyName = self._StringVars["select-body"].get()
                if bodyName != App.DEFAULT_NAME:
                    bodyKey = self._Body["data"][bodyName]
            except KeyError:
                # raise UnspecifiedBodyException
                pass

            try:
                # Perform sprite composition
                return headKey, bodyKey, func(headKey, bodyKey, **kwargs)
            except sprite_splitter.NonexistentHeadException as e:
                raise InvalidHeadException(e.filename)
            except sprite_splitter.NonexistentBodyException as e:
                raise InvalidBodyException(e.filename)
            except cv2.error:
                raise InvalidFilenameException

        except UnspecifiedHeadException:
            # Head not specified
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["failure"]["head"],
            )
        except UnspecifiedBodyException:
            # Body not specified
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["failure"]["body"],
            )
        except InvalidHeadException as e:
            # Head spritesheet does not exist
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["invalid"]["head"].format(e.filename),
            )
        except InvalidBodyException as e:
            # Body spritesheet does not exist
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["invalid"]["body"].format(e.filename),
            )

        return headKey, bodyKey, None

    def Export(self, func, message, **kwargs):
        """
        Composites and exports all frames to file.

        :param func:    Frame compositing callback function.
        :param message: Success message to display.

        :return: None.
        """
        try:
            # Perform sprite composition
            head, body, image = self.DoComposite(func, **kwargs)

            if image is not None:
                # Prompt user for destination filename
                FixPath(ROOT_OUTPUT_DIR)

                if not head and not body:
                    head = "blank"
                    body = "sheet"
                elif not head:
                    head = "body"
                elif not body:
                    body = "head"

                initialfile = "{}_{}.png".format(head, body)
                initialdir = ROOT_OUTPUT_DIR
                title = "Save As"
                filetypes = FILETYPES
                path = filedialog.asksaveasfilename(
                    initialfile=initialfile,
                    initialdir=initialdir,
                    title=title,
                    filetypes=filetypes,
                )
                if path:
                    # Save image if path is valid
                    sprite_splitter.SaveImage(image, path)
                    tk.messagebox.showinfo(
                        App.WINDOW_TITLE,
                        message.format(os.path.basename(path)),
                    )

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["failure"]["type"],
            )

        except EmptyFilenameException:
            # Filename not specified
            pass

    def ExportFrames(self, *, idle_only=False):
        """
        Composites and exports all frames to file.

        :param idle_only: Whether to export only idle frames. (Default False).

        :return: None.
        """
        reverse = self._BooleanVars["reverse-layers"].get()
        headfirst = self._StringVars["prioritize"].get() == "Head"

        if idle_only:
            message = App.MESSAGES["message"]["success"]["idle"]
        else:
            message = App.MESSAGES["message"]["success"]["full"]

        self.Export(
            sprite_splitter.Composite,
            message,
            headfirst=headfirst,
            reverse=reverse,
            idle_only=idle_only,
        )

    def InitPreviewAnim(self):
        """
        Initializes animated image preview canvas.

        :return: None.
        """
        self._Animation["objects"] = []
        self.InitCanvas(
            self._FrameGroupTop,
            "preview-anim",
            App.CANVAS_BORDER,
        )

    def InitButton(self, master, tag, command, relief=tk.RAISED):
        """
        Locally initializes a button.

        :param master:  Tkinter root frame for button.
        :param tag:     Tag of button to initialize.
        :param command: Callback function for button.
        :param relief:  Initial button relief. (Default tk.RAISED).

        :return: None.
        """
        size = App.SIZES.get(tag, App.SIZES["default-button"])
        width = size[0]  # Button width
        height = size[1]  # Button height
        foreground = App.FromRGB(*App.COLORS[tag]["fg"])  # FG color
        background = App.FromRGB(*App.COLORS[tag]["bg"])  # BG color

        # Image object
        path = App.IMAGES.get(tag, "")
        if path:
            image = sprite_imaging.OpenTkinter(path, width, height)
        else:
            image = None

        button = tk.Button(
            master,
            text=App.LABELS[tag],
            command=command,
        )

        button.image = image

        button.config(
            width=width,
            height=height,
            foreground=foreground,
            background=background,
            activebackground=background,
            activeforeground=foreground,
            image=image,
            relief=relief,
        )

        button.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

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
        canvas = tk.Canvas(
            master,
            width=App.SIZES[tag][0],
            height=App.SIZES[tag][1],
            background=App.FromRGB(*App.COLORS[tag]["bg"]),
            relief=tk.SUNKEN,
            borderwidth=border,
        )

        canvas.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
        )

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
        checkbox = tk.Checkbutton(
            master,
            text=App.LABELS[tag],
            variable=self._BooleanVars[tag],
        )

        checkbox.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        if command is not None:
            checkbox.config(command=command)

        self._Checkboxes[tag].destroy()
        self._Checkboxes[tag] = checkbox

    def InitDataBody(self):
        """
        Completes initialization of body data (from file).

        :return: None.
        """
        data = self._Body["data"] = {
            v.get("name", "---"): k
            for k, v in LoadBodyPaths().items()
        }

        self._Body["list"] = [App.DEFAULT_NAME] + sorted(list(data))
        self._Body["offsets"] = LoadBodyOffsets()

    def InitDataHead(self):
        """
        Completes initialization of head data (from file).

        :return: None.
        """
        data = self._Head["data"] = {
            v.get("name", "---"): k
            for k, v in LoadHeadPaths().items()
        }

        self._Head["list"] = [App.DEFAULT_NAME] + sorted(list(data))
        self._Head["offsets"] = LoadHeadOffsets()

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

        label = tk.Label(
            master,
            font=font,
            text=text,
        )
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

        menu = tk.OptionMenu(
            master,
            self._StringVars[tag],
            *options
        )
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

    def InitRadio(self, master, tag, variable, value, sticky, select=False):
        """
        Initializes a radio button.

        :param master:
        :param tag:
        :param variable:
        :param value:
        :param sticky:
        :param select:

        :return: None.
        """
        radio = tk.Radiobutton(
            master,
            text=App.LABELS[tag],
            variable=variable,
            value=value,
        )

        radio.grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

        if select:
            radio.select()
        else:
            radio.deselect()

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

    def InitPreviewStatic(self):
        """
        Initializes static image preview canvas.

        :return: None.
        """
        self._ImageObject = None  ## !!
        self.InitCanvas(
            self._FrameGroupTop,
            "preview-static",
            App.CANVAS_BORDER,
        )

    def MakeAnimationFrames(self, image):
        """
        Populates local animation buffer.

        :param image: Spritesheet to crop frames from.

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
        self._Animation["frame"] = 0
        self._Animation["forward"] = True
        self._Animation["speed"] = self._ScaleAnimSpeed.get()
        self._Canvases["preview-anim"].create_image(
            (16, 16),
            anchor=tk.NW,
            image=self._Animation["objects"][0],
        )

        self.UpdateOffsetLabels()
        self.UpdateFrameCountLabel()

    def MakeAnimationPreview(self, image):
        """
        Displays static preview frames.

        :param image: Image to display.

        :return: None.
        """
        self._ImageObject = sprite_imaging.ToTkinter(
            sprite_imaging.ToPIL(image))

        self._Canvases["preview-static"].create_image(
            (16, 16),
            anchor=tk.NW,
            image=self._ImageObject,
        )

        canvas = self._Canvases["preview-static"]
        for n in range(4):
            App.DrawText(canvas, 18 + 96 * n, 92, "({})".format(n))

    def MakePreview(self, func, state, **kwargs):
        """
        Generates a static preview image.

        :param func:  Compositing callback function to use.
        :param state: Named state of preview to generate.

        :return: None.
        """
        try:
            # Perform sprite composition
            self._Animation["state"] = state
            self._Head["offsets"] = LoadHeadOffsets()

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
                    self.MakeAnimationFrames(image)

                    try:
                        # Populate per-frame head offset data
                        self._Head["current"] = self._Head["offsets"][body]
                    except KeyError:
                        self._Head["current"] = {}

                    try:
                        # Populate per-frame body offset data
                        self._Body["current"] = self._Body["offsets"][body]
                    except KeyError:
                        self._Body["current"] = {}

                    self.UpdateOffsetLabels()

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGES["message"]["failure"]["type"],
            )

    def MakeIdlePreview(self):
        """
        Generates a preview image for current sprite's "idle" frames.

        :return: None
        """
        reverse = self._BooleanVars["reverse-layers"].get()
        headfirst = self._StringVars["prioritize"].get() == "Head"
        self.MakePreview(
            sprite_splitter.Composite,
            "idle",
            color=App.COLORS["preview-static"]["bg"],
            headfirst=headfirst,
            reverse=reverse,
        )

    def MakeLeftPreview(self):
        """
        Generates a preview image for current sprite's "left" frames.

        :return: None
        """
        reverse = self._BooleanVars["reverse-layers"].get()
        headfirst = self._StringVars["prioritize"].get() == "Head"
        self.MakePreview(
            sprite_splitter.Composite,
            "left",
            color=App.COLORS["preview-static"]["bg"],
            headfirst=headfirst,
            reverse=reverse,
        )

    def MakeRightPreview(self):
        """
        Generates a preview image for current sprite's "right" frames.

        :return: None
        """
        reverse = self._BooleanVars["reverse-layers"].get()
        headfirst = self._StringVars["prioritize"].get() == "Head"
        self.MakePreview(
            sprite_splitter.Composite,
            "right",
            color=App.COLORS["preview-static"]["bg"],
            headfirst=headfirst,
            reverse=reverse,
        )

    def RebuildBodyData(self):
        """
        Rebuilds JSON database for body spritesheet filepaths.

        :return: None
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["bdat"]

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateBodyJSON()
            self.InitDataBody()
            self.InitMenu(
                self._FrameGroupBot,
                "select-body",
                self._Body["list"],
            )

            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["rebuild"]["bdat"],
            )

    # noinspection PyMethodMayBeStatic
    def RebuildBodyImages(self):
        """
        Callback function. Rebuilds intermediate body spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["bimg"]

        if tk.messagebox.askquestion(title, query) == "yes":
            PrepareBody()
            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["rebuild"]["bimg"],
            )

    def RebuildBodyOffsets(self):
        """
        Callback function. Rebuilds body offset database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["boff"]

        if tk.messagebox.askquestion(title, query) == "yes":
            self._Body["offsets"] = LoadBodyOffsets()
            self.UpdateOffsetLabels()

            if self._Animation["objects"]:
                state = self._Animation["state"]
                if state == STATES.idle:
                    self.MakeIdlePreview()
                elif state == STATES.left:
                    self.MakeLeftPreview()
                elif state == STATES.right:
                    self.MakeRightPreview()

            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["rebuild"]["boff"],
            )

    # noinspection PyMethodMayBeStatic
    def DestroyBodyImages(self):
        """
        Callback function. Destroys intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["destroy"]["body"]

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushBodies()
            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["destroy"]["body"],
            )

    def RebuildHeadData(self):
        """
        Callback function. Rebuilds head JSON database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["hdat"]

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateHeadJSON()
            self.InitDataHead()
            self.InitMenu(
                self._FrameGroupBot,
                "select-head",
                self._Head["list"],
            )

            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["rebuild"]["hdat"],
            )

    # noinspection PyMethodMayBeStatic
    def RebuildHeadImages(self):
        """
        Callback function. Rebuilds intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["himg"]

        if tk.messagebox.askquestion(title, query) == "yes":
            PrepareHead()
            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["rebuild"]["himg"],
            )

    def RebuildHeadOffsets(self):
        """
        Callback function. Rebuilds head offset database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["rebuild"]["hoff"]

        if tk.messagebox.askquestion(title, query) == "yes":
            self._Head["offsets"] = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            if self._Animation["objects"]:
                state = self._Animation["state"]
                if state == STATES.idle:
                    self.MakeIdlePreview()
                elif state == STATES.left:
                    self.MakeLeftPreview()
                elif state == STATES.right:
                    self.MakeRightPreview()

            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["rebuild"]["hoff"],
            )

    # noinspection PyMethodMayBeStatic
    def DestroyHeadImages(self):
        """
        Callback function. Destroys intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.MESSAGES["confirm"]["destroy"]["head"]

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushHeads()
            tk.messagebox.showinfo(
                title,
                App.MESSAGES["message"]["destroy"]["head"],
            )

    # noinspection PyUnusedLocal
    def ToggleLayerOrder(self, event):
        """
        Callback function. Toggles sprite compositing layer order.

        :param event: Tkinter event.

        :return: None.
        """
        if self._Animation["objects"]:
            state = self._Animation["state"]
            if state == STATES.idle:
                self.MakeIdlePreview()
            elif state == STATES.left:
                self.MakeLeftPreview()
            elif state == STATES.right:
                self.MakeRightPreview()

    def TurnPlaybackOn(self):
        """
        Turns animation playing on.

        :return: None.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = True
            self._Buttons["pause-button"].config(relief=tk.RAISED)
            self._Buttons["play-button"].config(relief=tk.SUNKEN)
            self.DoAnimate()

    def TurnPlaybackOff(self):
        """
        Turns animation playing off.

        :return: None.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = False
            self._Buttons["pause-button"].config(relief=tk.SUNKEN)
            self._Buttons["play-button"].config(relief=tk.RAISED)

    def FrameForward(self):
        """
        Skips one frame to the right.

        Wraps around to the first frame if at the last one.

        :return: None.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = False
            self._Buttons["pause-button"].config(relief=tk.SUNKEN)
            self._Buttons["play-button"].config(relief=tk.RAISED)

            self._Animation["frame"] += 1
            if self._Animation["frame"] >= 4:
                self._Animation["frame"] = 0

            self.UpdateOffsetLabels()
            self.UpdateFrameCountLabel()
            self.UpdateAnimationImage()

    def FrameBackward(self):
        """
        Skips one frame to the left.

        Wraps around to the last frame if at the first one.

        :return: None.
        """
        if self._Animation["objects"]:
            self._Animation["playing"] = False
            self._Buttons["pause-button"].config(relief=tk.SUNKEN)
            self._Buttons["play-button"].config(relief=tk.RAISED)

            self._Animation["frame"] -= 1
            if self._Animation["frame"] < 0:
                self._Animation["frame"] = 3

            self.UpdateOffsetLabels()
            self.UpdateFrameCountLabel()
            self.UpdateAnimationImage()

    def UpdateBodyOffsetLabel(self, state, frame):
        """
        Updates label for current (x,y) body offset.

        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        try:
            self._Labels["offset-body"].config(
                text=App.LABELS["offset-body"].format(
                    *self._Body["current"]["offset"][state][frame]
                )
            )

        except (KeyError, IndexError):
            self._Labels["offset-body"].config(
                text=App.LABELS["offset-body"].format(0, 0)
            )

    def UpdateCurrentFrame(self):
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
        curFrame = self._Animation["frame"]
        if self._Animation["objects"]:
            if isForwards:
                # Forwards iteration
                curFrame += 1
                if curFrame >= 4:
                    if not isPingpong:
                        # Wrap to beginning
                        curFrame = 0
                    else:
                        # Switch iteration direction
                        curFrame = 2
                        isForwards = False
            else:
                # Backwards iteration
                curFrame -= 1
                if curFrame < 0:
                    # Switch iteration direction
                    curFrame = 1
                    isForwards = True

        # Update references to current frame
        self._Animation["forward"] = isForwards
        self._Animation["frame"] = curFrame

        # Update frame count label
        self.UpdateFrameCountLabel()

    def UpdateFrameCountLabel(self):
        """
        Updates label for currently-iterated frame.

        :return: None.
        """
        self._Labels["frame-anim"].config(
            text="Frame := " + " ".join([
                "({})".format(x)
                if x == self._Animation["frame"]
                else " {} ".format(x)
                for x in range(4)
            ])
        )

    def UpdateHeadOffsetLabel(self, state, frame):
        """
        Updates label for current (x,y) head offset.

        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        try:
            self._Labels["offset-head"].config(
                text=App.LABELS["offset-head"].format(
                    *self._Head["current"]["offset"][state][frame]
                )
            )

        except (KeyError, IndexError):
            self._Labels["offset-head"].config(
                text=App.LABELS["offset-head"].format(0, 0)
            )

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

        :return: None
        """
        state = self._Animation["state"]
        frame = self._Animation["frame"]
        self.UpdateHeadOffsetLabel(state, frame)
        self.UpdateBodyOffsetLabel(state, frame)

    def UpdateSpeed(self, speed):
        """
        Updates current animation speed.

        :param speed: New framerate.

        :return: None.
        """
        speed = int(speed)

        self._Labels["speed-anim"].config(
            text=App.LABELS["speed-anim"].format(speed)
        )
        self._Animation["speed"] = speed

        if speed == 0:
            self._Animation["init"] = False
        else:
            if not self._Animation["init"]:
                self._Animation["init"] = True
                self.DoAnimate()


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
