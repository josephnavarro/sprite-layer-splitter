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
    CONFIRM_REBUILD_BDAT = "Refresh list of available bodies?"
    CONFIRM_REBUILD_BIMG = "Remake source images for body sprites?"
    CONFIRM_REBUILD_BOFF = "Refresh body sprite offsets?"
    CONFIRM_REBUILD_HDAT = "Refresh list of available heads?"
    CONFIRM_REBUILD_HIMG = "Remake source images for head sprites?"
    CONFIRM_REBUILD_HOFF = "Refresh head sprite offsets?"
    CONFIRM_DESTROY_HEAD = "Delete source images for head sprites?"
    CONFIRM_DESTROY_BODY = "Delete source images for body sprites?"
    MESSAGE_FAILURE_BODY = "Error: Body not specified!"
    MESSAGE_FAILURE_HEAD = "Error: Head not specified!"
    MESSAGE_FAILURE_TYPE = "Error: Invalid image format specified!"
    MESSAGE_INVALID_BODY = "Error: Body spritesheet '{}' does not exist!"
    MESSAGE_INVALID_HEAD = "Error: Head spritesheet '{}' does not exist!"
    MESSAGE_REBUILD_BIMG = "Successfully reconstructed body source images."
    MESSAGE_REBUILD_BDAT = "Reassembled list of available bodies."
    MESSAGE_REBUILD_BOFF = "Successfully reloaded per-frame body offsets."
    MESSAGE_REBUILD_HIMG = "Successfully reconstructed head source images."
    MESSAGE_REBUILD_HDAT = "Reassembled list of available heads."
    MESSAGE_REBUILD_HOFF = "Successfully reloaded per-frame head offsets."
    MESSAGE_DESTROY_HEAD = "Completely deleted all head sources."
    MESSAGE_DESTROY_BODY = "Completely deleted all body sources."
    MESSAGE_SUCCESS_FULL = "Sprite frames saved to {}!"
    MESSAGE_SUCCESS_IDLE = "Idle frames saved to {}!"

    # Default widget dimensions
    SIZES = {
        "preview-static": [384, 96],
        "preview-anim":   [96, 96],
        "preview-resize": [384, 96],
    }

    if IsWindows():
        # Windows
        SIZES["default-menu"] = [26, 0]
        SIZES["default-button"] = [27, 0]
        SIZES["default-slider"] = [272, 0]
        FONTSIZE_VARW = 13
        FONTSIZE_MONO = 10
        CANVAS_BORDER = 13
    else:
        # OS X / Linux
        SIZES["default-menu"] = [19, 0]
        SIZES["default-button"] = [22, 0]
        SIZES["default-slider"] = [272, 0]
        FONTSIZE_VARW = 13
        FONTSIZE_MONO = 14
        CANVAS_BORDER = 13

    # Grid positions for widgets
    GRID_SCALE_SPEED_PREVIEW = [4, 1]

    GRID = {
        "head-options":         [1, 0],
        "select-head":          [2, 0],
        "rebuild-head-images":  [3, 0],
        "rebuild-head-data":    [4, 0],
        "rebuild-head-offsets": [5, 0],
        "destroy-head-images":  [6, 0],

        "body-options":         [1, 1],
        "select-body":          [2, 1],
        "rebuild-body-images":  [3, 1],
        "rebuild-body-data":    [4, 1],
        "rebuild-body-offsets": [5, 1],
        "destroy-body-images":  [6, 1],

        "preview-options":      [1, 2],
        "preview-idle":         [2, 2],
        "preview-left":         [3, 2],
        "preview-right":        [4, 2],
        "pingpong-animation":   [5, 2],
        "reverse-layers":       [6, 2],

        "export-options":       [1, 3],
        "export-full":          [2, 3],
        "export-idle":          [3, 3],
        "prioritize-label":     [4, 3],
        "prioritize-1":         [5, 3],
        "prioritize-2":         [6, 3],

        "preview-static":       [0, 1],
        "preview-anim":         [0, 2],
        "frame-anim":           [0, 1],
        "offset-head":          [1, 1],
        "offset-body":          [2, 1],
        "speed-anim":           [3, 1],
    }

    # Padding for widgets
    PAD = {
        "export-full":          [4, 4],
        "export-idle":          [4, 4],
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
    }

    # Preview composition dimensions
    RECTS = {
        "idle":  [0, 0, 128, 32],
        "left":  [0, 32, 128, 32],
        "right": [0, 64, 128, 32],
    }

    # Button and menu text labels
    LABELS = {
        "export-options":       "Export",
        "export-full":          "Export all frames",
        "export-idle":          "Export idle frames",

        "preview-options":      "Preview",
        "preview-idle":         "Preview idle frames",
        "preview-left":         "Preview left frames",
        "preview-right":        "Preview right frames",
        "pingpong-animation":   "Ping-pong animation",
        "reverse-layers":       "Reverse layering order",

        "body-options":         "Body",
        "select-body":          "Select body",
        "rebuild-body-images":  "Remake body sources",
        "rebuild-body-data":    "Refresh body listing",
        "rebuild-body-offsets": "Refresh body offsets",
        "destroy-body-images":  "Clean body sources",

        "head-options":         "Head",
        "select-head":          "Select head",
        "rebuild-head-images":  "Remake head sources",
        "rebuild-head-data":    "Refresh head listing",
        "rebuild-head-offsets": "Refresh head offsets",
        "destroy-head-images":  "Clean head sources",

        "frame-anim":           "Frame: ({0:d})  {1:d}   {2:d}   {3:d}",
        "offset-body":          "Body:   x = {0:+d}; y = {1:+d}",
        "offset-head":          "Head:   x = {0:+d}; y = {1:+d}",
        "speed-anim":           "Speed:  {0:d}",

        "prioritize-label":     "On layer collision",
        "prioritize-1":         "Paste head first",
        "prioritize-2":         "Paste body first",
    }

    COLORS = {
        "export-full":          {"fg": [0, 0, 0], "bg": [244, 212, 248]},
        "export-idle":          {"fg": [0, 0, 0], "bg": [244, 212, 248]},
        "preview-idle":         {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "preview-left":         {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "preview-right":        {"fg": [0, 0, 0], "bg": [200, 255, 212]},
        "rebuild-body-data":    {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "rebuild-body-images":  {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "rebuild-body-offsets": {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "destroy-body-images":  {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "rebuild-head-data":    {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "rebuild-head-images":  {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "rebuild-head-offsets": {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "destroy-head-images":  {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "select-head":          {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "select-body":          {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "preview-static":       {"fg": [0, 0, 0], "bg": [0, 0, 0]},
        "preview-anim":         {"fg": [0, 0, 0], "bg": [0, 0, 0]},
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
        self._IsForwards = True
        self._HasInitAnim = False

        self._Animation = {
            "objects": [],
            "frame":   0,
            "speed":   0,
            "state":   STATES.idle,
        }

        self._Body = {
            "data":    {},
            "list":    [""],
            "offsets": {},
            "current": {},
        }

        self._Head = {
            "data":    {},
            "list":    [""],
            "offsets": {},
            "current": {},
        }

        # Frames
        self._FrameTopleft = tk.Frame(self._Master)
        self._FrameTopleft.grid(row=0, column=0)

        self._FrameTopRight = tk.Frame(self._FrameTopleft)
        self._FrameTopRight.grid(row=0, column=3)

        self._FrameTop = tk.Frame(self._FrameTopRight, width=1, height=10)
        self._FrameTop.grid(row=0, column=0)

        self._FrameBottom = tk.Frame(self._Master)
        self._FrameBottom.grid(row=2)

        self._FrameLast = tk.Frame(self._FrameBottom, height=10)
        self._FrameLast.grid(row=7)

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
                self._FrameBottom,
                self._StringVars["select-head"],
                *self._Head["list"]
            ),
            "select-body": tk.OptionMenu(
                self._FrameBottom,
                self._StringVars["select-body"],
                *self._Body["list"]
            ),
        }

        # Labels
        self._Labels = {
            "offset-head":      tk.Label(),
            "offset-body":      tk.Label(),
            "speed-anim":       tk.Label(),
            "frame-anim":       tk.Label(),
            "prioritize-label": tk.Label(),
            "head-options":     tk.Label(),
            "body-options":     tk.Label(),
            "preview-options":  tk.Label(),
            "export-options":   tk.Label(),
        }

        # Sliders
        self._ScaleAnimSpeed = tk.Scale()

        # Complete widget initialization
        self.InitDataHead()
        self.InitDataBody()
        self.InitLabel(
            self._FrameBottom,
            "export-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )
        self.InitButton(
            self._FrameBottom,
            "export-idle",
            lambda: self.ExportFrames(idle_only=True),
        )
        self.InitButton(
            self._FrameBottom,
            "export-full",
            lambda: self.ExportFrames(),
        )
        self.InitPreviewStatic()
        self.InitPreviewAnim()
        self.InitSliderFramerate()
        self.InitLabel(
            self._FrameTopRight,
            "speed-anim",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0,
        )
        self.InitLabel(
            self._FrameTopRight,
            "frame-anim",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0, 1, 2, 3,
        )
        self.InitLabel(
            self._FrameTopRight,
            "offset-head",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0, 0,
        )
        self.InitLabel(
            self._FrameTopRight,
            "offset-body",
            ("Courier", App.FONTSIZE_MONO),
            tk.W, 0, 0,
        )
        self.InitLabel(
            self._FrameBottom,
            "preview-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )
        self.InitButton(
            self._FrameBottom,
            "preview-idle",
            self.MakeIdlePreview,
        )
        self.InitButton(
            self._FrameBottom,
            "preview-left",
            self.MakeLeftPreview,
        )
        self.InitButton(
            self._FrameBottom,
            "preview-right",
            self.MakeRightPreview,
        )
        self.InitLabel(
            self._FrameBottom,
            "body-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )
        self.InitButton(
            self._FrameBottom,
            "rebuild-body-data",
            self.RebuildBodyData,
        )
        self.InitButton(
            self._FrameBottom,
            "rebuild-body-images",
            self.RebuildBodyImages,
        )
        self.InitButton(
            self._FrameBottom,
            "rebuild-body-offsets",
            self.RebuildBodyOffsets,
        )
        self.InitButton(
            self._FrameBottom,
            "destroy-body-images",
            self.DestroyBodyImages,
        )
        self.InitLabel(
            self._FrameBottom,
            "head-options",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )
        self.InitButton(
            self._FrameBottom,
            "rebuild-head-data",
            self.RebuildHeadData,
        )
        self.InitButton(
            self._FrameBottom,
            "rebuild-head-images",
            self.RebuildHeadImages,
        )
        self.InitButton(
            self._FrameBottom,
            "rebuild-head-offsets",
            self.RebuildHeadOffsets,
        )
        self.InitButton(
            self._FrameBottom,
            "destroy-head-images",
            self.DestroyHeadImages,
        )
        self.InitMenu(
            self._FrameBottom,
            "select-head",
            self._Head["list"],
        )
        self.InitMenu(
            self._FrameBottom,
            "select-body",
            self._Body["list"],
        )
        self.InitCheckbox(
            self._FrameBottom,
            "pingpong-animation",
            tk.NS,
        )
        self.InitCheckbox(
            self._FrameBottom,
            "reverse-layers",
            tk.NS,
        )
        self.InitLabel(
            self._FrameBottom,
            "prioritize-label",
            ("sans-serif", App.FONTSIZE_VARW, "bold"),
            tk.NS,
        )
        self.InitRadio(
            self._FrameBottom,
            "prioritize-1",
            self._StringVars["prioritize"],
            "Head",
            tk.NS,
            select=True,
        )
        self.InitRadio(
            self._FrameBottom,
            "prioritize-2",
            self._StringVars["prioritize"],
            "Body",
            tk.NS,
        )

        # Kill iTunes instance on Mac (if any)
        if IsOSX():
            self.KillITunes()

    def DoAnimate(self):
        """
        Local animation callback function.

        :return: None
        """
        self.UpdateCurrentFrame()
        self.UpdateOffsetLabels()

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

        # Repeat if animation is active
        speed = self._Animation["speed"]
        if speed > 0:
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
                App.MESSAGE_FAILURE_HEAD,
            )
        except UnspecifiedBodyException:
            # Body not specified
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGE_FAILURE_BODY,
            )
        except InvalidHeadException as e:
            # Head spritesheet does not exist
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGE_INVALID_HEAD.format(e.filename),
            )
        except InvalidBodyException as e:
            # Body spritesheet does not exist
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGE_INVALID_BODY.format(e.filename),
            )

        return headKey, bodyKey, None

    def Export(self, func, message, **kwargs):
        """
        Composites and exports all frames to file.

        :param func:    Frame compositing callback function.
        :param message: Success message.

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
                    message = message.format(os.path.basename(path))
                    tk.messagebox.showinfo(App.WINDOW_TITLE, message)

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                App.WINDOW_TITLE,
                App.MESSAGE_FAILURE_TYPE,
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
            message = App.MESSAGE_SUCCESS_IDLE
        else:
            message = App.MESSAGE_SUCCESS_FULL

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
            self._FrameTopleft,
            "preview-anim",
            App.CANVAS_BORDER,
        )

    def InitButton(self, master, tag, command):
        """
        Locally initializes a button.

        :param master:  Tkinter root frame for button.
        :param tag:     Tag of button to initialize.
        :param command: Callback function for button.

        :return: None.
        """
        width = App.SIZES["default-button"][0]  # Button width
        foreground = App.FromRGB(*App.COLORS[tag]["fg"])  # FG color
        background = App.FromRGB(*App.COLORS[tag]["bg"])  # BG color

        button = tk.Button(
            master,
            text=App.LABELS[tag],
            command=command,
        )
        button.config(
            width=width,
            foreground=foreground,
            background=background,
            activebackground=background,
            activeforeground=foreground,
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

        self._Labels[tag].destroy()
        self._Labels[tag] = tk.Label(
            master,
            font=font,
            text=text,
        )
        self._Labels[tag].grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
        )

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
        self._Menus[tag].destroy()
        self._Menus[tag] = tk.OptionMenu(
            master,
            self._StringVars[tag],
            *options
        )
        self._Menus[tag].config(
            width=width,
            foreground=foreground,
            background=background,
            activebackground=background,
            activeforeground=foreground,
        )
        self._Menus[tag].grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            padx=App.PAD[tag][0],
            pady=App.PAD[tag][1],
        )

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
        self._RadioButtons[tag].destroy()
        self._RadioButtons[tag] = tk.Radiobutton(
            master,
            text=App.LABELS[tag],
            variable=variable,
            value=value,
        )
        self._RadioButtons[tag].grid(
            row=App.GRID[tag][0],
            column=App.GRID[tag][1],
            sticky=sticky,
        )

        if select:
            self._RadioButtons[tag].select()
        else:
            self._RadioButtons[tag].deselect()

    def InitSliderFramerate(self):
        """
        Completes initialization of framerate slider.

        :return: None.
        """
        self._ScaleAnimSpeed.destroy()
        self._ScaleAnimSpeed = tk.Scale(
            self._FrameTopRight,
            from_=App.SPEED_SCALE_MIN,
            to=App.SPEED_SCALE_MAX,
            orient=tk.HORIZONTAL,
            length=App.SIZES["default-slider"][0],
            showvalue=0,
            command=self.UpdateSpeed,
        )
        self._ScaleAnimSpeed.grid(
            row=App.GRID_SCALE_SPEED_PREVIEW[0],
            column=App.GRID_SCALE_SPEED_PREVIEW[1],
            sticky=tk.W,
            pady=4,
        )

    def InitPreviewStatic(self):
        """
        Initializes static image preview canvas.

        :return: None.
        """
        self._ImageObject = None  ## !!
        self.InitCanvas(
            self._FrameTopleft,
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
        frame1 = sprite_imaging.Crop(image, [w * 0, 0], [w, h])
        frame2 = sprite_imaging.Crop(image, [w * 1, 0], [w, h])
        frame3 = sprite_imaging.Crop(image, [w * 2, 0], [w, h])
        frame4 = sprite_imaging.Crop(image, [w * 3, 0], [w, h])

        self._Animation["objects"] = [
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame1)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame2)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame3)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame4)),
        ]

        # Reset animation counters
        self._Animation["frame"] = 0
        self._IsForwards = True
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

        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 0, 92, "(0)")
        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 1, 92, "(1)")
        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 2, 92, "(2)")
        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 3, 92, "(3)")

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
                                App.RECTS[state][2:4]),
                            cv2.COLOR_BGR2RGB),
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
            tk.messagebox.showinfo(App.WINDOW_TITLE, App.MESSAGE_FAILURE_TYPE)

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
            headfirst=headfirst,
            reverse=reverse,
            idle_only=True,
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
            headfirst=headfirst,
            reverse=reverse,
        )

    def RebuildBodyData(self):
        """
        Rebuilds JSON database for body spritesheet filepaths.

        :return: None
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_BDAT

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateBodyJSON()
            self.InitDataBody()
            self.InitMenu(
                self._FrameBottom,
                "select-body",
                self._Body["list"],
            )

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_BDAT)

    # noinspection PyMethodMayBeStatic
    def RebuildBodyImages(self):
        """
        Callback function. Rebuilds intermediate body spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_BIMG

        if tk.messagebox.askquestion(title, query) == "yes":
            PrepareBody()
            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_BIMG)

    def RebuildBodyOffsets(self):
        """
        Callback function. Rebuilds body offset database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_BOFF

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

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_BOFF)

    # noinspection PyMethodMayBeStatic
    def DestroyBodyImages(self):
        """
        Callback function. Destroys intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_DESTROY_BODY

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushBodies()
            tk.messagebox.showinfo(title, App.MESSAGE_DESTROY_BODY)

    def RebuildHeadData(self):
        """
        Callback function. Rebuilds head JSON database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_HDAT

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateHeadJSON()
            self.InitDataHead()
            self.InitMenu(
                self._FrameBottom,
                "select-head",
                self._Head["list"],
            )

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_HDAT)

    # noinspection PyMethodMayBeStatic
    def RebuildHeadImages(self):
        """
        Callback function. Rebuilds intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_HIMG

        if tk.messagebox.askquestion(title, query) == "yes":
            PrepareHead()
            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_HIMG)

    def RebuildHeadOffsets(self):
        """
        Callback function. Rebuilds head offset database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_HOFF

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

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_HOFF)

    # noinspection PyMethodMayBeStatic
    def DestroyHeadImages(self):
        """
        Callback function. Destroys intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_DESTROY_HEAD

        if tk.messagebox.askquestion(title, query) == "yes":
            FlushHeads()
            tk.messagebox.showinfo(title, App.MESSAGE_DESTROY_HEAD)

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
        isForwards = self._IsForwards
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
        self._IsForwards = isForwards
        self._Animation["frame"] = curFrame

        # Update frame count label
        self.UpdateFrameCountLabel()

    def UpdateFrameCountLabel(self):
        """
        Updates label for currently-iterated frame.

        :return: None.
        """
        self._Labels["frame-anim"].config(
            text="Frame: " + " ".join([
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
            self._HasInitAnim = False
        else:
            if not self._HasInitAnim:
                self._HasInitAnim = True
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
