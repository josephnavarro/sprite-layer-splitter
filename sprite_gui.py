#! usr/bin/env python3
"""
------------------------------------------------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.
------------------------------------------------------------------------------------------------------------------------
"""
import cv2
import tkinter as tk
import sprite_splitter
import sprite_utils
import sprite_json
from tkinter import messagebox
from tkinter import filedialog
from sprite_constant import *


class UnspecifiedHeadException(Exception):
    pass


class UnspecifiedBodyException(Exception):
    pass


class InvalidHeadException(sprite_splitter.NonexistentHeadException):
    __slots__ = []


    def __init__(self, name):
        super().__init__(name)


class InvalidBodyException(sprite_splitter.NonexistentBodyException):
    __slots__ = []


    def __init__(self, name):
        super().__init__(name)


class InvalidFilenameException(Exception):
    pass


class EmptyFilenameException(Exception):
    pass


class App(tk.Frame):
    __slots__ = [
        "_master",
        "_characters",
        "_classes",
        "_chara_string",
        "_class_string",
        "_chara_menu",
        "_class_menu",
        "_idle_button",
        "_full_button",
        "_rebuild_head_button",
        "_rebuild_body_button",
        "_chara_data",
        "_class_data",
        ]

    WINDOW_TITLE = "Fire Emblem 3DS Sprite Tool"

    FAILURE_HEAD_MESSAGE = "Error: Head not specified!"
    FAILURE_BODY_MESSAGE = "Error: Body not specified!"
    INVALID_HEAD_MESSAGE = "Error: Head spritesheet '{filename}' does not exist!"
    INVALID_BODY_MESSAGE = "Error: Body spritesheet '{filename}' does not exist!"
    FAILURE_TYPE_MESSAGE = "Error: Invalid image format specified!"
    SUCCESS_IDLE_MESSAGE = "Idle frames saved to {filename}!"
    SUCCESS_FULL_MESSAGE = "Sprite frames saved to {filename}!"
    REBUILD_HEAD_CONFIRM = "Rebuild head database?"
    REBUILD_HEAD_MESSAGE = "Head database was rebuilt."
    REBUILD_BODY_CONFIRM = "Rebuild body database?"
    REBUILD_BODY_MESSAGE = "Body database was rebuilt."

    DEFAULT_DROPDOWN_WIDTH = 26
    DEFAULT_BUTTON_WIDTH = 27

    DEFAULT_CHARA = "Select head"
    DEFAULT_CLASS = "Select body"

    CHARA_BUTTON_FG_COLOR = [0, 0, 0]
    CHARA_BUTTON_BG_COLOR = [255, 200, 200]
    CLASS_BUTTON_FG_COLOR = [0, 0, 0]
    CLASS_BUTTON_BG_COLOR = [200, 255, 200]

    IDLE_BUTTON_TEXT = "Composite idle frames"
    FULL_BUTTON_TEXT = "Composite all frames"
    REBUILD_HEAD_TEXT = "Rebuild head sources"
    REBUILD_BODY_TEXT = "Rebuild body sources"


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

        self._master = root
        self.winfo_toplevel().title(self.WINDOW_TITLE)

        self._chara_data = {}
        self._class_data = {}
        self._characters = [""]
        self._classes = [""]

        self._idle_button = tk.Button()
        self._full_button = tk.Button()
        self._rebuild_body_button = tk.Button()
        self._rebuild_head_button = tk.Button()
        self._chara_string = tk.StringVar(self._master)
        self._chara_menu = tk.OptionMenu(self._master, self._chara_string, *self._characters)
        self._class_string = tk.StringVar(self._master)
        self._class_menu = tk.OptionMenu(self._master, self._class_string, *self._classes)

        self._init_chara_data()
        self._init_class_data()
        self._init_idle_button()
        self._init_full_button()
        self._init_rebuild_body_button()
        self._init_rebuild_head_button()
        self._init_chara_menu()
        self._init_class_menu()


    def _init_chara_data(self) -> None:
        """
        Completes initialization of local character head data (as loaded from file).

        :return: None.
        """
        self._chara_data = {v.get("name", "---"): k for k, v in sprite_json.GetHeadPathData().items()}
        self._characters = list(self._chara_data)


    def _init_class_data(self):
        """
        Completes initialization of local character body data (as loaded from file).

        :return: None.
        """
        self._class_data = {v.get("name", "---"): k for k, v in sprite_json.GetBodyPathData().items()}
        self._classes = list(self._class_data)


    def _init_chara_menu(self) -> None:
        """
        Completes initialization of character head dropdown menu.

        :return: None.
        """
        self._chara_string = tk.StringVar(self._master)
        self._chara_string.set(self.DEFAULT_CHARA)

        self._chara_menu = tk.OptionMenu(self._master, self._chara_string, *self._characters)
        self._chara_menu.config(
            width=self.DEFAULT_DROPDOWN_WIDTH,
            fg=self.FromRGB(*self.CHARA_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.CHARA_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.CHARA_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.CHARA_BUTTON_FG_COLOR)
            )
        self._chara_menu.grid(row=0, column=0, padx=4, pady=5)


    def _init_class_menu(self) -> None:
        """
        Completes initialization of character body dropdown menu.

        :return: None.
        """
        self._class_string = tk.StringVar(self._master)
        self._class_string.set(self.DEFAULT_CLASS)

        self._class_menu = tk.OptionMenu(self._master, self._class_string, *self._classes)
        self._class_menu.config(
            width=self.DEFAULT_DROPDOWN_WIDTH,
            fg=self.FromRGB(*self.CLASS_BUTTON_FG_COLOR),
            bg=self.FromRGB(*self.CLASS_BUTTON_BG_COLOR),
            activebackground=self.FromRGB(*self.CLASS_BUTTON_BG_COLOR),
            activeforeground=self.FromRGB(*self.CLASS_BUTTON_FG_COLOR)
            )
        self._class_menu.grid(row=0, column=1, padx=4, pady=5)


    def _init_idle_button(self) -> None:
        """
        Completes initialization of "idle composition" button.

        :return: None.
        """
        self._idle_button = tk.Button(self._master, text=self.IDLE_BUTTON_TEXT, command=self.composite_idle)
        self._idle_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._idle_button.grid(row=2, column=0, padx=4, pady=5)


    def _init_full_button(self) -> None:
        """
        Completes initialization of "full composition" button.

        :return: None.
        """
        self._full_button = tk.Button(self._master, text=self.FULL_BUTTON_TEXT, command=self.composite_full)
        self._full_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._full_button.grid(row=2, column=1, padx=4, pady=5)


    def _init_rebuild_body_button(self) -> None:
        """
        Completes initialization of "rebuild body" button.

        :return: None.
        """
        self._rebuild_body_button = tk.Button(self._master, text=self.REBUILD_BODY_TEXT, command=self.rebuild_body)
        self._rebuild_body_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._rebuild_body_button.grid(row=3, column=1, padx=4, pady=5)


    def _init_rebuild_head_button(self) -> None:
        """
        Completes initialization of "rebuild head" button.

        :return: None.
        """
        self._rebuild_head_button = tk.Button(self._master, text=self.REBUILD_HEAD_TEXT, command=self.rebuild_head)
        self._rebuild_head_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._rebuild_head_button.grid(row=3, column=0, padx=4, pady=10)


    def composite_idle(self) -> None:
        """
        Composites idle frames.

        :return: None.
        """
        try:
            # Get head key
            try:
                head = self._chara_data[self._chara_string.get()]
            except KeyError:
                raise UnspecifiedHeadException

            # Get body key
            try:
                body = self._class_data[self._class_string.get()]
            except KeyError:
                raise UnspecifiedBodyException

            # Prompt user for destination filename
            sprite_utils.FixPath(ROOT_OUTPUT_DIRECTORY)
            output = filedialog.asksaveasfilename(
                initialfile="{}_{}.png".format(head, body),
                initialdir=ROOT_OUTPUT_DIRECTORY,
                title="Save As",
                filetypes=FILETYPES
                )
            if not output:
                raise EmptyFilenameException

            # Perform sprite composition
            try:
                sprite_splitter.MainIdle(head, body, output)
            except sprite_splitter.NonexistentHeadException as e:
                raise InvalidHeadException(e.filename)
            except sprite_splitter.NonexistentBodyException as e:
                raise InvalidBodyException(e.filename)
            except cv2.error:
                raise InvalidFilenameException

            # Alert user upon success
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.SUCCESS_IDLE_MESSAGE.format(filename=os.path.basename(output))
                )

        except UnspecifiedHeadException:
            # Head not specified
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_HEAD_MESSAGE)

        except UnspecifiedBodyException:
            # Body not specified
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_BODY_MESSAGE)

        except InvalidHeadException as e:
            # Head spritesheet does not exist
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.INVALID_HEAD_MESSAGE.format(filename=e.filename))

        except InvalidBodyException as e:
            # Body spritesheet does not exist
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.INVALID_BODY_MESSAGE.format(filename=e.filename))

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_TYPE_MESSAGE)

        except EmptyFilenameException:
            pass


    def composite_full(self):
        """
        Composites full frames.

        :return: None.
        """
        try:
            # Get head key
            try:
                head = self._chara_data[self._chara_string.get()]
            except KeyError:
                raise UnspecifiedHeadException

            # Get body key
            try:
                body = self._class_data[self._class_string.get()]
            except KeyError:
                raise UnspecifiedBodyException

            # Prompt user for destination filename
            sprite_utils.FixPath(ROOT_OUTPUT_DIRECTORY)
            output = filedialog.asksaveasfilename(
                initialfile="{}_{}.png".format(head, body),
                initialdir=ROOT_OUTPUT_DIRECTORY,
                title="Save As",
                filetypes=FILETYPES
                )
            if not output:
                raise EmptyFilenameException

            # Perform sprite composition
            try:
                sprite_splitter.Main(head, body, output)
            except sprite_splitter.NonexistentHeadException as e:
                raise InvalidHeadException(e.filename)
            except sprite_splitter.NonexistentBodyException as e:
                raise InvalidBodyException(e.filename)
            except cv2.error:
                raise InvalidFilenameException

            # Alert user upon success
            tk.messagebox.showinfo(
                self.WINDOW_TITLE,
                self.SUCCESS_FULL_MESSAGE.format(filename=os.path.basename(output))
                )

        except UnspecifiedHeadException:
            # Head not specified
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_HEAD_MESSAGE)

        except UnspecifiedBodyException:
            # Body not specified
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_BODY_MESSAGE)

        except InvalidHeadException as e:
            # Head spritesheet does not exist
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.INVALID_HEAD_MESSAGE.format(filename=e.filename))

        except InvalidBodyException as e:
            # Body spritesheet does not exist
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.INVALID_BODY_MESSAGE.format(filename=e.filename))

        except InvalidFilenameException:
            # Image format not recognized
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.FAILURE_TYPE_MESSAGE)

        except EmptyFilenameException:
            pass


    def rebuild_body(self) -> None:
        """
        Rebuilds body JSON database.

        :return: None
        """
        do_rebuild = tk.messagebox.askquestion(self.WINDOW_TITLE, self.REBUILD_BODY_CONFIRM)
        if do_rebuild == "yes":
            sprite_json.CreateBodyJSON()
            self._init_class_data()
            self._init_class_menu()
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.REBUILD_BODY_MESSAGE)


    def rebuild_head(self) -> None:
        """
        Rebuilds head JSON database.

        :return: None.
        """
        do_rebuild = tk.messagebox.askquestion(self.WINDOW_TITLE, self.REBUILD_HEAD_CONFIRM)
        if do_rebuild == "yes":
            sprite_json.CreateHeadJSON()
            self._init_chara_data()
            self._init_chara_menu()
            tk.messagebox.showinfo(self.WINDOW_TITLE, self.REBUILD_HEAD_MESSAGE)


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
