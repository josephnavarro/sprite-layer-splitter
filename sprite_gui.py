#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.

--------------------------------------------------------------------------------
"""
import sys
import cv2
import numpy as np
import tkinter as tk
import sprite_splitter
import sprite_imaging
from tkinter import messagebox
from tkinter import filedialog
from sprite_prepare import *


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
    INVALID_BODY_MESSAGE = "Error: Body spritesheet '{filename}' does not " \
                           "exist!"
    INVALID_HEAD_MESSAGE = "Error: Head spritesheet '{filename}' does not " \
                           "exist!"
    REBUILD_BIMG_CONFIRM = "Rebuild body source images?"
    REBUILD_BIMG_MESSAGE = "Body source images successfully rebuilt."
    REBUILD_BODY_CONFIRM = "Rebuild body database?"
    REBUILD_BODY_MESSAGE = "Body database was rebuilt."
    REBUILD_HIMG_CONFIRM = "Rebuild head source images?"
    REBUILD_HIMG_MESSAGE = "Head source images successfully rebuilt."
    REBUILD_HEAD_CONFIRM = "Rebuild head database?"
    REBUILD_HEAD_MESSAGE = "Head database was rebuilt."
    SUCCESS_FULL_MESSAGE = "Sprite frames saved to {filename}!"
    SUCCESS_IDLE_MESSAGE = "Idle frames saved to {filename}!"

    # Default widget dimensions
    if sys.platform == "win32":
        DEFAULT_OPTION_WIDTH = 26
        DEFAULT_BUTTON_WIDTH = 27
        SPEED_SCALE_LEN = 256
    else:
        DEFAULT_OPTION_WIDTH = 26
        DEFAULT_BUTTON_WIDTH = 29
        SPEED_SCALE_LEN = 480

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
    GRID_PREVIEW_FRAME_LABEL = [0, 1]
    GRID_HEAD_XYOFFSET_LABEL = [1, 1]
    GRID_BODY_XYOFFSET_LABEL = [2, 1]
    GRID_PREVIEW_SPEED_LABEL = [3, 1]
    GRID_PREVIEW_SPEED_SCALE = [4, 1]
    GRID_PING_PONG_CHECK_BOX = [5, 1]

    GRID_IMAGEPREVIEW_CANVAS = [0, 1]
    GRID_ANIM_PREVIEW_CANVAS = [0, 2]
    GRID_SELECT_HEAD_OPTIONS = [1, 0]
    GRID_RB_SRCS_HEAD_BUTTON = [2, 0]
    GRID_RB_JSON_HEAD_BUTTON = [3, 0]
    GRID_SELECT_BODY_OPTIONS = [1, 1]
    GRID_RB_SRCS_BODY_BUTTON = [2, 1]
    GRID_RB_JSON_BODY_BUTTON = [3, 1]
    GRID_PREVIEW_IDLE_BUTTON = [1, 2]
    GRID_PREVIEW_LEFT_BUTTON = [2, 2]
    GRID_PREVIEW_RIGHTBUTTON = [3, 2]
    GRID_COMPOSE_IDLE_BUTTON = [2, 3]
    GRID_COMPOSE_FULL_BUTTON = [3, 3]

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
    RB_JSON_BODY_LABEL = "Rebuild body database"
    RB_JSON_HEAD_LABEL = "Rebuild head database"
    RB_IMGS_BODY_LABEL = "Rebuild body source images"
    RB_IMGS_HEAD_LABEL = "Rebuild head source images"
    SAV_IDLE_BTN_LABEL = "Save idle frames"
    SAV_FULL_BTN_LABEL = "Save all frames"
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
        self._master = root
        self._master.resizable(False, False)
        self.winfo_toplevel().title(self.WINDOW_TITLE)

        # Initialize local non-widget data
        self._image_obj = None
        self._frame_fwd = True
        self._init_anim = False
        self._anim_objs = []
        self._cur_frame = 0
        self._cur_speed = 0
        self._cur_state = STATES[STATES.idle]

        self._body_data = {}
        self._body_list = [""]
        self._body_offs = {}
        self._cur_body = {}

        self._head_data = {}
        self._head_list = [""]
        self._head_offs = {}
        self._cur_head = {}

        self._ani_ping_pong_bool = tk.BooleanVar()
        self._head_option_string = tk.StringVar(self._master)
        self._body_option_string = tk.StringVar(self._master)
        self._preview_img_canvas = tk.Canvas(self._master)
        self._preview_ani_canvas = tk.Canvas(self._master)

        # Topleft frame
        self._topleft_frame = tk.Frame(self._master)
        self._topleft_frame.grid(row=0, column=0)

        # Topright frame
        self._topright_frame = tk.Frame(self._topleft_frame)
        self._topright_frame.grid(row=0, column=3)

        # Top frame (padding only)
        self._top_frame = tk.Frame(self._topright_frame, width=10, height=10)
        self._top_frame.grid(row=0, column=0)

        # Bottom frame
        self._bottom_frame = tk.Frame(self._master)
        self._bottom_frame.grid(row=2)

        # Initialize widgets
        self._exports_idle_button = tk.Button()
        self._exports_full_button = tk.Button()
        self._preview_idle_button = tk.Button()
        self._preview_left_button = tk.Button()
        self._preview_rightbutton = tk.Button()
        self._rebuild_body_button = tk.Button()
        self._rebuild_head_button = tk.Button()
        self._rebuild_body_images = tk.Button()
        self._rebuild_head_images = tk.Button()
        self._select_head_options = tk.OptionMenu(self._bottom_frame,
                                                  self._head_option_string,
                                                  *self._head_list)
        self._select_body_options = tk.OptionMenu(self._bottom_frame,
                                                  self._body_option_string,
                                                  *self._body_list)
        self._anim_pingpong_check = tk.Checkbutton()
        self._head_xyoffset_label = tk.Label()
        self._body_xyoffset_label = tk.Label()
        self._preview_speed_label = tk.Label()
        self._preview_frame_label = tk.Label()
        self._preview_speed_scale = tk.Scale()

        # Complete widget initialization
        self._init_head_data()
        self._init_body_data()
        self._init_save_idle_button()
        self._init_save_full_button()
        self._init_preview_canvas()
        self._init_preview_speed()
        self._init_preview_frame()
        self._init_offset_labels()
        self._init_preview_idle_button()
        self._init_preview_left_button()
        self._init_preview_rightbutton()
        self._init_rebuild_body_button()
        self._init_rebuild_head_button()
        self._init_rebuild_body_images()
        self._init_rebuild_head_images()
        self._init_select_head_options()
        self._init_select_body_options()
        self._init_anim_pingpong_check()

    def _init_anim_pingpong_check(self) -> None:
        """
        Completes initialization of checkbox for toggling animation ping-pong.

        :return: None.
        """
        self._anim_pingpong_check.destroy()

        self._anim_pingpong_check = tk.Checkbutton(
            self._topright_frame,
            text=self.ANIMATECHECK_LABEL,
            variable=self._ani_ping_pong_bool
            )

        self._anim_pingpong_check.grid(
            row=self.GRID_PING_PONG_CHECK_BOX[0],
            column=self.GRID_PING_PONG_CHECK_BOX[1],
            sticky=tk.W
            )

    def _init_body_data(self):
        """
        Completes initialization of local character body data (as loaded from
        file).

        :return: None.
        """
        self._body_data = {v.get("name", "---"): k for k, v in
                           LoadBodyPaths().items()}
        self._body_list = list(self._body_data)
        self._body_offs = LoadBodyOffsets()

    def _init_head_data(self) -> None:
        """
        Completes initialization of local character head data (as loaded from
        file).

        :return: None.
        """
        self._head_data = {v.get("name", "---"): k for k, v in
                           LoadHeadPaths().items()}
        self._head_list = list(self._head_data)
        self._head_offs = LoadHeadOffsets()

    def _init_offset_labels(self) -> None:
        """

        :return:
        """
        self._head_xyoffset_label.destroy()
        self._head_xyoffset_label = tk.Label(
            self._topright_frame,
            text="{0:s} {1:+d}, {2:+d}".format(self.XYHEADOFFSET_LABEL, 0, 0),
            )

        self._head_xyoffset_label.grid(
            row=self.GRID_HEAD_XYOFFSET_LABEL[0],
            column=self.GRID_HEAD_XYOFFSET_LABEL[1],
            sticky=tk.W,
            )

        self._body_xyoffset_label.destroy()
        self._body_xyoffset_label = tk.Label(
            self._topright_frame,
            text="{0:s} {1:+d}, {2:+d}".format(self.XYBODYOFFSET_LABEL, 0, 0),
            )

        self._body_xyoffset_label.grid(
            row=self.GRID_BODY_XYOFFSET_LABEL[0],
            column=self.GRID_BODY_XYOFFSET_LABEL[1],
            sticky=tk.W,
            )

    def _init_preview_frame(self) -> None:
        """
        Completes initialization of current frame display.

        :return: None
        """
        self._preview_frame_label.destroy()
        self._preview_frame_label = tk.Label(
            self._topright_frame,
            text="Frame: 0",
            )

        self._preview_frame_label.grid(
            row=self.GRID_PREVIEW_FRAME_LABEL[0],
            column=self.GRID_PREVIEW_FRAME_LABEL[1],
            sticky=tk.W,
            )

    def _init_preview_speed(self) -> None:
        """
        Completes initialization of framerate adjustment widgets.

        :return: None.
        """
        # Create speed label
        self._preview_speed_label.destroy()
        self._preview_speed_label = tk.Label(
            self._topright_frame,
            text="Speed: 0",
            )

        self._preview_speed_label.grid(
            row=self.GRID_PREVIEW_SPEED_LABEL[0],
            column=self.GRID_PREVIEW_SPEED_LABEL[1],
            sticky=tk.W,
            )

        # Create speed scale
        self._preview_speed_scale.destroy()
        self._preview_speed_scale = tk.Scale(
            self._topright_frame,
            from_=self.SPEED_SCALE_MIN,
            to=self.SPEED_SCALE_MAX,
            orient=tk.HORIZONTAL,
            length=self.SPEED_SCALE_LEN,
            showvalue=0,
            command=self.update_speed
            )
        self._preview_speed_scale.grid(
            row=self.GRID_PREVIEW_SPEED_SCALE[0],
            column=self.GRID_PREVIEW_SPEED_SCALE[1],
            sticky=tk.W
            )

    def _init_rebuild_body_images(self) -> None:
        """
        Completes initialization of "rebuild body intermediates" button.

        :return: None.
        """
        self._rebuild_body_images.destroy()
        self._rebuild_body_images = tk.Button(
            self._bottom_frame,
            text=self.RB_IMGS_BODY_LABEL,
            command=self.rebuild_body_intermediates,
            )

        self._rebuild_body_images.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            fg=self.FromRGB(*self.BODY_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.BODY_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.BODY_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.BODY_BUTTON_FG_COLOR),
            )

        self._rebuild_body_images.grid(
            row=self.GRID_RB_SRCS_BODY_BUTTON[0],
            column=self.GRID_RB_SRCS_BODY_BUTTON[1],
            padx=self.PAD_RB_IMGS_BODY_BUTTON[0],
            pady=self.PAD_RB_IMGS_BODY_BUTTON[1],
            )

    def _init_rebuild_head_images(self) -> None:
        """
        Completes initialization of "rebuild head intermediates" button.

        :return: None.
        """
        self._rebuild_head_images.destroy()
        self._rebuild_head_images = tk.Button(
            self._bottom_frame,
            text=self.RB_IMGS_HEAD_LABEL,
            command=self.rebuild_head_intermediates,
            )

        self._rebuild_head_images.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            fg=self.FromRGB(*self.HEAD_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.HEAD_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.HEAD_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.HEAD_BUTTON_FG_COLOR),
            )

        self._rebuild_head_images.grid(
            row=self.GRID_RB_SRCS_HEAD_BUTTON[0],
            column=self.GRID_RB_SRCS_HEAD_BUTTON[1],
            padx=self.PAD_RB_IMGS_HEAD_BUTTON[0],
            pady=self.PAD_RB_IMGS_HEAD_BUTTON[1],
            )

    def _init_select_head_options(self) -> None:
        """
        Completes initialization of character head dropdown menu.

        :return: None.
        """
        self._head_option_string.set(self.DEFAULT_HEAD_LABEL)

        self._select_head_options.destroy()
        self._select_head_options = tk.OptionMenu(
            self._bottom_frame,
            self._head_option_string,
            *self._head_list,
            )

        self._select_head_options.config(
            width=self.DEFAULT_OPTION_WIDTH,
            fg=self.FromRGB(*self.HEAD_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.HEAD_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.HEAD_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.HEAD_BUTTON_FG_COLOR),
            )

        self._select_head_options.grid(
            row=self.GRID_SELECT_HEAD_OPTIONS[0],
            column=self.GRID_SELECT_HEAD_OPTIONS[1],
            padx=self.PAD_SELECT_HEAD_OPTIONS[0],
            pady=self.PAD_SELECT_HEAD_OPTIONS[1],
            )

    def _init_select_body_options(self) -> None:
        """
        Completes initialization of character body dropdown menu.

        :return: None.
        """
        self._body_option_string.set(self.DEFAULT_BODY_LABEL)

        self._select_body_options.destroy()
        self._select_body_options = tk.OptionMenu(
            self._bottom_frame,
            self._body_option_string,
            *self._body_list,
            )

        self._select_body_options.config(
            width=self.DEFAULT_OPTION_WIDTH,
            fg=self.FromRGB(*self.BODY_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.BODY_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.BODY_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.BODY_BUTTON_FG_COLOR),
            )

        self._select_body_options.grid(
            row=self.GRID_SELECT_BODY_OPTIONS[0],
            column=self.GRID_SELECT_BODY_OPTIONS[1],
            padx=self.PAD_SELECT_BODY_OPTIONS[0],
            pady=self.PAD_SELECT_BODY_OPTIONS[1],
            )

    def _init_save_idle_button(self) -> None:
        """
        Completes initialization of "save idle frames" button.

        :return: None.
        """
        self._exports_idle_button.destroy()
        self._exports_idle_button = tk.Button(
            self._bottom_frame,
            text=self.SAV_IDLE_BTN_LABEL,
            command=self.save_idle,
            )

        self._exports_idle_button.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            fg=self.FromRGB(*self.SAVE_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.SAVE_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.SAVE_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.SAVE_BUTTON_FG_COLOR),
            )

        self._exports_idle_button.grid(
            row=self.GRID_COMPOSE_IDLE_BUTTON[0],
            column=self.GRID_COMPOSE_IDLE_BUTTON[1],
            padx=self.PAD_COMPOSE_IDLE_BUTTON[0],
            pady=self.PAD_COMPOSE_IDLE_BUTTON[1],
            )

    def _init_save_full_button(self) -> None:
        """
        Completes initialization of "full composition" button.

        :return: None.
        """
        self._exports_full_button.destroy()
        self._exports_full_button = tk.Button(
            self._bottom_frame,
            text=self.SAV_FULL_BTN_LABEL,
            command=self.save_full,
            )

        self._exports_full_button.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            fg=self.FromRGB(*self.SAVE_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.SAVE_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.SAVE_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.SAVE_BUTTON_FG_COLOR),
            )

        self._exports_full_button.grid(
            row=self.GRID_COMPOSE_FULL_BUTTON[0],
            column=self.GRID_COMPOSE_FULL_BUTTON[1],
            padx=self.PAD_COMPOSE_FULL_BUTTON[0],
            pady=self.PAD_COMPOSE_FULL_BUTTON[1],
            )

    def _init_preview_canvas(self) -> None:
        """
        Completes initialization of preview image canvas.

        :return: None.
        """
        # Set up static sprite preview
        self._image_obj = None

        self._preview_img_canvas.destroy()
        self._preview_img_canvas = tk.Canvas(
            self._topleft_frame,
            width=self.PREVIEW_CANVAS_WIDTH,
            height=self.PREVIEW_CANVAS_HEIGHT,
            bg=self.FromRGB(*self.PREVIEW_CANVAS_COLOR),
            relief=tk.SUNKEN,
            borderwidth=16,
            )

        self._preview_img_canvas.grid(
            row=self.GRID_IMAGEPREVIEW_CANVAS[0],
            column=self.GRID_IMAGEPREVIEW_CANVAS[1],
            )

        # Set up animated sprite preview
        self._anim_objs = []

        self._preview_ani_canvas.destroy()
        self._preview_ani_canvas = tk.Canvas(
            self._topleft_frame,
            width=self.PREVIEW_ANIM_WIDTH,
            height=self.PREVIEW_ANIM_HEIGHT,
            bg=self.FromRGB(*self.PREVIEW_CANVAS_COLOR),
            relief=tk.SUNKEN,
            borderwidth=16,
            )

        self._preview_ani_canvas.grid(
            row=self.GRID_ANIM_PREVIEW_CANVAS[0],
            column=self.GRID_ANIM_PREVIEW_CANVAS[1],
            )

    def _init_preview_idle_button(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self._preview_idle_button.destroy()
        self._preview_idle_button = tk.Button(
            self._bottom_frame,
            text=self.PREVIEW_IDLE_LABEL,
            command=self.make_idle_preview,
            )

        self._preview_idle_button.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            bg=self.FromRGB(*self.PREVIEW_BTN_BG_COLOR),
            fg=self.FromRGB(*self.PREVIEW_BTN_FG_COLOR),
            activebackground=self.FromRGB(*self.PREVIEW_BTN_BG_COLOR),
            activeforeground=self.FromRGB(*self.PREVIEW_BTN_FG_COLOR),
            )

        self._preview_idle_button.grid(
            row=self.GRID_PREVIEW_IDLE_BUTTON[0],
            column=self.GRID_PREVIEW_IDLE_BUTTON[1],
            padx=self.PAD_PREVIEW_IDLE_BUTTON[0],
            pady=self.PAD_PREVIEW_IDLE_BUTTON[1],
            )

    def _init_preview_left_button(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self._preview_left_button.destroy()
        self._preview_left_button = tk.Button(
            self._bottom_frame,
            text=self.PREVIEW_LEFT_LABEL,
            command=self.make_left_preview,
            )

        self._preview_left_button.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            bg=self.FromRGB(*self.PREVIEW_BTN_BG_COLOR),
            fg=self.FromRGB(*self.PREVIEW_BTN_FG_COLOR),
            activebackground=self.FromRGB(*self.PREVIEW_BTN_BG_COLOR),
            activeforeground=self.FromRGB(*self.PREVIEW_BTN_FG_COLOR),
            )

        self._preview_left_button.grid(
            row=self.GRID_PREVIEW_LEFT_BUTTON[0],
            column=self.GRID_PREVIEW_LEFT_BUTTON[1],
            padx=self.PAD_PREVIEW_LEFT_BUTTON[0],
            pady=self.PAD_PREVIEW_LEFT_BUTTON[1],
            )

    def _init_preview_rightbutton(self) -> None:
        """
        Completes initialization of "preview idle" button.

        :return: None
        """
        self._preview_rightbutton.destroy()
        self._preview_rightbutton = tk.Button(
            self._bottom_frame,
            text=self.PREVIEW_RIGHTLABEL,
            command=self.make_right_preview,
            )

        self._preview_rightbutton.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            bg=self.FromRGB(*self.PREVIEW_BTN_BG_COLOR),
            fg=self.FromRGB(*self.PREVIEW_BTN_FG_COLOR),
            activebackground=self.FromRGB(*self.PREVIEW_BTN_BG_COLOR),
            activeforeground=self.FromRGB(*self.PREVIEW_BTN_FG_COLOR),
            )

        self._preview_rightbutton.grid(
            row=self.GRID_PREVIEW_RIGHTBUTTON[0],
            column=self.GRID_PREVIEW_RIGHTBUTTON[1],
            padx=self.PAD_PREVIEW_RIGHTBUTTON[0],
            pady=self.PAD_PREVIEW_RIGHTBUTTON[1],
            )

    def _init_rebuild_body_button(self) -> None:
        """
        Completes initialization of "rebuild body" button.

        :return: None.
        """
        self._rebuild_body_button.destroy()
        self._rebuild_body_button = tk.Button(
            self._bottom_frame,
            text=self.RB_JSON_BODY_LABEL,
            command=self.rebuild_body_database,
            )

        self._rebuild_body_button.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            fg=self.FromRGB(*self.BODY_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.BODY_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.BODY_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.BODY_BUTTON_FG_COLOR),
            )

        self._rebuild_body_button.grid(
            row=self.GRID_RB_JSON_BODY_BUTTON[0],
            column=self.GRID_RB_JSON_BODY_BUTTON[1],
            padx=self.PAD_RB_JSON_BODY_BUTTON[0],
            pady=self.PAD_RB_JSON_BODY_BUTTON[1],
            )

    def _init_rebuild_head_button(self) -> None:
        """
        Completes initialization of "rebuild head" button.

        :return: None.
        """
        self._rebuild_head_button.destroy()
        self._rebuild_head_button = tk.Button(
            self._bottom_frame,
            text=self.RB_JSON_HEAD_LABEL,
            command=self.rebuild_head_database,
            )

        self._rebuild_head_button.config(
            width=self.DEFAULT_BUTTON_WIDTH,
            fg=self.FromRGB(*self.HEAD_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.HEAD_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.HEAD_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.HEAD_BUTTON_FG_COLOR),
            )

        self._rebuild_head_button.grid(
            row=self.GRID_RB_JSON_HEAD_BUTTON[0],
            column=self.GRID_RB_JSON_HEAD_BUTTON[1],
            padx=self.PAD_RB_JSON_HEAD_BUTTON[0],
            pady=self.PAD_RB_JSON_HEAD_BUTTON[1],
            )

    def _composite(self, func) -> (str, str, (np.ndarray or None)):
        """
        Performs a general-purpose image composition routine.

        :param func: Function to use for compositing
                     (e.g. CompositeIdle, CompositeFull...)

        :return: Tuple containing (in order) head key, body key,
                 and generated numpy image.
        """
        head: str = ""
        body: str = ""

        try:
            # Get head key
            try:
                head: str = self._head_data[self._head_option_string.get()]
            except KeyError:
                raise UnspecifiedHeadException

            # Get body key
            try:
                body: str = self._body_data[self._body_option_string.get()]
            except KeyError:
                raise UnspecifiedBodyException

            # Perform sprite composition
            try:
                return head, body, func(head, body)
            except sprite_splitter.NonexistentHeadException as e:
                raise InvalidHeadException(e.filename)
            except sprite_splitter.NonexistentBodyException as e:
                raise InvalidBodyException(e.filename)
            except cv2.error:
                raise InvalidFilenameException

        except UnspecifiedHeadException:
            # Head not specified
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.FAILURE_HEAD_MESSAGE,
                )

        except UnspecifiedBodyException:
            # Body not specified
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.FAILURE_BODY_MESSAGE,
                )

        except InvalidHeadException as e:
            # Head spritesheet does not exist
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.INVALID_HEAD_MESSAGE.format(filename=e.filename),
                )

        except InvalidBodyException as e:
            # Body spritesheet does not exist
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.INVALID_BODY_MESSAGE.format(filename=e.filename),
                )

        return head, body, None

    def save_idle(self) -> None:
        """
        Composites and saves idle frames.

        :return: None.
        """
        try:
            # Perform image composition
            head, body, image = self._composite(sprite_splitter.CompositeIdle)

            if image is not None:
                # Prompt user for destination filename
                FixPath(ROOT_OUTPUT_DIRECTORY)

                path: str = filedialog.asksaveasfilename(
                    initialfile="{}_{}.png".format(head, body),
                    initialdir=ROOT_OUTPUT_DIRECTORY,
                    title="Save As",
                    filetypes=FILETYPES,
                    )

                if not path:
                    raise EmptyFilenameException

                sprite_splitter.SaveImage(image, path)

                # Alert user upon success
                tk.messagebox.showinfo(
                    self.WINDOW_TITLE,
                    self.SUCCESS_IDLE_MESSAGE.format(
                        filename=os.path.basename(path)
                        )
                    )

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_TYPE_MESSAGE)

        except EmptyFilenameException:
            # Filename not specified
            pass

    def save_full(self):
        """
        Composites full frames.

        :return: None.
        """
        try:
            # Perform sprite composition
            head, body, image = self._composite(sprite_splitter.CompositeFull)

            if image is not None:
                # Prompt user for destination filename
                FixPath(ROOT_OUTPUT_DIRECTORY)

                path: str = filedialog.asksaveasfilename(
                    initialfile="{}_{}.png".format(head, body),
                    initialdir=ROOT_OUTPUT_DIRECTORY,
                    title="Save As",
                    filetypes=FILETYPES,
                    )

                if not path:
                    raise EmptyFilenameException

                sprite_splitter.SaveImage(image, path)

                # Alert user upon success
                tk.messagebox.showinfo(
                    self.WINDOW_TITLE,
                    self.SUCCESS_IDLE_MESSAGE.format(
                        filename=os.path.basename(path)
                        ),
                    )

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.FAILURE_TYPE_MESSAGE,
                )

        except EmptyFilenameException:
            # Filename not specified
            pass

    def make_idle_preview(self) -> None:
        """
        Generates a preview image for current sprite's "idle" frames.

        :return: None
        """
        try:
            # Perform sprite composition
            head, body, image = self._composite(sprite_splitter.CompositeIdle)
            if image is not None:
                try:
                    image = sprite_imaging.Crop(
                        image,
                        self.PREVIEW_IDLE_CROP_ORIG,
                        self.PREVIEW_IDLE_CROP_SIZE,
                        )

                    image = cv2.resize(
                        cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                        dsize=self.PREVIEW_RESIZED_DIMENS,
                        interpolation=cv2.INTER_NEAREST,
                        )

                    # Set static preview
                    self._image_obj = sprite_imaging.ToTkinter(
                        sprite_imaging.ToPIL(image),
                        )

                    self._preview_img_canvas.create_image(
                        (16, 16),
                        anchor=tk.NW,
                        image=self._image_obj,
                        )

                    # Set animated preview
                    self.set_animation_frames(image)

                    # Set current state and offsets
                    self._cur_state = STATES[STATES.idle]
                    try:
                        self._cur_head = self._head_offs[
                            self._body_data[self._body_option_string.get()]
                        ]
                    except KeyError:
                        self._cur_head = {}

                    try:
                        self._cur_body = self._body_offs[
                            self._body_data[self._body_option_string.get()]
                        ]
                    except KeyError:
                        self._cur_body = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.FAILURE_TYPE_MESSAGE,
                )

        except EmptyFilenameException:
            pass

    def make_left_preview(self) -> None:
        """
        Generates a preview image for current sprite's "left" frames.

        :return: None
        """
        try:
            # Perform sprite composition
            head, body, image = self._composite(sprite_splitter.CompositeFull)
            if image is not None:
                try:
                    image = sprite_imaging.Crop(
                        image,
                        self.PREVIEW_LEFT_CROP_ORIG,
                        self.PREVIEW_LEFT_CROP_SIZE,
                        )
                    image = cv2.resize(
                        cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                        dsize=self.PREVIEW_RESIZED_DIMENS,
                        interpolation=cv2.INTER_NEAREST,
                        )

                    # Generate static preview
                    self._image_obj = sprite_imaging.ToTkinter(
                        sprite_imaging.ToPIL(image)
                        )
                    self._preview_img_canvas.create_image(
                        (16, 16),
                        anchor=tk.NW,
                        image=self._image_obj,
                        )

                    # Set animated preview
                    self.set_animation_frames(image)

                    # Set current state and offsets
                    self._cur_state = STATES[STATES.left]
                    try:
                        self._cur_head = self._head_offs[
                            self._body_data[self._body_option_string.get()]
                        ]
                    except KeyError:
                        self._cur_head = {}

                    try:
                        self._cur_body = self._body_offs[
                            self._body_data[self._body_option_string.get()]
                        ]
                    except KeyError:
                        self._cur_body = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.FAILURE_TYPE_MESSAGE,
                )

        except EmptyFilenameException:
            # Filename not specified
            pass

    def make_right_preview(self) -> None:
        """
        Generates a preview image for current sprite's "right" frames.

        :return: None
        """
        try:
            # Perform sprite composition
            head, body, image = self._composite(sprite_splitter.CompositeFull)
            if image is not None:
                try:
                    image = sprite_imaging.Crop(
                        image,
                        self.PREVIEW_RIGHTCROP_ORIG,
                        self.PREVIEW_RIGHTCROP_SIZE,
                        )

                    image = cv2.resize(
                        cv2.cvtColor(image, cv2.COLOR_BGR2RGB),
                        dsize=self.PREVIEW_RESIZED_DIMENS,
                        interpolation=cv2.INTER_NEAREST,
                        )

                    # Set static preview
                    self._image_obj = sprite_imaging.ToTkinter(
                        sprite_imaging.ToPIL(image),
                        )

                    self._preview_img_canvas.create_image(
                        (16, 16),
                        anchor=tk.NW,
                        image=self._image_obj,
                        )

                    # Set animated preview
                    self.set_animation_frames(image)

                    # Set current state and offsets
                    self._cur_state = STATES[STATES.right]
                    try:
                        self._cur_head = self._head_offs[
                            self._body_data[self._body_option_string.get()]
                        ]
                    except KeyError:
                        self._cur_head = {}

                    try:
                        self._cur_body = self._body_offs[
                            self._body_data[self._body_option_string.get()]
                        ]
                    except KeyError:
                        self._cur_body = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.FAILURE_TYPE_MESSAGE,
                )

        except EmptyFilenameException:
            # Filename not specified
            pass

    def rebuild_body_database(self) -> None:
        """
        Rebuilds body JSON database.

        :return: None
        """
        do_rebuild = tk.messagebox.askquestion(
            self.WINDOW_TITLE,
            self.REBUILD_BODY_CONFIRM,
            )

        if do_rebuild == "yes":
            CreateBodyJSON()
            self._init_body_data()
            self._init_select_body_options()
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.REBUILD_BODY_MESSAGE,
                )

    def rebuild_head_database(self) -> None:
        """
        Rebuilds head JSON database.

        :return: None.
        """
        do_rebuild = tk.messagebox.askquestion(
            self.WINDOW_TITLE,
            self.REBUILD_HEAD_CONFIRM,
            )

        if do_rebuild == "yes":
            CreateHeadJSON()
            self._init_head_data()
            self._init_select_head_options()
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.REBUILD_HEAD_MESSAGE,
                )

    def rebuild_body_intermediates(self) -> None:
        """
        Rebuilds intermediate body spritesheets.

        :return: None.
        """
        do_rebuild = tk.messagebox.askquestion(
            self.WINDOW_TITLE,
            self.REBUILD_BIMG_CONFIRM,
            )

        if do_rebuild == "yes":
            PrepareBody()
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.REBUILD_BIMG_MESSAGE,
                )

    def rebuild_head_intermediates(self) -> None:
        """
        Rebuilds intermediate head spritesheets.

        :return: None.
        """
        do_rebuild = tk.messagebox.askquestion(
            self.WINDOW_TITLE,
            self.REBUILD_HIMG_CONFIRM,
            )

        if do_rebuild == "yes":
            PrepareHead()
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.REBUILD_HIMG_MESSAGE,
                )

    def set_animation_frames(self, image) -> None:
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

        self._anim_objs = [
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame1)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame2)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame3)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame4)),
            ]

        # Reset animation counters
        self._cur_frame = 0
        self._frame_fwd = True
        self._cur_speed = self._preview_speed_scale.get()
        self._preview_ani_canvas.create_image(
            (16, 16),
            anchor=tk.NW,
            image=self._anim_objs[0],
            )

    def animate(self) -> None:
        """
        Local animation callback function.

        This function calls itself periodically, and thus should only be
        manually invoked once.

        :return: None
        """
        self.update_frame()
        self.update_offset_labels()

        try:
            # Draw frame to canvas
            self._preview_ani_canvas.create_image(
                (16, 16),
                anchor=tk.NW,
                image=self._anim_objs[self._cur_frame],
                )
        except IndexError:
            pass

        # Repeat if animation is active
        if self._cur_speed > 0:
            self.after(1000 // self._cur_speed, self.animate)

    def update_frame(self) -> None:
        """
        Increments current animation frame.

        :return: None.
        """
        # Check frame iteration type
        frame_fwd = self._frame_fwd
        is_pingpong = self._ani_ping_pong_bool.get()
        if not is_pingpong:
            frame_fwd = True

        # Increment frame
        cur_frame = self._cur_frame
        if self._anim_objs:
            if frame_fwd:
                cur_frame += 1
                if cur_frame >= 4:
                    if not is_pingpong:
                        cur_frame = 0
                    else:
                        cur_frame = 2
                        frame_fwd = False
            else:
                cur_frame -= 1
                if cur_frame < 0:
                    cur_frame = 1
                    frame_fwd = True

        # Update references to current frame
        self._frame_fwd = frame_fwd
        self._cur_frame = cur_frame
        self._preview_frame_label.config(text="Frame: {}".format(cur_frame))

    def update_speed(self, speed) -> None:
        """
        Updates current animation speed.

        :param speed: Framerate to update with.

        :return: None.
        """
        self._preview_speed_label.config(text="Speed: {}".format(speed))
        self._cur_speed = int(speed)

        if int(speed) == 0:
            self._init_anim = False
        else:
            if not self._init_anim:
                self._init_anim = True
                self.animate()

    def update_offset_labels(self) -> None:
        """
        Updates per-frame (x,y) head and body offset labels.

        :return: None
        """
        state: str = self._cur_state
        cur_frame: int = self._cur_frame

        try:
            # Update head offset label
            head_offsets = self._cur_head["offset"][state]

            if self._cur_head["size"] == "small":
                head_offsets = head_offsets[1:4] + [head_offsets[0]]

            x, y = head_offsets[cur_frame]
            self._head_xyoffset_label.config(
                text="{0:s} {1:+d}, {2:+d}".format(
                    self.XYHEADOFFSET_LABEL, x, y,
                    ),
                )

        except (KeyError, IndexError):
            self._head_xyoffset_label.config(
                text="{0:s} {1:+d}, {2:+d}".format(
                    self.XYHEADOFFSET_LABEL, 0, 0,
                    ),
                )

        try:
            # Update body offset label
            body_offsets = self._cur_body["offset"][state]
            x, y = body_offsets[cur_frame]

            self._body_xyoffset_label.config(
                text="{0:s} {1:+d}, {2:+d}".format(
                    self.XYBODYOFFSET_LABEL, x, y,
                    ),
                )

        except (KeyError, IndexError):
            self._body_xyoffset_label.config(
                text="{0:s} {1:+d}, {2:+d}".format(
                    self.XYBODYOFFSET_LABEL, 0, 0,
                    ),
                )


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
