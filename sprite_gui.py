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
    FAILURE_BODY_MESSAGE = "Error: Body not specified!"
    FAILURE_HEAD_MESSAGE = "Error: Head not specified!"
    FAILURE_TYPE_MESSAGE = "Error: Invalid image format specified!"
    INVALID_BODY_MESSAGE = "Error: Body spritesheet '{}' does not exist!"
    INVALID_HEAD_MESSAGE = "Error: Head spritesheet '{}' does not exist!"
    REBUILD_BIMG_CONFIRM = "Rebuild body source images?"
    REBUILD_BIMG_MESSAGE = "Body source images successfully rebuilt."
    REBUILD_BDAT_CONFIRM = "Update available bodies?"
    REBUILD_BDAT_MESSAGE = "Body database was rebuilt."
    REBUILD_BOFF_CONFIRM = "Update body offsets?"
    REBUILD_BOFF_MESSAGE = "Body offsets updated."
    REBUILD_HIMG_CONFIRM = "Rebuild head source images?"
    REBUILD_HIMG_MESSAGE = "Head source images successfully rebuilt."
    REBUILD_HDAT_CONFIRM = "Update available heads?"
    REBUILD_HDAT_MESSAGE = "Head database was rebuilt."
    REBUILD_HOFF_CONFIRM = "Update head offsets?"
    REBUILD_HOFF_MESSAGE = "Head offsets updated."
    SUCCESS_FULL_MESSAGE = "Sprite frames saved to {}!"
    SUCCESS_IDLE_MESSAGE = "Idle frames saved to {}!"

    # Default widget dimensions
    if IsWindows():
        # Windows
        DEFAULT_OPTION_WIDTH = 26
        DEFAULT_BUTTON_WIDTH = 27
        DEFAULT_SLIDER_WIDTH = 256
    else:
        # OS X / Linux
        DEFAULT_OPTION_WIDTH = 19
        DEFAULT_BUTTON_WIDTH = 22
        DEFAULT_SLIDER_WIDTH = 256

    PREVIEW_CANVAS_WIDTH = 384
    PREVIEW_CANVAS_HEIGHT = 96
    PREVIEW_ANIM_WIDTH = 96
    PREVIEW_ANIM_HEIGHT = 96

    # Default widget colors
    BODY_BUTTON_FG_COLOR = [0, 0, 0]
    HEAD_BUTTON_FG_COLOR = [0, 0, 0]
    PREVIEW_BTN_FG_COLOR = [0, 0, 0]
    PREVIEW_CANVAS_COLOR = [0, 0, 0]
    SAVE_BUTTON_FG_COLOR = [0, 0, 0]
    BODY_BUTTON_BG_COLOR = [255, 200, 200]
    HEAD_BUTTON_BG_COLOR = [200, 224, 255]
    PREVIEW_BTN_BG_COLOR = [200, 255, 212]
    SAVE_BUTTON_BG_COLOR = [244, 212, 248]

    # Grid positions for widgets
    GRID_LABEL_FRAME_PREVIEW = [0, 1]
    GRID_LABEL_HEAD_XYOFFSET = [1, 1]
    GRID_LABEL_BODY_XYOFFSET = [2, 1]
    GRID_LABEL_SPEED_PREVIEW = [3, 1]
    GRID_SCALE_SPEED_PREVIEW = [4, 1]
    GRID_CHECK_ANIM_PINGPONG = [5, 1]
    GRID_CANVAS_IMGS_PREVIEW = [0, 1]
    GRID_CANVAS_ANIM_PREVIEW = [0, 2]
    GRID_OPTIONS_SELECT_HEAD = [1, 0]
    GRID_BUTTON_REBUILD_HIMG = [2, 0]
    GRID_BUTTON_REBUILD_HDAT = [3, 0]
    GRID_BUTTON_REBUILD_HOFF = [4, 0]
    GRID_OPTIONS_SELECT_BODY = [1, 1]
    GRID_BUTTON_REBUILD_BIMG = [2, 1]
    GRID_BUTTON_REBUILD_BDAT = [3, 1]
    GRID_BUTTON_REBUILD_BOFF = [4, 1]
    GRID_BUTTON_PREVIEW_IDLE = [2, 2]
    GRID_BUTTON_PREVIEW_LEFT = [3, 2]
    GRID_BUTTON_PREVIEW_RIGH = [4, 2]
    GRID_BUTTON_COMPOSE_IDLE = [2, 3]
    GRID_BUTTON_COMPOSE_FULL = [3, 3]

    # Padding for widgets
    PAD_COMPOSE_FULL_BUTTON = [4, 4]
    PAD_COMPOSE_IDLE_BUTTON = [4, 4]
    PAD_PREVIEW_IDLE_BUTTON = [4, 4]
    PAD_PREVIEW_LEFT_BUTTON = [4, 4]
    PAD_PREVIEW_RIGHTBUTTON = [4, 4]
    PAD_RB_JSON_BODY_BUTTON = [4, 4]
    PAD_RB_JSON_HEAD_BUTTON = [4, 4]
    PAD_RB_IMGS_BODY_BUTTON = [4, 4]
    PAD_RB_IMGS_HEAD_BUTTON = [4, 4]
    PAD_SELECT_BODY_OPTIONS = [4, 4]
    PAD_SELECT_HEAD_OPTIONS = [4, 4]

    # Preview composition dimensions
    PREVIEW_IDLE_CROP_ORIG = [0, 0]
    PREVIEW_IDLE_CROP_SIZE = [128, 32]
    PREVIEW_LEFT_CROP_ORIG = [0, 32]
    PREVIEW_LEFT_CROP_SIZE = [128, 32]
    PREVIEW_RIGHTCROP_ORIG = [0, 64]
    PREVIEW_RIGHTCROP_SIZE = [128, 32]
    PREVIEW_RESIZED_DIMENS = (384, 96)

    # Button and menu text labels
    DEFAULT_HEAD_LABEL = "Select head"
    DEFAULT_BODY_LABEL = "Select body"
    PREVIEW_IDLE_LABEL = "Preview idle frames"
    PREVIEW_LEFT_LABEL = "Preview left frames"
    PREVIEW_RIGHTLABEL = "Preview right frames"
    REBUILD_BDAT_LABEL = "Update available bodies"
    REBUILD_HDAT_LABEL = "Update available heads"
    REBUILD_BIMG_LABEL = "Rebuild body source images"
    REBUILD_HIMG_LABEL = "Rebuild head source images"
    REBUILD_BOFF_LABEL = "Reload body offset data"
    REBUILD_HOFF_LABEL = "Reload head offset data"
    SAV_IDLE_BTN_LABEL = "Export idle frames"
    SAV_FULL_BTN_LABEL = "Export all frames"
    ANIMATECHECK_LABEL = "Ping-pong animation"
    XYHEADOFFSET_LABEL = "Head offset:"
    XYBODYOFFSET_LABEL = "Body offset:"

    # Animation speeds
    SPEED_SCALE_MIN = 0
    SPEED_SCALE_MAX = 12

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
        self._BtnExportIdle = tk.Button()
        self._BtnExportFull = tk.Button()
        self._BtnPreviewIdle = tk.Button()
        self._BtnPreviewLeft = tk.Button()
        self._BtnPreviewRight = tk.Button()
        self._BtnRebuildBodyData = tk.Button()
        self._BtnRebuildBodyImages = tk.Button()
        self._BtnRebuildBodyOffsets = tk.Button()
        self._BtnRebuildHeadData = tk.Button()
        self._BtnRebuildHeadImages = tk.Button()
        self._BtnRebuildHeadOffsets = tk.Button()

        # Menus
        self._MenuSelectHead = tk.OptionMenu(self._FrameBottom,
                                             self._StrHeadOption,
                                             *self._HeadList)

        self._MenuSelectBody = tk.OptionMenu(self._FrameBottom,
                                             self._StrBodyOption,
                                             *self._BodyList)

        # Check buttons
        self._CheckAnimPingpong = tk.Checkbutton()

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
        self.InitBtnExportIdle()
        self.InitBtnExportFull()
        self.InitCanvasPreviews()
        self.InitSpeedWidgets()
        self.InitFrameReadout()
        self.InitLabelOffsets()
        self.InitBtnPreviewIdle()
        self.InitBtnPreviewLeft()
        self.InitBtnPreviewRight()
        self.InitBtnRebuildBodyData()
        self.InitBtnRebuildBodyImages()
        self.InitBtnRebuildBodyOffsets()
        self.InitBtnRebuildHeadData()
        self.InitBtnRebuildHeadImages()
        self.InitBtnRebuildHeadOffsets()
        self.InitSelectHeadOptions()
        self.InitSelectBodyOptions()
        self.InitAnimPingpongCheck()

    def DoAnimate(self) -> None:
        """
        Local animation callback function.

        This function calls itself periodically, and thus should only be
        manually invoked once.

        :return: None
        """
        self.UpdateCurrentFrame()
        self.UpdateOffsetLabels()

        try:
            # Draw frame to canvas
            pos: tuple = (16, 16)
            anchor: str = tk.NW
            im: tk.PhotoImage = self._AnimObjs[self._CurFrame]
            self._CanvAnimPreview.create_image(pos, anchor=anchor, image=im)

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
        head_key: str = ""
        body_key: str = ""

        try:
            # Get head key
            try:
                head_name: str = self._StrHeadOption.get()
                head_key: str = self._HeadData[head_name]
            except KeyError:
                raise UnspecifiedHeadException

            # Get body key
            try:
                body_name: str = self._StrBodyOption.get()
                body_key: str = self._BodyData[body_name]
            except KeyError:
                raise UnspecifiedBodyException

            # Perform sprite composition
            try:
                return head_key, body_key, func(head_key, body_key)
            except sprite_splitter.NonexistentHeadException as e:
                raise InvalidHeadException(e.filename)
            except sprite_splitter.NonexistentBodyException as e:
                raise InvalidBodyException(e.filename)
            except cv2.error:
                raise InvalidFilenameException

        except UnspecifiedHeadException:
            # Head not specified
            title: str = self.WINDOW_TITLE
            message: str = self.FAILURE_HEAD_MESSAGE
            tk.messagebox.showinfo(title, message)

        except UnspecifiedBodyException:
            # Body not specified
            title: str = self.WINDOW_TITLE
            message: str = self.FAILURE_BODY_MESSAGE
            tk.messagebox.showinfo(title, message)

        except InvalidHeadException as e:
            # Head spritesheet does not exist
            title: str = self.WINDOW_TITLE
            message: str = self.INVALID_HEAD_MESSAGE.format(e.filename)
            tk.messagebox.showinfo(title, message)

        except InvalidBodyException as e:
            # Body spritesheet does not exist
            title: str = self.WINDOW_TITLE
            message: str = self.INVALID_BODY_MESSAGE.format(e.filename)
            tk.messagebox.showinfo(title, message)

        return head_key, body_key, None

    def ExportFullFrames(self) -> None:
        """
        Composites and exports all frames to file.

        :return: None.
        """
        try:
            # Perform sprite composition
            head, body, image = self.DoComposite(sprite_splitter.CompositeFull)

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
                    fn: str = os.path.basename(path)
                    message: str = self.SUCCESS_IDLE_MESSAGE.format(fn)
                    tk.messagebox.showinfo(title, message)

        except InvalidFilenameException:
            # Image format not recognized
            title: str = self.WINDOW_TITLE
            message: str = self.FAILURE_TYPE_MESSAGE
            tk.messagebox.showinfo(title, message)

        except EmptyFilenameException:
            # Filename not specified
            pass

    def ExportIdleFrames(self) -> None:
        """
        Composites and exports idle frames to file.

        :return: None.
        """
        try:
            # Perform image composition
            head, body, image = self.DoComposite(sprite_splitter.CompositeIdle)

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
                    fn: str = os.path.basename(path)
                    message: str = self.SUCCESS_IDLE_MESSAGE.format(fn)

                    tk.messagebox.showinfo(title, message)

        except InvalidFilenameException:
            # Image format not recognized
            title: str = self.WINDOW_TITLE
            message: str = self.FAILURE_TYPE_MESSAGE
            tk.messagebox.showinfo(title, message)

    def InitAnimatedPreview(self) -> None:
        """
        Initializes animated image preview canvas.

        :return: None.
        """
        self._AnimObjs = []

        self._CanvAnimPreview.destroy()

        master: tk.Frame = self._FrameTopleft
        width: int = self.PREVIEW_ANIM_WIDTH
        height: int = self.PREVIEW_ANIM_HEIGHT
        bg: str = self.FromRGB(*self.PREVIEW_CANVAS_COLOR)
        relief: str = tk.SUNKEN
        border: int = 16

        self._CanvAnimPreview = tk.Canvas(
            master,
            width=width,
            height=height,
            background=bg,
            relief=relief,
            borderwidth=border,
        )

        row: int = self.GRID_CANVAS_ANIM_PREVIEW[0]  # Row
        col: int = self.GRID_CANVAS_ANIM_PREVIEW[1]  # Column

        self._CanvAnimPreview.grid(row=row, column=col)

    def InitAnimPingpongCheck(self) -> None:
        """
        Completes initialization of checkbox for toggling animation ping-pong.

        :return: None.
        """
        self._CheckAnimPingpong.destroy()

        mtr: tk.Frame = self._FrameTopRight  # Master
        txt: str = self.ANIMATECHECK_LABEL  # Text
        var: tk.BooleanVar = self._BoolAnimPingPong  # Variable
        row: int = self.GRID_CHECK_ANIM_PINGPONG[0]  # Row
        column: int = self.GRID_CHECK_ANIM_PINGPONG[1]  # Column
        sticky: str = tk.W  # Sticky

        self._CheckAnimPingpong = tk.Checkbutton(mtr, text=txt, variable=var)
        self._CheckAnimPingpong.grid(row=row, column=column, sticky=sticky)

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
        label: str = self.XYBODYOFFSET_LABEL
        text: str = "{0:s} {1:+d}, {2:+d}".format(label, 0, 0)
        row: int = self.GRID_LABEL_BODY_XYOFFSET[0]
        col: int = self.GRID_LABEL_BODY_XYOFFSET[1]
        sticky: str = tk.W

        self._LabelOffsetBody = tk.Label(master, text=text)
        self._LabelOffsetBody.grid(row=row, column=col, sticky=sticky)

    def InitBtnExportFull(self) -> None:
        """
        Completes initialization of "full composition" button.

        :return: None.
        """
        self._BtnExportFull.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.SAV_FULL_BTN_LABEL
        cmd: types.FunctionType = self.ExportFullFrames

        self._BtnExportFull = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        fg: str = self.FromRGB(*self.SAVE_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.SAVE_BUTTON_BG_COLOR)

        self._BtnExportFull.config(
            width=width,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_COMPOSE_FULL[0]  # Row
        col: int = self.GRID_BUTTON_COMPOSE_FULL[1]  # Column
        px: int = self.PAD_COMPOSE_FULL_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_COMPOSE_FULL_BUTTON[1]  # Vertical padding

        self._BtnExportFull.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnExportIdle(self) -> None:
        """
        Completes initialization of "save idle frames" button.

        :return: None.
        """
        self._BtnExportIdle.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.SAV_IDLE_BTN_LABEL
        cmd: types.FunctionType = self.ExportIdleFrames

        self._BtnExportIdle = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        fg: str = self.FromRGB(*self.SAVE_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.SAVE_BUTTON_BG_COLOR)

        self._BtnExportIdle.config(
            width=width,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_COMPOSE_IDLE[0]  # Row
        col: int = self.GRID_BUTTON_COMPOSE_IDLE[1]  # Column
        px: int = self.PAD_COMPOSE_IDLE_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_COMPOSE_IDLE_BUTTON[1]  # Vertical padding

        self._BtnExportIdle.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnPreviewIdle(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self._BtnPreviewIdle.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.PREVIEW_IDLE_LABEL
        cmd: types.FunctionType = self.MakeIdlePreview

        self._BtnPreviewIdle = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        bg: str = self.FromRGB(*self.PREVIEW_BTN_BG_COLOR)
        fg: str = self.FromRGB(*self.PREVIEW_BTN_FG_COLOR)

        self._BtnPreviewIdle.config(
            width=width,
            background=bg,
            foreground=fg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_PREVIEW_IDLE[0]  # Row
        col: int = self.GRID_BUTTON_PREVIEW_IDLE[1]  # Column
        px: int = self.PAD_PREVIEW_IDLE_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_PREVIEW_IDLE_BUTTON[1]  # Vertical padding

        self._BtnPreviewIdle.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnPreviewLeft(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self._BtnPreviewLeft.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.PREVIEW_LEFT_LABEL
        cmd: types.FunctionType = self.MakeLeftPreview

        self._BtnPreviewLeft = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        bg: str = self.FromRGB(*self.PREVIEW_BTN_BG_COLOR)
        fg: str = self.FromRGB(*self.PREVIEW_BTN_FG_COLOR)

        self._BtnPreviewLeft.config(
            width=width,
            background=bg,
            foreground=fg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_PREVIEW_LEFT[0]  # Row
        col: int = self.GRID_BUTTON_PREVIEW_LEFT[1]  # Column
        px: int = self.PAD_PREVIEW_LEFT_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_PREVIEW_LEFT_BUTTON[1]  # Vertical padding

        self._BtnPreviewLeft.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnPreviewRight(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self._BtnPreviewRight.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.PREVIEW_RIGHTLABEL
        cmd: types.FunctionType = self.MakeRightPreview

        self._BtnPreviewRight = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        bg: str = self.FromRGB(*self.PREVIEW_BTN_BG_COLOR)
        fg: str = self.FromRGB(*self.PREVIEW_BTN_FG_COLOR)

        self._BtnPreviewRight.config(
            width=width,
            background=bg,
            foreground=fg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_PREVIEW_RIGH[0]  # Row
        col: int = self.GRID_BUTTON_PREVIEW_RIGH[1]  # Column
        px: int = self.PAD_PREVIEW_RIGHTBUTTON[0]  # Horizontal padding
        py: int = self.PAD_PREVIEW_RIGHTBUTTON[1]  # Vertical padding

        self._BtnPreviewRight.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnRebuildBodyData(self) -> None:
        """
        Completes initialization of "rebuild body" button.

        :return: None.
        """
        self._BtnRebuildBodyData.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.REBUILD_BDAT_LABEL
        cmd: types.FunctionType = self.RebuildBodyData

        self._BtnRebuildBodyData = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        fg: str = self.FromRGB(*self.BODY_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.BODY_BUTTON_BG_COLOR)

        self._BtnRebuildBodyData.config(
            width=width,
            background=bg,
            foreground=fg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_REBUILD_BDAT[0]  # Row
        col: int = self.GRID_BUTTON_REBUILD_BDAT[1]  # Column
        px: int = self.PAD_RB_JSON_BODY_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_RB_JSON_BODY_BUTTON[1]  # Vertical padding

        self._BtnRebuildBodyData.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnRebuildBodyImages(self) -> None:
        """
        Completes initialization of "rebuild body intermediates" button.

        :return: None.
        """
        self._BtnRebuildBodyImages.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = App.REBUILD_BIMG_LABEL
        cmd: types.FunctionType = self.RebuildBodyImages

        self._BtnRebuildBodyImages = tk.Button(master, text=text, command=cmd)

        width: int = App.DEFAULT_BUTTON_WIDTH
        fg: str = App.FromRGB(*App.BODY_BUTTON_FG_COLOR)
        bg: str = App.FromRGB(*App.BODY_BUTTON_BG_COLOR)

        self._BtnRebuildBodyImages.config(
            width=width,
            foreground=fg,
            background=bg,
            activeforeground=fg,
            activebackground=bg,
        )

        row: int = self.GRID_BUTTON_REBUILD_BIMG[0]  # Row
        col: int = self.GRID_BUTTON_REBUILD_BIMG[1]  # Column
        px: int = self.PAD_RB_IMGS_BODY_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_RB_IMGS_BODY_BUTTON[1]  # Vertical padding

        self._BtnRebuildBodyImages.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnRebuildBodyOffsets(self) -> None:
        """
        Completes initialization of "rebuild body offsets" button.

        :return: None.
        """
        self._BtnRebuildBodyOffsets.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = App.REBUILD_BOFF_LABEL
        cmd: types.FunctionType = self.RebuildBodyOffsets

        self._BtnRebuildBodyOffsets = tk.Button(master, text=text, command=cmd)

        width: int = App.DEFAULT_BUTTON_WIDTH
        fg: str = App.FromRGB(*App.BODY_BUTTON_FG_COLOR)
        bg: str = App.FromRGB(*App.BODY_BUTTON_BG_COLOR)

        self._BtnRebuildBodyOffsets.config(
            width=width,
            foreground=fg,
            background=bg,
            activeforeground=fg,
            activebackground=bg,
        )

        row: int = self.GRID_BUTTON_REBUILD_BOFF[0]  # Row
        col: int = self.GRID_BUTTON_REBUILD_BOFF[1]  # Column
        px: int = self.PAD_RB_IMGS_BODY_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_RB_IMGS_BODY_BUTTON[1]  # Vertical padding

        self._BtnRebuildBodyOffsets.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnRebuildHeadData(self) -> None:
        """
        Completes initialization of "rebuild head" button.

        :return: None.
        """
        self._BtnRebuildHeadData.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.REBUILD_HDAT_LABEL
        cmd: types.FunctionType = self.RebuildHeadData

        self._BtnRebuildHeadData = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        fg: str = self.FromRGB(*self.HEAD_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.HEAD_BUTTON_BG_COLOR)

        self._BtnRebuildHeadData.config(
            width=width,
            background=bg,
            foreground=fg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_REBUILD_HDAT[0]  # Row
        col: int = self.GRID_BUTTON_REBUILD_HDAT[1]  # Column
        px: int = self.PAD_RB_JSON_HEAD_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_RB_JSON_HEAD_BUTTON[1]  # Vertical padding

        self._BtnRebuildHeadData.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnRebuildHeadImages(self) -> None:
        """
        Completes initialization of "rebuild head intermediates" button.

        :return: None.
        """
        self._BtnRebuildHeadImages.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = self.REBUILD_HIMG_LABEL
        cmd: types.FunctionType = self.RebuildHeadImages

        self._BtnRebuildHeadImages = tk.Button(master, text=text, command=cmd)

        width: int = self.DEFAULT_BUTTON_WIDTH
        fg: str = self.FromRGB(*self.HEAD_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.HEAD_BUTTON_BG_COLOR)

        self._BtnRebuildHeadImages.config(
            width=width,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_BUTTON_REBUILD_HIMG[0]  # Row
        col: int = self.GRID_BUTTON_REBUILD_HIMG[1]  # Column
        px: int = self.PAD_RB_IMGS_HEAD_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_RB_IMGS_HEAD_BUTTON[1]  # Vertical padding

        self._BtnRebuildHeadImages.grid(row=row, column=col, padx=px, pady=py)

    def InitBtnRebuildHeadOffsets(self) -> None:
        """
        Completes initialization of "rebuild head offsets" button.

        :return: None.
        """
        self._BtnRebuildHeadOffsets.destroy()

        master: tk.Frame = self._FrameBottom
        text: str = App.REBUILD_HOFF_LABEL
        cmd: types.FunctionType = self.RebuildHeadOffsets

        self._BtnRebuildHeadOffsets = tk.Button(master, text=text, command=cmd)

        width: int = App.DEFAULT_BUTTON_WIDTH
        fg: str = App.FromRGB(*App.HEAD_BUTTON_FG_COLOR)
        bg: str = App.FromRGB(*App.HEAD_BUTTON_FG_COLOR)

        self._BtnRebuildHeadOffsets.config(
            width=width,
            foreground=fg,
            background=bg,
            activeforeground=fg,
            activebackground=bg,
        )

        row: int = self.GRID_BUTTON_REBUILD_HOFF[0]  # Row
        col: int = self.GRID_BUTTON_REBUILD_HOFF[1]  # Column
        px: int = self.PAD_RB_IMGS_HEAD_BUTTON[0]  # Horizontal padding
        py: int = self.PAD_RB_IMGS_HEAD_BUTTON[1]  # Vertical padding

        self._BtnRebuildHeadOffsets.grid(row=row, column=col, padx=px, pady=py)

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
        text: str = "Frame: 0"
        row: int = self.GRID_LABEL_FRAME_PREVIEW[0]
        col: int = self.GRID_LABEL_FRAME_PREVIEW[1]
        sticky: str = tk.W

        self._LabelAnimFrame = tk.Label(master, text=text)
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
        label: str = self.XYHEADOFFSET_LABEL
        text: str = "{0:s} {1:+d}, {2:+d}".format(label, 0, 0)
        row: int = self.GRID_LABEL_HEAD_XYOFFSET[0]
        column: int = self.GRID_LABEL_HEAD_XYOFFSET[1]
        sticky: str = tk.W

        self._LabelOffsetHead = tk.Label(master, text=text)
        self._LabelOffsetHead.grid(row=row, column=column, sticky=sticky)

    def InitLabelOffsets(self) -> None:
        """
        Completes initialization of per-frame (x,y) offset labels.

        :return: None.
        """
        self.InitHeadOffsetLabel()
        self.InitBodyOffsetLabel()

    def InitSelectHeadOptions(self) -> None:
        """
        Completes initialization of character head dropdown menu.

        :return: None.
        """
        self._StrHeadOption.set(self.DEFAULT_HEAD_LABEL)

        self._MenuSelectHead.destroy()

        master: tk.Frame = self._FrameBottom
        label: tk.StringVar = self._StrHeadOption
        options: list = self._HeadList

        self._MenuSelectHead = tk.OptionMenu(master, label, *options)

        width: int = self.DEFAULT_OPTION_WIDTH
        fg: str = self.FromRGB(*self.HEAD_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.HEAD_BUTTON_BG_COLOR)

        self._MenuSelectHead.config(
            width=width,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
        )

        row: int = self.GRID_OPTIONS_SELECT_HEAD[0]  # Row
        col: int = self.GRID_OPTIONS_SELECT_HEAD[1]  # Column
        px: int = self.PAD_SELECT_HEAD_OPTIONS[0]  # Horizontal padding
        py: int = self.PAD_SELECT_HEAD_OPTIONS[1]  # Vertical padding

        self._MenuSelectHead.grid(row=row, column=col, padx=px, pady=py)

    def InitSelectBodyOptions(self) -> None:
        """
        Completes initialization of character body dropdown menu.

        :return: None.
        """
        self._StrBodyOption.set(self.DEFAULT_BODY_LABEL)

        self._MenuSelectBody.destroy()

        master: tk.Frame = self._FrameBottom
        text: tk.StringVar = self._StrBodyOption
        options: list = self._BodyList
        width: int = self.DEFAULT_OPTION_WIDTH
        fg: str = self.FromRGB(*self.BODY_BUTTON_FG_COLOR)
        bg: str = self.FromRGB(*self.BODY_BUTTON_BG_COLOR)

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
        px: int = self.PAD_SELECT_BODY_OPTIONS[0]  # Horizontal padding
        py: int = self.PAD_SELECT_BODY_OPTIONS[1]  # Vertical padding

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

        self._LabelAnimSpeed = tk.Label(master, text=text)
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

        self._ScaleAnimSpeed.grid(row=row, column=col, sticky=sticky)

    def InitStaticPreview(self) -> None:
        """
        Initializes static image preview canvas.

        :return: None.
        """
        self._ImageObj = None

        self._CanvStaticPreview.destroy()

        master: tk.Frame = self._FrameTopleft
        width: int = self.PREVIEW_CANVAS_WIDTH
        height: int = self.PREVIEW_CANVAS_HEIGHT
        bg: str = self.FromRGB(*self.PREVIEW_CANVAS_COLOR)
        relief: str = tk.SUNKEN
        border: int = 16

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
        w, h = self.PREVIEW_ANIM_WIDTH, self.PREVIEW_ANIM_HEIGHT
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

        self._CanvStaticPreview.create_text(
            32 + 96 * 0, 32, font="Arial 20 bold", fill="white", text="0"
        )
        self._CanvStaticPreview.create_text(
            32 + 96 * 1, 32, font="Arial 20 bold", fill="white", text="1"
        )
        self._CanvStaticPreview.create_text(
            32 + 96 * 2, 32, font="Arial 20 bold", fill="white", text="2"
        )
        self._CanvStaticPreview.create_text(
            32 + 96 * 3, 32, font="Arial 20 bold", fill="white", text="3"
        )

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
                    start: list = self.PREVIEW_IDLE_CROP_ORIG
                    size: list = self.PREVIEW_IDLE_CROP_SIZE
                    dsize: tuple = self.PREVIEW_RESIZED_DIMENS
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
            message: str = self.FAILURE_TYPE_MESSAGE
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
                    start: list = self.PREVIEW_LEFT_CROP_ORIG
                    size: list = self.PREVIEW_LEFT_CROP_SIZE
                    dsize: tuple = self.PREVIEW_RESIZED_DIMENS
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
            message: str = self.FAILURE_TYPE_MESSAGE
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
                    start: list = self.PREVIEW_RIGHTCROP_ORIG
                    size: list = self.PREVIEW_RIGHTCROP_SIZE
                    dsize: tuple = self.PREVIEW_RESIZED_DIMENS
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
            message: str = self.FAILURE_TYPE_MESSAGE
            tk.messagebox.showinfo(title, message)

    def RebuildBodyData(self) -> None:
        """
        Rebuilds JSON database for body spritesheet filepaths.

        :return: None
        """
        title: str = self.WINDOW_TITLE
        query: str = self.REBUILD_BDAT_CONFIRM

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateBodyJSON()

            self.InitBodyData()
            self.InitSelectBodyOptions()

            message: str = self.REBUILD_BDAT_MESSAGE
            tk.messagebox.showinfo(title, message)

    def RebuildBodyImages(self) -> None:
        """
        Rebuilds intermediate body spritesheets.

        :return: None.
        """
        title: str = self.WINDOW_TITLE
        message: str = self.REBUILD_BIMG_CONFIRM

        if tk.messagebox.askquestion(title, message) == "yes":
            PrepareBody()

            message = self.REBUILD_BIMG_MESSAGE
            tk.messagebox.showinfo(title, message)

    def RebuildBodyOffsets(self) -> None:
        """
        Rebuilds body offset database.

        :return: None.
        """
        title: str = App.WINDOW_TITLE
        message: str = App.REBUILD_BOFF_CONFIRM

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

            message = App.REBUILD_BOFF_MESSAGE
            tk.messagebox.showinfo(title, message)

    def RebuildHeadData(self) -> None:
        """
        Rebuilds head JSON database.

        :return: None.
        """
        title: str = self.WINDOW_TITLE
        message: str = self.REBUILD_HDAT_CONFIRM

        if tk.messagebox.askquestion(title, message) == "yes":
            CreateHeadJSON()

            self.InitHeadData()
            self.InitSelectHeadOptions()

            message = self.REBUILD_HDAT_MESSAGE
            tk.messagebox.showinfo(title, message)

    def RebuildHeadImages(self) -> None:
        """
        Rebuilds intermediate head spritesheets.

        :return: None.
        """
        title: str = App.WINDOW_TITLE
        message: str = App.REBUILD_HIMG_CONFIRM

        if tk.messagebox.askquestion(title, message) == "yes":
            PrepareHead()

            message = self.REBUILD_HIMG_MESSAGE
            tk.messagebox.showinfo(title, message)

    def RebuildHeadOffsets(self) -> None:
        """
        Rebuilds head offset database.

        :return: None.
        """
        title: str = App.WINDOW_TITLE
        message: str = App.REBUILD_HOFF_CONFIRM

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

            message = App.REBUILD_HOFF_MESSAGE
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

            label: str = self.XYBODYOFFSET_LABEL
            text: str = "{0:s} {1:+d}, {2:+d}".format(label, x, y)
            self._LabelOffsetBody.config(text=text)

        except (KeyError, IndexError):
            label: str = self.XYBODYOFFSET_LABEL
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
        text: str = "Frame: {}".format(curFrame)
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

            # This is necessary; don't worry about it! Don't worry.
            if self._CurHead["size"] == "small":
                headOffsets = headOffsets[1:4] + [headOffsets[0]]

            x, y = headOffsets[frame]
            label: str = self.XYHEADOFFSET_LABEL
            text: str = "{0:s} {1:+d}, {2:+d}".format(label, x, y)
            self._LabelOffsetHead.config(text=text)

        except (KeyError, IndexError):
            label: str = self.XYHEADOFFSET_LABEL
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
