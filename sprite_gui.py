#! usr/bin/env python3
"""
--------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.

--------------------------------------------------------------------------------
"""
import cv2
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
    else:
        # OS X / Linux
        SIZES["default-menu"] = [19, 0]
        SIZES["default-button"] = [22, 0]
        SIZES["default-slider"] = [280, 0]

    # Grid positions for widgets
    GRID_SCALE_SPEED_PREVIEW = [4, 1]

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
        "offset-body":          [2, 1],
        "offset-head":          [1, 1],
        "frame-anim":           [0, 1],
        "speed-anim":           [3, 1],
        "select-head":          [1, 0],
        "select-body":          [1, 1],
        "preview-static":       [0, 1],
        "preview-anim":         [0, 2],
        "pingpong-animation":   [1, 2],
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
    }

    # Preview composition dimensions
    RECTS = {
        "idle":  [0, 0, 128, 32],
        "left":  [0, 32, 128, 32],
        "right": [0, 64, 128, 32],
    }

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
        "offset-body":          "Body: {0:+d}, {1:+d}",
        "offset-head":          "Head: {0:+d}, {1:+d}",
        "speed-anim":           "Speed: {0:d}",
        "frame-anim":           "Frame: ({0:d})  {1:d}  {2:d}  {3:d}",
        "select-head":          "Select head",
        "select-body":          "Select body",
        "pingpong-animation":   "Ping-pong animation",
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
        "select-head":          {"fg": [0, 0, 0], "bg": [200, 224, 255]},
        "select-body":          {"fg": [0, 0, 0], "bg": [255, 200, 200]},
        "preview-static":       {"fg": [0, 0, 0], "bg": [0, 0, 0]},
        "preview-anim":         {"fg": [0, 0, 0], "bg": [0, 0, 0]},
    }

    LABEL_CHECK_REVERSE_LAYERING = "Reverse layering"

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
        self._AnimObjects = []
        self._ImageObject = None
        self._IsForwards = True
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

        # String variables
        self._StringVars = {
            "select-head": tk.StringVar(self._Master),
            "select-body": tk.StringVar(self._Master),
        }

        # Frames
        self._FrameTopleft = tk.Frame(self._Master)
        self._FrameTopleft.grid(row=0, column=0)

        self._FrameTopRight = tk.Frame(self._FrameTopleft)
        self._FrameTopRight.grid(row=0, column=3)

        self._FrameTop = tk.Frame(self._FrameTopRight, width=10, height=10)
        self._FrameTop.grid(row=0, column=0)

        self._FrameBottom = tk.Frame(self._Master)
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

        # Menus
        self._Menus = {
            "select-head": tk.OptionMenu(
                self._FrameBottom,
                self._StringVars["select-head"],
                *self._HeadList
            ),
            "select-body": tk.OptionMenu(
                self._FrameBottom,
                self._StringVars["select-body"],
                *self._BodyList
            ),
        }

        # Labels
        self._Labels = {
            "offset-head": tk.Label(),
            "offset-body": tk.Label(),
            "speed-anim":  tk.Label(),
            "frame-anim":  tk.Label(),
        }

        # Sliders
        self._ScaleAnimSpeed = tk.Scale()

        # Complete widget initialization
        self.InitDataHead()
        self.InitDataBody()
        self.InitButton(self._FrameBottom,
                        "export-idle",
                        self.ExportIdleFrames)
        self.InitButton(self._FrameBottom,
                        "export-full",
                        self.ExportFullFrames)
        self.InitPreviewStatic()
        self.InitPreviewAnim()
        self.InitSliderFramerate()
        self.InitLabel(self._FrameTopRight,
                       "speed-anim",
                       ("Courier", 14),
                       tk.W, 0)
        self.InitLabel(self._FrameTopRight,
                       "frame-anim",
                       ("Courier", 14),
                       tk.W, 0, 1, 2, 3)
        self.InitLabel(self._FrameTopRight,
                       "offset-head",
                       ("Courier", 14),
                       tk.W, 0, 0)
        self.InitLabel(self._FrameTopRight,
                       "offset-body",
                       ("Courier", 14),
                       tk.W, 0, 0)
        self.InitButton(self._FrameBottom,
                        "preview-idle",
                        self.MakeIdlePreview)
        self.InitButton(self._FrameBottom,
                        "preview-left",
                        self.MakeLeftPreview)
        self.InitButton(self._FrameBottom,
                        "preview-right",
                        self.MakeRightPreview)
        self.InitButton(self._FrameBottom,
                        "rebuild-body-data",
                        self.RebuildBodyData)
        self.InitButton(self._FrameBottom,
                        "rebuild-body-images",
                        self.RebuildBodyImages)
        self.InitButton(self._FrameBottom,
                        "rebuild-body-offsets",
                        self.RebuildBodyOffsets)
        self.InitButton(self._FrameBottom,
                        "rebuild-head-data",
                        self.RebuildHeadData)
        self.InitButton(self._FrameBottom,
                        "rebuild-head-images",
                        self.RebuildHeadImages)
        self.InitButton(self._FrameBottom,
                        "rebuild-head-offsets",
                        self.RebuildHeadOffsets)
        self.InitMenu(self._FrameBottom,
                      "select-head",
                      self._HeadList)
        self.InitMenu(self._FrameBottom,
                      "select-body",
                      self._BodyList)
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
            self._Canvases["preview-anim"].create_image(
                (16, 16),
                anchor=tk.NW,
                image=self._AnimObjects[self._CurFrame],
            )
        except IndexError:
            # Current frame is invalid
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
        headKey = ""
        bodyKey = ""

        try:
            try:
                # Get head key
                headName = self._StringVars["select-head"].get()
                headKey = self._HeadData[headName]
            except KeyError:
                raise UnspecifiedHeadException

            try:
                # Get body key
                bodyName = self._StringVars["select-body"].get()
                bodyKey = self._BodyData[bodyName]
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
            tk.messagebox.showinfo(App.WINDOW_TITLE,
                                   App.MESSAGE_FAILURE_HEAD)
        except UnspecifiedBodyException:
            # Body not specified
            tk.messagebox.showinfo(App.WINDOW_TITLE,
                                   App.MESSAGE_FAILURE_BODY)
        except InvalidHeadException as e:
            # Head spritesheet does not exist
            tk.messagebox.showinfo(App.WINDOW_TITLE,
                                   App.MESSAGE_INVALID_HEAD.format(e.filename))
        except InvalidBodyException as e:
            # Body spritesheet does not exist
            tk.messagebox.showinfo(App.WINDOW_TITLE,
                                   App.MESSAGE_INVALID_BODY.format(e.filename))

        return headKey, bodyKey, None

    def ExportFrames(self, func, message) -> None:
        """
        Composites and exports all frames to file.

        :param func:    Frame compositing callback function.
        :param message: Success message.

        :return: None.
        """
        try:
            # Perform sprite composition
            head, body, image = self.DoComposite(func)

            if image is not None:
                # Prompt user for destination filename
                FixPath(ROOT_OUTPUT_DIR)
                initialfile = "{}_{}.png".format(head, body)
                initialdir = ROOT_OUTPUT_DIR
                title = "Save As"
                filetypes = FILETYPES
                path = filedialog.asksaveasfilename(initialfile=initialfile,
                                                    initialdir=initialdir,
                                                    title=title,
                                                    filetypes=filetypes)
                if path:
                    # Save image if path is valid
                    sprite_splitter.SaveImage(image, path)
                    message = message.format(os.path.basename(path))
                    tk.messagebox.showinfo(App.WINDOW_TITLE, message)

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(App.WINDOW_TITLE,
                                   App.MESSAGE_FAILURE_TYPE)

        except EmptyFilenameException:
            # Filename not specified
            pass

    def ExportFullFrames(self) -> None:
        """
        Composites and exports all frames to file.

        :return: None.
        """
        self.ExportFrames(sprite_splitter.CompositeFull,
                          App.MESSAGE_SUCCESS_FULL)

    def ExportIdleFrames(self) -> None:
        """
        Composites and exports idle frames to file.

        :return: None.
        """
        self.ExportFrames(sprite_splitter.CompositeIdle,
                          App.MESSAGE_SUCCESS_IDLE)

    def InitPreviewAnim(self) -> None:
        """
        Initializes animated image preview canvas.

        :return: None.
        """
        self._AnimObjects = []
        self.InitCanvas(self._FrameTopleft, "preview-anim", 13)

    def InitButton(self, master, tag, cmd) -> None:
        """
        Locally initializes a button.

        :param master: Tkinter root frame for button.
        :param tag:    Tag of button to initialize.
        :param cmd:    Callback function for button.

        :return: None.
        """
        width = App.SIZES["default-button"][0]  # Button width
        foreground = App.FromRGB(*App.COLORS[tag]["fg"])  # FG color
        background = App.FromRGB(*App.COLORS[tag]["bg"])  # BG color

        self._Buttons[tag].destroy()
        self._Buttons[tag] = tk.Button(master,
                                       text=App.LABELS[tag],
                                       command=cmd)
        self._Buttons[tag].config(width=width,
                                  foreground=foreground,
                                  background=background,
                                  activebackground=background,
                                  activeforeground=foreground)
        self._Buttons[tag].grid(row=App.GRID[tag][0],
                                column=App.GRID[tag][1],
                                padx=App.PAD[tag][0],
                                pady=App.PAD[tag][1])

    def InitCanvas(self, master, tag, border) -> None:
        """
        Locally initializes a canvas.

        :param master: Widget root.
        :param tag:    Name of canvas to initialize.
        :param border: Border size for canvas.

        :return: None.
        """
        background = App.FromRGB(*App.COLORS[tag]["bg"])

        self._Canvases[tag].destroy()
        self._Canvases[tag] = tk.Canvas(master,
                                        width=App.SIZES[tag][0],
                                        height=App.SIZES[tag][1],
                                        background=background,
                                        relief=tk.SUNKEN,
                                        borderwidth=border)
        self._Canvases[tag].grid(row=App.GRID[tag][0],
                                 column=App.GRID[tag][1])

    def InitCheckbox(self, master, tag, variable, sticky) -> None:
        """
        Initializes a checkbox.

        :param master:
        :param tag:
        :param variable:
        :param sticky:

        :return:
        """
        self._Checkboxes[tag].destroy()
        self._Checkboxes[tag] = tk.Checkbutton(master,
                                               text=App.LABELS[tag],
                                               variable=variable)
        self._Checkboxes[tag].grid(row=App.GRID[tag][0],
                                   column=App.GRID[tag][1],
                                   sticky=sticky)

    def InitCheckAnimPingpong(self) -> None:
        """
        Completes initialization of checkbox for toggling animation ping-pong.

        :return: None.
        """
        self.InitCheckbox(self._FrameBottom,
                          "pingpong-animation",
                          self._BoolAnimPingPong,
                          tk.NS)

    def InitCheckLayerReverse(self):
        """
        Callback function. TODO

        :return: None.
        """
        return

    def InitDataBody(self):
        """
        Completes initialization of body data (from file).

        :return: None.
        """
        self._BodyData = {v.get("name", "---"): k
                          for k, v in LoadBodyPaths().items()}
        self._BodyList = sorted(list(self._BodyData))
        self._BodyOffsets = LoadBodyOffsets()

    def InitDataHead(self) -> None:
        """
        Completes initialization of head data (from file).

        :return: None.
        """
        self._HeadData = {v.get("name", "---"): k
                          for k, v in LoadHeadPaths().items()}
        self._HeadList = sorted(list(self._HeadData))
        self._HeadOffsets = LoadHeadOffsets()

    def InitLabel(self, master, tag, font, sticky, *args) -> None:
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
        self._Labels[tag] = tk.Label(master,
                                     font=font,
                                     text=text)
        self._Labels[tag].grid(row=App.GRID[tag][0],
                               column=App.GRID[tag][1],
                               sticky=sticky)

    def InitMenu(self, master, tag, options) -> None:
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
        self._Menus[tag] = tk.OptionMenu(master,
                                         self._StringVars[tag],
                                         *options)
        self._Menus[tag].config(width=width,
                                foreground=foreground,
                                background=background,
                                activebackground=background,
                                activeforeground=foreground)
        self._Menus[tag].grid(row=App.GRID[tag][0],
                              column=App.GRID[tag][1],
                              padx=App.PAD[tag][0],
                              pady=App.PAD[tag][1])

    def InitSliderFramerate(self) -> None:
        """
        Completes initialization of framerate slider.

        :return: None.
        """
        self._ScaleAnimSpeed.destroy()
        self._ScaleAnimSpeed = tk.Scale(self._FrameTopRight,
                                        from_=App.SPEED_SCALE_MIN,
                                        to=App.SPEED_SCALE_MAX,
                                        orient=tk.HORIZONTAL,
                                        length=App.SIZES["default-slider"][0],
                                        showvalue=0,
                                        command=self.UpdateSpeed)
        self._ScaleAnimSpeed.grid(row=App.GRID_SCALE_SPEED_PREVIEW[0],
                                  column=App.GRID_SCALE_SPEED_PREVIEW[1],
                                  sticky=tk.W,
                                  pady=4)

    def InitPreviewStatic(self) -> None:
        """
        Initializes static image preview canvas.

        :return: None.
        """
        self._ImageObject = None  ## !!
        self.InitCanvas(self._FrameTopleft, "preview-static", 13)

    def MakeAnimationFrames(self, image) -> None:
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

        self._AnimObjects = [
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame1)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame2)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame3)),
            sprite_imaging.ToTkinter(sprite_imaging.ToPIL(frame4)),
        ]

        # Reset animation counters
        self._CurFrame = 0
        self._IsForwards = True
        self._CurSpeed = self._ScaleAnimSpeed.get()
        self._Canvases["preview-anim"].create_image((16, 16),
                                                    anchor=tk.NW,
                                                    image=self._AnimObjects[0])

    def MakeAnimationPreview(self, image) -> None:
        """
        Displays static preview frames.

        :param image: Image to display.

        :return: None.
        """
        self._ImageObject = sprite_imaging.ToTkinter(
            sprite_imaging.ToPIL(image))
        self._Canvases["preview-static"].create_image((16, 16),
                                                      anchor=tk.NW,
                                                      image=self._ImageObject)

        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 0, 92, "(0)")
        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 1, 92, "(1)")
        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 2, 92, "(2)")
        App.DrawText(self._Canvases["preview-static"], 18 + 96 * 3, 92, "(3)")

    def MakePreview(self, func, state) -> None:
        """
        Generates a static preview image.

        :param func:  Compositing callback function to use.
        :param state: Named state of preview to generate.

        :return: None.
        """
        try:
            # Perform sprite composition
            self._HeadOffsets = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            head, body, image = self.DoComposite(func)

            if image is not None:
                try:
                    # Crop idle frames from source spritesheet
                    start = App.RECTS[state][0:2]
                    size = App.RECTS[state][2:4]
                    dsize = tuple(App.SIZES["preview-resize"])
                    interp = cv2.INTER_NEAREST

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
                        headName = self._StringVars["select-head"].get()
                        headKey = self._BodyData[headName]
                        self._CurHead = self._HeadOffsets[headKey]
                    except KeyError:
                        self._CurHead = {}

                    try:
                        # Populate per-frame body offset data
                        bodyName = self._StringVars["select-body"].get()
                        bodyKey = self._BodyData[bodyName]
                        self._CurBody = self._BodyOffsets[bodyKey]
                    except KeyError:
                        self._CurBody = {}

                except cv2.error:
                    raise InvalidFilenameException

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(App.WINDOW_TITLE,
                                   App.MESSAGE_FAILURE_TYPE)

    def MakeIdlePreview(self) -> None:
        """
        Generates a preview image for current sprite's "idle" frames.

        :return: None
        """
        self.MakePreview(sprite_splitter.CompositeIdle, "idle")

    def MakeLeftPreview(self) -> None:
        """
        Generates a preview image for current sprite's "left" frames.

        :return: None
        """
        self.MakePreview(sprite_splitter.CompositeFull, "left")

    def MakeRightPreview(self) -> None:
        """
        Generates a preview image for current sprite's "right" frames.

        :return: None
        """
        self.MakePreview(sprite_splitter.CompositeFull, "right")

    def RebuildBodyData(self) -> None:
        """
        Rebuilds JSON database for body spritesheet filepaths.

        :return: None
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_BDAT

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateBodyJSON()
            self.InitDataBody()
            self.InitMenu(self._FrameBottom, "select-body", self._BodyList)

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_BDAT)

    # noinspection PyMethodMayBeStatic
    def RebuildBodyImages(self) -> None:
        """
        Callback function. Rebuilds intermediate body spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_BIMG

        if tk.messagebox.askquestion(title, query) == "yes":
            PrepareBody()
            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_BIMG)

    def RebuildBodyOffsets(self) -> None:
        """
        Callback function. Rebuilds body offset database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_BOFF

        if tk.messagebox.askquestion(title, query) == "yes":
            self._BodyOffsets = LoadBodyOffsets()
            self.UpdateOffsetLabels()

            if self._AnimObjects:
                if self._CurState == STATES[STATES.idle]:
                    self.MakeIdlePreview()
                elif self._CurState == STATES[STATES.left]:
                    self.MakeLeftPreview()
                elif self._CurState == STATES[STATES.right]:
                    self.MakeRightPreview()

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_BOFF)

    def RebuildHeadData(self) -> None:
        """
        Callback function. Rebuilds head JSON database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_HDAT

        if tk.messagebox.askquestion(title, query) == "yes":
            CreateHeadJSON()
            self.InitDataHead()
            self.InitMenu(self._FrameBottom, "select-head", self._HeadList)

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_HDAT)

    # noinspection PyMethodMayBeStatic
    def RebuildHeadImages(self) -> None:
        """
        Callback function. Rebuilds intermediate head spritesheets.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_HIMG

        if tk.messagebox.askquestion(title, query) == "yes":
            PrepareHead()
            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_HIMG)

    def RebuildHeadOffsets(self) -> None:
        """
        Callback function. Rebuilds head offset database.

        :return: None.
        """
        title = App.WINDOW_TITLE
        query = App.CONFIRM_REBUILD_HOFF

        if tk.messagebox.askquestion(title, query) == "yes":
            self._HeadOffsets = LoadHeadOffsets()
            self.UpdateOffsetLabels()

            if self._AnimObjects:
                if self._CurState == STATES[STATES.idle]:
                    self.MakeIdlePreview()
                elif self._CurState == STATES[STATES.left]:
                    self.MakeLeftPreview()
                elif self._CurState == STATES[STATES.right]:
                    self.MakeRightPreview()

            tk.messagebox.showinfo(title, App.MESSAGE_REBUILD_HOFF)

    def UpdateBodyOffsetLabel(self, state, frame) -> None:
        """
        Updates label for current (x,y) body offset.

        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        try:
            self._Labels["offset-body"].config(
                text=App.LABELS["offset-body"].format(
                    *self._CurBody["offset"][state][frame]))

        except (KeyError, IndexError):
            self._Labels["offset-body"].config(
                text=App.LABELS["offset-body"].format(0, 0))

    def UpdateCurrentFrame(self) -> None:
        """
        Increments current animation frame.

        :return: None.
        """
        # Check frame iteration type
        isForwards = self._IsForwards
        isPingpong = self._BoolAnimPingPong.get()
        if not isPingpong:
            isForwards = True

        # Increment frame
        curFrame = self._CurFrame
        if self._AnimObjects:
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
        self._CurFrame = curFrame

        # Update frame count label
        self._Labels["frame-anim"].config(
            text="Frame: " + " ".join(["({})".format(x)
                                       if x == curFrame
                                       else " {} ".format(x)
                                       for x in range(4)]))

    def UpdateHeadOffsetLabel(self, state, frame) -> None:
        """
        Updates label for current (x,y) head offset.

        :param state: Current sprite state.
        :param frame: Current frame of animation.

        :return: None.
        """
        try:
            self._Labels["offset-head"].config(
                text=App.LABELS["offset-head"].format(
                    *self._CurHead["offset"][state][frame]))

        except (KeyError, IndexError):
            self._Labels["offset-head"].config(
                text=App.LABELS["offset-head"].format(0, 0))

    def UpdateOffsetLabels(self) -> None:
        """
        Updates per-frame (x,y) head and body offset labels.

        :return: None
        """
        state = self._CurState
        frame = self._CurFrame
        self.UpdateHeadOffsetLabel(state, frame)
        self.UpdateBodyOffsetLabel(state, frame)

    def UpdateSpeed(self, speed) -> None:
        """
        Updates current animation speed.

        :param speed: New framerate.

        :return: None.
        """
        self._Labels["speed-anim"].config(
            text=App.LABELS["speed-anim"].format(int(speed)))
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
