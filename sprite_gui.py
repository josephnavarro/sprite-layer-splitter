#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.

--------------------------------------------------------------------------------
"""
import cv2
import types
import numpy as np
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
    Exception thrown  when sprite composition is attempted while no head is
    selected.
    """
    pass


class App(tk.Frame):
    WINDOW_TITLE = "Fire Emblem 3DS Sprite Tool"

    # Popup message text content
    CONFIRM_REBUILD_BDAT = "Recheck body listing?"
    CONFIRM_REBUILD_BIMG = "Reconstruct body source images?"
    CONFIRM_REBUILD_BOFF = "Reload body offsets?"
    CONFIRM_REBUILD_HDAT = "Recheck head listing?"
    CONFIRM_REBUILD_HIMG = "Reconstruct head source images?"
    CONFIRM_REBUILD_HOFF = "Reload head offsets?"
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
    MESSAGE_SUCCESS_FULL = "Sprite frames saved to {}!"
    MESSAGE_SUCCESS_IDLE = "Idle frames saved to {}!"

    # Default widget dimensions
    if IsWindows():
        # Windows
        DEFAULT_OPTION_WIDTH = 26
        DEFAULT_BUTTON_WIDTH = 27
        DEFAULT_SLIDER_WIDTH = 272
    else:
        # OS X / Linux
        DEFAULT_OPTION_WIDTH = 19
        DEFAULT_BUTTON_WIDTH = 22
        DEFAULT_SLIDER_WIDTH = 280

    PREVIEW_CANVAS_SIZE = [384, 96]
    PREVIEW_ANIM_SIZE = [96, 96]

    # Default widget colors
    FG_COLOR_BUTTON_BODY = [0, 0, 0]
    FG_COLOR_BUTTON_HEAD = [0, 0, 0]
    FG_COLOR_BUTTON_PREV = [0, 0, 0]
    FG_COLOR_PREVIEW_CVS = [0, 0, 0]
    FG_COLOR_BUTTON_SAVE = [0, 0, 0]
    BG_COLOR_BUTTON_BODY = [255, 200, 200]
    BG_COLOR_BUTTON_HEAD = [200, 224, 255]
    BG_COLOR_BUTTON_PREV = [200, 255, 212]
    BG_COLOR_BUTTON_SAVE = [244, 212, 248]

    # Grid positions for widgets
    GRID_LABEL_FRAME_PREVIEW = [0, 1]
    GRID_LABEL_HEAD_XYOFFSET = [1, 1]
    GRID_LABEL_BODY_XYOFFSET = [2, 1]
    GRID_LABEL_SPEED_PREVIEW = [3, 1]
    GRID_SCALE_SPEED_PREVIEW = [4, 1]
    GRID_CHECK_ANIM_PINGPONG = [1, 2]
    GRID_CHECK_LAYER_REVERSE = [1, 3]
    GRID_CANVAS_IMGS_PREVIEW = [0, 1]
    GRID_CANVAS_ANIM_PREVIEW = [0, 2]
    GRID_OPTIONS_SELECT_HEAD = [1, 0]

    GRID = {
        "export-full":          [3, 3],
        "export-idle":          [2, 3],
        "preview-idle":         [2, 2],
        "preview-left":         [3, 2],
        "preview-right":        [4, 2],
        "rebuild-body-data":    [3, 1],
        "rebuild-body-images":  [2, 1],
        "rebuild-body-offsets": [4, 1],
        "rebuild-head-data":    [3, 0],
        "rebuild-head-images":  [2, 0],
        "rebuild-head-offsets": [4, 0],
    }

    GRID_OPTIONS_SELECT_BODY = [1, 1]

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
    }

    PAD_OPTIONS_SELECT_BODY = [4, 4]
    PAD_OPTIONS_SELECT_HEAD = [4, 4]

    # Preview composition dimensions
    ORIG_PREVIEW_CROP_IDLE = [0, 0]
    ORIG_PREVIEW_CROP_LEFT = [0, 32]
    ORIG_PREVIEW_CROP_RIGH = [0, 64]
    SIZE_PREVIEW_CROP_IDLE = [128, 32]
    SIZE_PREVIEW_CROP_LEFT = [128, 32]
    SIZE_PREVIEW_CROP_RIGH = [128, 32]
    SIZE_PREVIEW_RESIZE_UP = (384, 96)

    # Button and menu text labels
    LABELS = {
        "export-full":          "Export all frames",
        "export-idle":          "Export idle frames",
        "preview-idle":         "Preview idle frames",
        "preview-left":         "Preview left frames",
        "preview-right":        "Preview right frames",
        "rebuild-body-data":    "Recheck body listing",
        "rebuild-body-images":  "Reconstruct body images",
        "rebuild-body-offsets": "Reload body offsets",
        "rebuild-head-data":    "Recheck head listing",
        "rebuild-head-images":  "Reconstruct head images",
        "rebuild-head-offsets": "Reload head offsets",
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
        "rebuild-head-data":    {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "rebuild-head-images":  {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "rebuild-head-offsets": {"fg": [0, 0, 0], "bg": [200, 224, 255]},
    }

    LABEL_CHECK_PINGPONG_ANIMATE = "Ping-pong animation"
    LABEL_CHECK_REVERSE_LAYERING = "Reverse layering"
    LABEL_CURRENT_XY_HEAD_OFFSET = "Head: "
    LABEL_CURRENT_XY_BODY_OFFSET = "Body: "
    LABEL_MENU_CHOICES_HEAD_NULL = "Select head"
    LABEL_MENU_CHOICES_BODY_NULL = "Select body"

    # Animation speeds
    SPEED_SCALE_MIN = 0
    SPEED_SCALE_MAX = 12

    @staticmethod
    def DrawText(canvas, x, y, text) -> None:
        """
        Draws text to a given canvas.

        :param canvas: Canvas to modify.
        :param x:      Topleft x-coordinate to draw at.
        :param y:      Topleft y-coordinate to draw at.
        :param text:   Text to render.

        :return: None.
        """
        font: str = "Courier 14 bold"
        for m in range(-2, 3):
            for n in range(-2, 3):
                canvas.create_text(x + m, y + n,
                                   font=font,
                                   fill="black",
                                   text=text,
                                   anchor=tk.NW)

        canvas.create_text(x, y,
                           font=font,
                           fill="white",
                           text=text,
                           anchor=tk.NW)

    @staticmethod
    def FromRGB(r: int, g: int, b: int) -> str:
        """
        Returns a Tkinter-friendly color code from an RGB color tuple.

        :param r: Red channel (0-255)
        :param g: Green channel (0-255)
        :param b: Blue channel (0-255)

        :return:
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

        self.winfo_toplevel().title(self.WINDOW_TITLE)

        # Set icon for Mac OS X
        if IsOSX():
            image: tk.Image = tk.Image("photo", file="misc/icon.png")
            # noinspection PyProtectedMember
            root.tk.call("wm", "iconphoto", root._w, image)

        # Initialize local non-widget data
        self._AnimObjs = []
        self._ImageObj = None
        self._IsForward = True
        self._HasInitAnim = False
        self._CurFrame = 0
        self._CurSpeed = 0
        self._CurState = STATES[STATES.idle]

        self._BodyData = {}
        self._BodyList = [""]
        self._BodyOffsets = {}
        self._CurBody = {}

        self._HeadData = {}
        self._HeadList = [""]
        self._HeadOffsets = {}
        self._CurHead = {}

        self._BoolAnimPingPong = tk.BooleanVar()
        self._StrHeadOption = tk.StringVar(self._Master)
        self._StrBodyOption = tk.StringVar(self._Master)
        self._CanvStaticPreview = tk.Canvas(self._Master)
        self._CanvAnimPreview = tk.Canvas(self._Master)

        # Frames
        self._FrameTopleft = tk.Frame(self._Master)
        self._FrameTopRight = tk.Frame(self._FrameTopleft)
        self._FrameTop = tk.Frame(self._FrameTopRight, width=10, height=10)
        self._FrameBottom = tk.Frame(self._Master)

        self._FrameTopleft.grid(row=0, column=0)
        self._FrameTopRight.grid(row=0, column=3)
        self._FrameTop.grid(row=0, column=0)
        self._FrameBottom.grid(row=2)

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
            "rebuild-head-data":    tk.Button(),
            "rebuild-head-images":  tk.Button(),
            "rebuild-head-offsets": tk.Button(),
        }

        # Check buttons
        self._CheckAnimPingpong = tk.Checkbutton()
        self._CheckLayerReverse = tk.Checkbutton()

        # Menus
        self._MenuSelectHead = tk.OptionMenu(self._FrameBottom,
                                             self._StrHeadOption,
                                             *self._HeadList)

        self._MenuSelectBody = tk.OptionMenu(self._FrameBottom,
                                             self._StrBodyOption,
                                             *self._BodyList)

        # Labels
        self._LabelOffsetHead = tk.Label()
        self._LabelOffsetBody = tk.Label()
        self._LabelAnimSpeed = tk.Label()
        self._LabelAnimFrame = tk.Label()

        # Sliders
        self._ScaleAnimSpeed = tk.Scale()

        # Complete widget initialization
        self.InitHeadData()
        self.InitBodyData()
        self.InitButtonExportIdle()
        self.InitButtonExportFull()
        self.InitCanvasPreviews()
        self.InitSpeedWidgets()
        self.InitFrameReadout()
        self.InitOffsetLabels()
        self.InitButtonPreviewIdle()
        self.InitButtonPreviewLeft()
        self.InitButtonPreviewRight()
        self.InitButtonRebuildBodyData()
        self.InitButtonRebuildBodyImages()
        self.InitButtonRebuildBodyOffsets()
        self.InitButtonRebuildHeadData()
        self.InitButtonRebuildHeadImages()
        self.InitButtonRebuildHeadOffsets()
        self.InitOptionSelectHead()
        self.InitOptionSelectBody()
        self.InitCheckAnimPingpong()
        self.InitCheckLayerReverse()

    def DoAnimate(self) -> None:
        """
        Local animation callback function.

        :return: None
        """
        self.UpdateCurrentFrame()
        self.UpdateOffsetLabels()

        try:
            # Draw frame to canvas
            p: tuple = (16, 16)
            a: str = tk.NW
            i: tk.PhotoImage = self._AnimObjs[self._CurFrame]
            self._CanvAnimPreview.create_image(p, anchor=a, image=i)

            # FONT RENDERING IS EXPENSIVE!!!!!!!!!!!!!!!!!!!!
            # text: str = "({})".format(self._CurFrame)
            # App.DrawText(self._CanvAnimPreview, 18, 92, text)

        except IndexError:
            pass

        # Repeat if animation is active
        if self._CurSpeed > 0:
            self.after(1000 // self._CurSpeed, self.DoAnimate)

    def DoComposite(self, func) -> (str, str, (np.ndarray or None)):
        """
        Performs a general-purpose image composition routine.

        :param func: Compositing function (CompositeIdle or CompositeFull)

        :return: Tuple of head key, body key, and numpy image.
        """
        headKey: str = ""
        bodyKey: str = ""

        try:
            # Get head key
            try:
                headName: str = self._StrHeadOption.get()
                headKey: str = self._HeadData[headName]
            except KeyError:
                raise UnspecifiedHeadException

            # Get body key
            try:
                bodyName: str = self._StrBodyOption.get()
                bodyKey: str = self._BodyData[bodyName]
            except KeyError:
                raise UnspecifiedBodyException

            # Perform sprite composition
            try:
                return headKey, bodyKey, func(headKey, bodyKey)
            except sprite_splitter.NonexistentHeadException as e:
                raise InvalidHeadException(e.filename)
            except sprite_splitter.NonexistentBodyException as e:
                raise InvalidBodyException(e.filename)
            except cv2.error:
                raise InvalidFilenameException

        except UnspecifiedHeadException:
            # Head not specified
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_FAILURE_HEAD
            tk.messagebox.showinfo(title, message)

        except UnspecifiedBodyException:
            # Body not specified
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_FAILURE_BODY
            tk.messagebox.showinfo(title, message)

        except InvalidHeadException as e:
            # Head spritesheet does not exist
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_INVALID_HEAD.format(e.filename)
            tk.messagebox.showinfo(title, message)

        except InvalidBodyException as e:
            # Body spritesheet does not exist
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_INVALID_BODY.format(e.filename)
            tk.messagebox.showinfo(title, message)

        return headKey, bodyKey, None

    def ExportFrames(self, func, message) -> None:
        """
        Composites and exports all frames to file.

        :param func:
        :param message:

        :return: None.
        """
        try:
            # Perform sprite composition
            head, body, image = self.DoComposite(func)

            if image is not None:
                # Prompt user for destination filename
                FixPath(ROOT_OUTPUT_DIR)

                initialfile: str = "{}_{}.png".format(head, body)
                initialdir: str = ROOT_OUTPUT_DIR
                title: str = "Save As"
                filetypes: list = FILETYPES

                path: str = filedialog.asksaveasfilename(
                    initialfile=initialfile,
                    initialdir=initialdir,
                    title=title,
                    filetypes=filetypes,
                )

                if path:
                    # Save image if path is valid
                    sprite_splitter.SaveImage(image, path)

                    title: str = self.WINDOW_TITLE
                    name: str = os.path.basename(path)
                    message: str = message.format(name)
                    tk.messagebox.showinfo(title, message)

        except InvalidFilenameException:
            # Image format not recognized
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_FAILURE_TYPE
            tk.messagebox.showinfo(title, message)

        except EmptyFilenameException:
            # Filename not specified
            pass

    def ExportFullFrames(self) -> None:
        """
        Composites and exports all frames to file.

        :return: None.
        """
        func = sprite_splitter.CompositeFull
        message = self.MESSAGE_SUCCESS_FULL
        self.ExportFrames(func, message)

    def ExportIdleFrames(self) -> None:
        """
        Composites and exports idle frames to file.

        :return: None.
        """
        func = sprite_splitter.CompositeIdle
        message = self.MESSAGE_SUCCESS_IDLE
        self.ExportFrames(func, message)

    def InitAnimatedPreview(self) -> None:
        """
        Initializes animated image preview canvas.

        :return: None.
        """
        self._AnimObjs = []

        self._CanvAnimPreview.destroy()

        master: tk.Frame = self._FrameTopleft
        width: int = self.PREVIEW_ANIM_SIZE[0]
        height: int = self.PREVIEW_ANIM_SIZE[1]
        background: str = self.FromRGB(*self.FG_COLOR_PREVIEW_CVS)
        relief: str = tk.SUNKEN
        border: int = 13

        self._CanvAnimPreview = tk.Canvas(
            master,
            width=width,
            height=height,
            background=background,
            relief=relief,
            borderwidth=border,
        )

        row: int = self.GRID_CANVAS_ANIM_PREVIEW[0]  # Row
        col: int = self.GRID_CANVAS_ANIM_PREVIEW[1]  # Column

        self._CanvAnimPreview.grid(row=row, column=col)

    def InitButton(self, master, tag, cmd) -> None:
        """
        Initializes a specific local button.

        :param master: Tkinter root frame for button.
        :param tag:    Tag of button to initialize.
        :param cmd:    Callback function for button.

        :return: None.
        """
        self._Buttons[tag].destroy()

        text: str = App.LABELS[tag]
        self._Buttons[tag] = tk.Button(master, text=text, command=cmd)

        width: int = App.DEFAULT_BUTTON_WIDTH
        foreground: str = App.FromRGB(*App.COLORS[tag]["fg"])
        background: str = App.FromRGB(*App.COLORS[tag]["bg"])

        self._Buttons[tag].config(
            width=width,
            foreground=foreground,
            background=background,
            activebackground=background,
            activeforeground=foreground,
        )

        row: int = App.GRID[tag][0]  # Row
        col: int = App.GRID[tag][1]  # Column
        px: int = App.PAD[tag][0]  # Horizontal padding
        py: int = App.PAD[tag][1]  # Vertical padding

        self._Buttons[tag].grid(row=row, column=col, padx=px, pady=py)

    def InitCheckAnimPingpong(self) -> None:
        """
        Completes initialization of checkbox for toggling animation ping-pong.

        :return: None.
        """
        self._CheckAnimPingpong.destroy()

        mtr: tk.Frame = self._FrameBottom  # Master
        txt: str = self.LABEL_CHECK_PINGPONG_ANIMATE  # Text
        var: tk.BooleanVar = self._BoolAnimPingPong  # Variable
        row: int = self.GRID_CHECK_ANIM_PINGPONG[0]  # Row
        column: int = self.GRID_CHECK_ANIM_PINGPONG[1]  # Column
        sticky: str = tk.NS  # Sticky

        self._CheckAnimPingpong = tk.Checkbutton(mtr, text=txt, variable=var)
        self._CheckAnimPingpong.grid(row=row, column=column, sticky=sticky)

    def InitCheckLayerReverse(self):
        """

        :return: None.
        """
        return

    def InitBodyData(self):
        """
        Completes initialization of body data (from file).

        :return: None.
        """
        self._BodyData = {
            v.get("name", "---"): k
            for k, v in LoadBodyPaths().items()
        }

        self._BodyList = sorted(list(self._BodyData))
        self._BodyOffsets = LoadBodyOffsets()

    def InitBodyOffsetLabel(self) -> None:
        """
        Completes initialization of framewise (x,y) body offsets.

        :return: None.
        """
        self._LabelOffsetBody.destroy()

        master: tk.Frame = self._FrameTopRight
        label: str = self.LABEL_CURRENT_XY_BODY_OFFSET
        text: str = "{0:s} {1:+d}, {2:+d}".format(label, 0, 0)
        row: int = self.GRID_LABEL_BODY_XYOFFSET[0]
        col: int = self.GRID_LABEL_BODY_XYOFFSET[1]
        sticky: str = tk.W
        font: tuple = ("Courier", 14)

        self._LabelOffsetBody = tk.Label(master, font=font, text=text)
        self._LabelOffsetBody.grid(row=row, column=col, sticky=sticky)

    def InitButtonExportFull(self) -> None:
        """
        Completes initialization of "full composition" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "export-full", self.ExportFullFrames)

    def InitButtonExportIdle(self) -> None:
        """
        Completes initialization of "save idle frames" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "export-idle", self.ExportIdleFrames)

    def InitButtonPreviewIdle(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self.InitButton(self._FrameBottom, "preview-idle", self.MakeIdlePreview)

    def InitButtonPreviewLeft(self) -> None:
        """
        Completes initialization of "preview left" button.

        :return: None
        """
        self.InitButton(self._FrameBottom, "preview-left", self.MakeLeftPreview)

    def InitButtonPreviewRight(self) -> None:
        """
        Completes initialization of "preview right" button.

        :return: None
        """
        self.InitButton(self._FrameBottom, "preview-right", self.MakeRightPreview)

    def InitButtonRebuildBodyData(self) -> None:
        """
        Completes initialization of "rebuild body" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "rebuild-body-data", self.RebuildBodyData)

    def InitButtonRebuildBodyImages(self) -> None:
        """
        Completes initialization of "rebuild body intermediates" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "rebuild-body-images", self.RebuildBodyImages)

    def InitButtonRebuildBodyOffsets(self) -> None:
        """
        Completes initialization of "rebuild body offsets" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "rebuild-body-offsets", self.RebuildBodyOffsets)

    def InitButtonRebuildHeadData(self) -> None:
        """
        Completes initialization of "rebuild head" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "rebuild-head-data", self.RebuildHeadData)

    def InitButtonRebuildHeadImages(self) -> None:
        """
        Completes initialization of "rebuild head intermediates" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "rebuild-head-images", self.RebuildHeadImages)

    def InitButtonRebuildHeadOffsets(self) -> None:
        """
        Completes initialization of "rebuild head offsets" button.

        :return: None.
        """
        self.InitButton(self._FrameBottom, "rebuild-head-offsets", self.RebuildHeadOffsets)

    def InitCanvasPreviews(self) -> None:
        """
        Completes initialization of preview image canvas.

        :return: None.
        """
        self.InitStaticPreview()
        self.InitAnimatedPreview()

    def InitFrameReadout(self) -> None:
        """
        Completes initialization of current frame display.

        :return: None
        """
        self._LabelAnimFrame.destroy()

        master: tk.Frame = self._FrameTopRight
        text: str = "Frame: (0)  1   2   3"
        row: int = self.GRID_LABEL_FRAME_PREVIEW[0]
        col: int = self.GRID_LABEL_FRAME_PREVIEW[1]
        sticky: str = tk.W
        font: tuple = ("Courier", 14)

        self._LabelAnimFrame = tk.Label(master, font=font, text=text)
        self._LabelAnimFrame.grid(row=row, column=col, sticky=sticky)

    def InitHeadData(self) -> None:
        """
        Completes initialization of head data (from file).

        :return: None.
        """
        self._HeadData = {
            v.get("name", "---"): k
            for k, v in LoadHeadPaths().items()
        }

        self._HeadList = sorted(list(self._HeadData))
        self._HeadOffsets = LoadHeadOffsets()

    def InitHeadOffsetLabel(self) -> None:
        """
        Completes initialization of framewise (x,y) head offsets.

        :return: None.
        """
        self._LabelOffsetHead.destroy()

        master: tk.Frame = self._FrameTopRight
        label: str = self.LABEL_CURRENT_XY_HEAD_OFFSET
        text: str = "{0:s} {1:+d}, {2:+d}".format(label, 0, 0)
        row: int = self.GRID_LABEL_HEAD_XYOFFSET[0]
        column: int = self.GRID_LABEL_HEAD_XYOFFSET[1]
        sticky: str = tk.W
        font: tuple = ("Courier", 14)

        self._LabelOffsetHead = tk.Label(master, font=font, text=text)
        self._LabelOffsetHead.grid(row=row, column=column, sticky=sticky)

    def InitOffsetLabels(self) -> None:
        """
        Completes initialization of per-frame (x,y) offset labels.

        :return: None.
        """
        self.InitHeadOffsetLabel()
        self.InitBodyOffsetLabel()

    def InitOptionSelectHead(self) -> None:
        """
        Completes initialization of character head dropdown menu.

        :return: None.
        """
        self._StrHeadOption.set(self.LABEL_MENU_CHOICES_HEAD_NULL)

        self._MenuSelectHead.destroy()

        master: tk.Frame = self._FrameBottom
        label: tk.StringVar = self._StrHeadOption
        options: list = self._HeadList

        self._MenuSelectHead = tk.OptionMenu(master, label, *options)

        width: int = self.DEFAULT_OPTION_WIDTH
        fg: str = self.FromRGB(*self.FG_COLOR_BUTTON_HEAD)
        bg: str = self.FromRGB(*self.BG_COLOR_BUTTON_HEAD)

        self._MenuSelectHead.config(
            width=width,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_OPTIONS_SELECT_HEAD[0]  # Row
        col: int = self.GRID_OPTIONS_SELECT_HEAD[1]  # Column
        px: int = self.PAD_OPTIONS_SELECT_HEAD[0]  # Horizontal padding
        py: int = self.PAD_OPTIONS_SELECT_HEAD[1]  # Vertical padding

        self._MenuSelectHead.grid(row=row, column=col, padx=px, pady=py)

    def InitOptionSelectBody(self) -> None:
        """
        Completes initialization of character body dropdown menu.

        :return: None.
        """
        self._StrBodyOption.set(self.LABEL_MENU_CHOICES_BODY_NULL)

        self._MenuSelectBody.destroy()

        master: tk.Frame = self._FrameBottom
        text: tk.StringVar = self._StrBodyOption
        options: list = self._BodyList
        width: int = self.DEFAULT_OPTION_WIDTH
        fg: str = self.FromRGB(*self.FG_COLOR_BUTTON_BODY)
        bg: str = self.FromRGB(*self.BG_COLOR_BUTTON_BODY)

        self._MenuSelectBody = tk.OptionMenu(master, text, *options)

        self._MenuSelectBody.config(
            width=width,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_OPTIONS_SELECT_BODY[0]  # Row
        col: int = self.GRID_OPTIONS_SELECT_BODY[1]  # Column
        px: int = self.PAD_OPTIONS_SELECT_BODY[0]  # Horizontal padding
        py: int = self.PAD_OPTIONS_SELECT_BODY[1]  # Vertical padding

        self._MenuSelectBody.grid(row=row, column=col, padx=px, pady=py)

    def InitSpeedWidgets(self) -> None:
        """
        Completes initialization of framerate adjustment widgets.

        :return: None.
        """
        # Create speed label
        self._LabelAnimSpeed.destroy()

        master: tk.Frame = self._FrameTopRight
        text: str = "Speed: 0"
        row: int = self.GRID_LABEL_SPEED_PREVIEW[0]
        col: int = self.GRID_LABEL_SPEED_PREVIEW[1]
        sticky: str = tk.W
        font: tuple = ("Courier", 14)

        self._LabelAnimSpeed = tk.Label(master, font=font, text=text)
        self._LabelAnimSpeed.grid(row=row, column=col, sticky=sticky)

        # Create speed scale
        self._ScaleAnimSpeed.destroy()

        master: tk.Frame = self._FrameTopRight
        from_: int = self.SPEED_SCALE_MIN
        to: int = self.SPEED_SCALE_MAX
        orient: str = tk.HORIZONTAL
        length: int = self.DEFAULT_SLIDER_WIDTH
        showvalue: int = 0
        cmd: types.FunctionType = self.UpdateSpeed

        self._ScaleAnimSpeed = tk.Scale(
            master,
            from_=from_,
            to=to,
            orient=orient,
            length=length,
            showvalue=showvalue,
            command=cmd,
        )

        row: int = self.GRID_SCALE_SPEED_PREVIEW[0]
        col: int = self.GRID_SCALE_SPEED_PREVIEW[1]
        sticky: str = tk.W

        self._ScaleAnimSpeed.grid(row=row, column=col, sticky=sticky, pady=4)

    def InitStaticPreview(self) -> None:
        """
        Initializes static image preview canvas.

        :return: None.
        """
        self._ImageObj = None

        self._CanvStaticPreview.destroy()

        master: tk.Frame = self._FrameTopleft
        width: int = self.PREVIEW_CANVAS_SIZE[0]
        height: int = self.PREVIEW_CANVAS_SIZE[1]
        bg: str = self.FromRGB(*self.FG_COLOR_PREVIEW_CVS)
        relief: str = tk.SUNKEN
        border: int = 13

        self._CanvStaticPreview = tk.Canvas(
            master,
            width=width,
            height=height,
            background=bg,
            relief=relief,
            borderwidth=border,
        )

        row: int = self.GRID_CANVAS_IMGS_PREVIEW[0]  # Row
        col: int = self.GRID_CANVAS_IMGS_PREVIEW[1]  # Column

        self._CanvStaticPreview.grid(row=row, column=col)

    def MakeAnimationFrames(self, image) -> None:
        """
        Populates local animation buffer.

        :param image: Spritesheet to crop frames from.

        :return: None
        """
        # Get animation frames
        w, h = self.PREVIEW_ANIM_SIZE[0], self.PREVIEW_ANIM_SIZE[1]
        frame1 = sprite_imaging.Crop(image, [w * 0, 0], [w, h])
        frame2 = sprite_imaging.Crop(image, [w * 1, 0], [w, h])
        frame3 = sprite_imaging.Crop(image, [w * 2, 0], [w, h])
        frame4 = sprite_imaging.Crop(image, [w * 3, 0], [w, h])

        self._AnimObjs = [
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame1)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame2)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame3)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame4)),
        ]

        # Reset animation counters
        self._CurFrame: int = 0
        self._IsForward: bool = True
        self._CurSpeed: str = self._ScaleAnimSpeed.get()

        # Draw first frame to animation canvas
        pos: tuple = (16, 16)
        anchor: str = tk.NW
        im: tk.PhotoImage = self._AnimObjs[0]

        self._CanvAnimPreview.create_image(pos, anchor=anchor, image=im)

        # FONT RENDERING IS EXPENSIVE!!!!!!!!!!!!!!!!!!!!!!!
        # text: str = "({})".format(self._CurFrame)
        # App.DrawText(self._CanvAnimPreview, 18, 92, text)

    def MakeAnimationPreview(self, image) -> None:
        """
        Displays animation preview frames.

        :param image: Image to display.

        :return: None.
        """
        self._ImageObj = sprite_imaging.ToTkinter(sprite_imaging.ToPIL(image))

        pos: tuple = (16, 16)
        anchor: str = tk.NW
        im: tk.PhotoImage = self._ImageObj

        self._CanvStaticPreview.create_image(pos, anchor=anchor, image=im)

        App.DrawText(self._CanvStaticPreview, 18 + 96 * 0, 92, "(0)")
        App.DrawText(self._CanvStaticPreview, 18 + 96 * 1, 92, "(1)")
        App.DrawText(self._CanvStaticPreview, 18 + 96 * 2, 92, "(2)")
        App.DrawText(self._CanvStaticPreview, 18 + 96 * 3, 92, "(3)")

    def MakeIdlePreview(self) -> None:
        """
        Generates a preview image for current sprite's "idle" frames.

        :return: None
        """
        try:
            # Perform sprite composition
            self._HeadOffsets = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            head, body, image = self.DoComposite(sprite_splitter.CompositeIdle)

            if image is not None:
                try:
                    # Crop idle frames from source spritesheet
                    start: list = self.ORIG_PREVIEW_CROP_IDLE
                    size: list = self.SIZE_PREVIEW_CROP_IDLE
                    dsize: tuple = self.SIZE_PREVIEW_RESIZE_UP
                    interp: int = cv2.INTER_NEAREST

                    image = sprite_imaging.Crop(image, start, size)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image = cv2.resize(image, dsize=dsize, interpolation=interp)

                    # Set static and animated previews
                    self.MakeAnimationPreview(image)
                    self.MakeAnimationFrames(image)

                    # Set current state
                    self._CurState = STATES[STATES.idle]
                    try:
                        # Populate per-frame head offset data
                        body_name: str = self._StrBodyOption.get()
                        body_key: str = self._BodyData[body_name]
                        self._CurHead = self._HeadOffsets[body_key]
                    except KeyError:
                        self._CurHead = {}

                    try:
                        # Populate per-frame body offset data
                        body_name: str = self._StrBodyOption.get()
                        body_key: str = self._BodyData[body_name]
                        self._CurBody = self._BodyOffsets[body_key]
                    except KeyError:
                        self._CurBody = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_FAILURE_TYPE
            tk.messagebox.showinfo(title, message)

    def MakeLeftPreview(self) -> None:
        """
        Generates a preview image for current sprite's "left" frames.

        :return: None
        """
        try:
            # Perform sprite composition
            self._HeadOffsets = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            head, body, image = self.DoComposite(sprite_splitter.CompositeFull)

            if image is not None:
                try:
                    # Crop left-facing frames from source spritesheet
                    start: list = self.ORIG_PREVIEW_CROP_LEFT
                    size: list = self.SIZE_PREVIEW_CROP_LEFT
                    dsize: tuple = self.SIZE_PREVIEW_RESIZE_UP
                    interp: int = cv2.INTER_NEAREST

                    image = sprite_imaging.Crop(image, start, size)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image = cv2.resize(image, dsize=dsize, interpolation=interp)

                    # Set static and animated previews
                    self.MakeAnimationPreview(image)
                    self.MakeAnimationFrames(image)

                    # Set current state
                    self._CurState = STATES[STATES.left]
                    try:
                        # Populate per-frame head offset data
                        bodyName: str = self._StrBodyOption.get()
                        bodyKey: str = self._BodyData[bodyName]
                        self._CurHead = self._HeadOffsets[bodyKey]
                    except KeyError:
                        self._CurHead = {}

                    try:
                        # Populate per-frame body offset data
                        bodyName: str = self._StrBodyOption.get()
                        bodyKey: str = self._BodyData[bodyName]
                        self._CurBody = self._BodyOffsets[bodyKey]
                    except KeyError:
                        self._CurBody = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_FAILURE_TYPE
            tk.messagebox.showinfo(title, message)

    def MakeRightPreview(self) -> None:
        """
        Generates a preview image for current sprite's "right" frames.

        :return: None
        """
        try:
            # Perform sprite composition
            self._HeadOffsets = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            head, body, image = self.DoComposite(sprite_splitter.CompositeFull)

            if image is not None:
                try:
                    # Crop right-facing frames from source spritesheet
                    start: list = self.ORIG_PREVIEW_CROP_RIGH
                    size: list = self.SIZE_PREVIEW_CROP_RIGH
                    dsize: tuple = self.SIZE_PREVIEW_RESIZE_UP
                    interp: int = cv2.INTER_NEAREST

                    image = sprite_imaging.Crop(image, start, size)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image = cv2.resize(image, dsize=dsize, interpolation=interp)

                    # Set static and animated previews
                    self.MakeAnimationPreview(image)
                    self.MakeAnimationFrames(image)

                    # Set current state
                    self._CurState = STATES[STATES.right]

                    try:
                        # Populate per-frame head offset data
                        bodyName: str = self._StrBodyOption.get()
                        bodyKey: str = self._BodyData[bodyName]
                        self._CurHead = self._HeadOffsets[bodyKey]
                    except KeyError:
                        self._CurHead = {}

                    try:
                        # Populate per-frame body offset data
                        bodyName: str = self._StrBodyOption.get()
                        bodyKey: str = self._BodyData[bodyName]
                        self._CurBody = self._BodyOffsets[bodyKey]
                    except KeyError:
                        self._CurBody = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            title: str = self.WINDOW_TITLE
            message: str = self.MESSAGE_FAILURE_TYPE
            tk.messagebox.showinfo(title, message)

    def RebuildBodyData(self) -> None:
        """
        Rebuilds JSON database for body spritesheet filepaths.

        :return: None
        """
        title: str = self.WINDOW_TITLE
        query: str = self.CONFIRM_REBUILD_BDAT

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateBodyJSON()

            self.InitBodyData()
            self.InitOptionSelectBody()

            message: str = self.MESSAGE_REBUILD_BDAT
            tk.messagebox.showinfo(title, message)

    def RebuildBodyImages(self) -> None:
        """
        Rebuilds intermediate body spritesheets.

        :return: None.
        """
        title: str = self.WINDOW_TITLE
        message: str = self.CONFIRM_REBUILD_BIMG

        if tk.messagebox.askquestion(title, message) == "yes":
            PrepareBody()

            message = self.MESSAGE_REBUILD_BIMG
            tk.messagebox.showinfo(title, message)

    def RebuildBodyOffsets(self) -> None:
        """
        Rebuilds body offset database.

        :return: None.
        """
        title: str = App.WINDOW_TITLE
        message: str = App.CONFIRM_REBUILD_BOFF

        if tk.messagebox.askquestion(title, message) == "yes":
            self._BodyOffsets = LoadBodyOffsets()
            self.UpdateOffsetLabels()

            if self._AnimObjs:
                if self._CurState == STATES[STATES.idle]:
                    self.MakeIdlePreview()
                elif self._CurState == STATES[STATES.left]:
                    self.MakeLeftPreview()
                elif self._CurState == STATES[STATES.right]:
                    self.MakeRightPreview()

            message = App.MESSAGE_REBUILD_BOFF
            tk.messagebox.showinfo(title, message)

    def RebuildHeadData(self) -> None:
        """
        Rebuilds head JSON database.

        :return: None.
        """
        title: str = self.WINDOW_TITLE
        message: str = self.CONFIRM_REBUILD_HDAT

        if tk.messagebox.askquestion(title, message) == "yes":
            CreateHeadJSON()

            self.InitHeadData()
            self.InitOptionSelectHead()

            message = self.MESSAGE_REBUILD_HDAT
            tk.messagebox.showinfo(title, message)

    def RebuildHeadImages(self) -> None:
        """
        Rebuilds intermediate head spritesheets.

        :return: None.
        """
        title: str = App.WINDOW_TITLE
        message: str = App.CONFIRM_REBUILD_HIMG

        if tk.messagebox.askquestion(title, message) == "yes":
            PrepareHead()

            message = self.MESSAGE_REBUILD_HIMG
            tk.messagebox.showinfo(title, message)

    def RebuildHeadOffsets(self) -> None:
        """
        Rebuilds head offset database.

        :return: None.
        """
        title: str = App.WINDOW_TITLE
        message: str = App.CONFIRM_REBUILD_HOFF

        if tk.messagebox.askquestion(title, message) == "yes":
            self._HeadOffsets = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            if self._AnimObjs:
                if self._CurState == STATES[STATES.idle]:
                    self.MakeIdlePreview()
                elif self._CurState == STATES[STATES.left]:
                    self.MakeLeftPreview()
                elif self._CurState == STATES[STATES.right]:
                    self.MakeRightPreview()

            message = App.MESSAGE_REBUILD_HOFF
            tk.messagebox.showinfo(title, message)

    def UpdateBodyOffsetLabel(self, state, frame) -> None:
        """
        Updates label for current (x,y) body offset.

        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        try:
            bodyOffsets: list = self._CurBody["offset"][state]
            x, y = bodyOffsets[frame]

            label: str = self.LABEL_CURRENT_XY_BODY_OFFSET
            text: str = "{0:s} {1:+d}, {2:+d}".format(label, x, y)
            self._LabelOffsetBody.config(text=text)

        except (KeyError, IndexError):
            label: str = self.LABEL_CURRENT_XY_BODY_OFFSET
            text: str = "{0:s} {1:+d}, {2:+d}".format(label, 0, 0)
            self._LabelOffsetBody.config(text=text)

    def UpdateCurrentFrame(self) -> None:
        """
        Increments current animation frame.

        :return: None.
        """
        # Check frame iteration type
        isForward: bool = self._IsForward
        isPingpong: bool = self._BoolAnimPingPong.get()
        if not isPingpong:
            isForward = True

        # Increment frame
        curFrame = self._CurFrame
        if self._AnimObjs:
            if isForward:
                curFrame += 1
                if curFrame >= 4:
                    if not isPingpong:
                        curFrame = 0
                    else:
                        curFrame = 2
                        isForward = False
            else:
                curFrame -= 1
                if curFrame < 0:
                    curFrame = 1
                    isForward = True

        # Update references to current frame
        self._IsForward = isForward
        self._CurFrame = curFrame

        # Update frame count label
        text: str = "Frame: " + " ".join(
            ["({})".format(x) if x == curFrame else " {} ".format(x) for x in
             range(4)])

        self._LabelAnimFrame.config(text=text)

    def UpdateHeadOffsetLabel(self, state, frame) -> None:
        """
        Updates label for current (x,y) head offset.

        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        try:
            headOffsets: list = self._CurHead["offset"][state]

            x, y = headOffsets[frame]
            label: str = self.LABEL_CURRENT_XY_HEAD_OFFSET
            text: str = "{0:s} {1:+d}, {2:+d}".format(label, x, y)
            self._LabelOffsetHead.config(text=text)

        except (KeyError, IndexError):
            label: str = self.LABEL_CURRENT_XY_HEAD_OFFSET
            text: str = "{0:s} {1:+d}, {2:+d}".format(label, 0, 0)
            self._LabelOffsetHead.config(text=text)

    def UpdateOffsetLabels(self) -> None:
        """
        Updates per-frame (x,y) head and body offset labels.

        :return: None
        """
        state: str = self._CurState
        frame: int = self._CurFrame
        self.UpdateHeadOffsetLabel(state, frame)
        self.UpdateBodyOffsetLabel(state, frame)

    def UpdateSpeed(self, speed) -> None:
        """
        Updates current animation speed.

        :param speed: New framerate.

        :return: None.
        """
        text: str = "Speed: {}".format(speed)
        self._LabelAnimSpeed.config(text=text)
        self._CurSpeed = int(speed)

        if int(speed) == 0:
            self._HasInitAnim = False
        else:
            if not self._HasInitAnim:
                self._HasInitAnim = True
                self.DoAnimate()


def GUIMain() -> None:
    """
    Entrypoint for GUI version of Sprite Compositing Tool.

    :return: None
    """
    root = tk.Tk()
    app = App(root)
    app.mainloop()


if __name__ == "__main__":
    GUIMain()
