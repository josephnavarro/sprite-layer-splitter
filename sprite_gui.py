#! usr/bin/env python3
"""
------------------------------------------------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Graphical user interface layer.
------------------------------------------------------------------------------------------------------------------------
"""
import tkinter as tk
import sprite_splitter
import sprite_utils
import sprite_json
from sprite_constant import *
from tkinter import filedialog


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

    DEFAULT_DROPDOWN_WIDTH = 48
    DEFAULT_BUTTON_WIDTH = 46

    DEFAULT_CHARA = "Select head"
    DEFAULT_CLASS = "Select body"

    IDLE_BUTTON_TEXT = "Composite idle frames"
    FULL_BUTTON_TEXT = "Composite all frames"
    REBUILD_HEAD_TEXT = "Rebuild head sources"
    REBUILD_BODY_TEXT = "Rebuild body sources"


    def __init__(self, root, *args, **kwargs):
        """
        GUI layer over sprite composition tool.

        :param root:   Tkinter application instance.
        :param args:   Optional arguments to tk.Frame.
        :param kwargs: Keyword arguments to tk.Frame.
        """
        super().__init__(root, *args, **kwargs)

        self._master = root

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
        self._chara_data = {v.get("name", "---"): k for k, v in sprite_json.GetCharaPathData().items()}
        self._characters = list(self._chara_data)


    def _init_class_data(self):
        """
        Completes initialization of local character body data (as loaded from file).

        :return: None.
        """
        self._class_data = {v.get("name", "---"): k for k, v in sprite_json.GetClassPathData().items()}
        self._classes = list(self._class_data)


    def _init_chara_menu(self) -> None:
        """
        Completes initialization of character head dropdown menu.

        :return: None.
        """
        self._chara_string = tk.StringVar(self._master)
        self._chara_string.set(self.DEFAULT_CHARA)

        self._chara_menu = tk.OptionMenu(self._master, self._chara_string, *self._characters)
        self._chara_menu.config(width=self.DEFAULT_DROPDOWN_WIDTH)
        self._chara_menu.grid(row=0, column=0, padx=10, pady=5)


    def _init_class_menu(self) -> None:
        """
        Completes initialization of character body dropdown menu.

        :return: None.
        """
        self._class_string = tk.StringVar(self._master)
        self._class_string.set(self.DEFAULT_CLASS)

        self._class_menu = tk.OptionMenu(self._master, self._class_string, *self._classes)
        self._class_menu.config(width=self.DEFAULT_DROPDOWN_WIDTH)
        self._class_menu.grid(row=1, column=0, padx=10, pady=5)


    def _init_idle_button(self) -> None:
        """
        Completes initialization of "idle composition" button.

        :return: None.
        """
        self._idle_button = tk.Button(self._master, text=self.IDLE_BUTTON_TEXT, command=self.composite_idle)
        self._idle_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._idle_button.grid(row=2, column=0, padx=10, pady=10)


    def _init_full_button(self) -> None:
        """
        Completes initialization of "full composition" button.

        :return: None.
        """
        self._full_button = tk.Button(self._master, text=self.FULL_BUTTON_TEXT, command=self.composite_full)
        self._full_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._full_button.grid(row=3, column=0, padx=10, pady=10)


    def _init_rebuild_body_button(self) -> None:
        """
        Completes initialization of "rebuild body" button.

        :return: None.
        """
        self._rebuild_body_button = tk.Button(self._master, text=self.REBUILD_BODY_TEXT, command=self.rebuild_body)
        self._rebuild_body_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._rebuild_body_button.grid(row=4, column=0, padx=10, pady=10)


    def _init_rebuild_head_button(self) -> None:
        """
        Completes initialization of "rebuild head" button.

        :return: None.
        """
        self._rebuild_head_button = tk.Button(self._master, text=self.REBUILD_HEAD_TEXT, command=self.rebuild_head)
        self._rebuild_head_button.config(width=self.DEFAULT_BUTTON_WIDTH)
        self._rebuild_head_button.grid(row=5, column=0, padx=10, pady=10)


    def composite_idle(self) -> None:
        """
        Composites idle frames.

        :return: None.
        """
        try:
            head = self._chara_data[self._chara_string.get()]
            body = self._class_data[self._class_string.get()]
            sprite_utils.FixPath(ROOT_OUTPUT_DIRECTORY)

            output = filedialog.asksaveasfilename(
                initialfile="{}_{}.png".format(head, body),
                initialdir=ROOT_OUTPUT_DIRECTORY,
                title="Save As",
                filetypes=FILETYPES
                )

            sprite_splitter.MainIdle(head, body, output, )

        except KeyError:
            pass


    def composite_full(self):
        """
        Composites full frames.

        :return: None.
        """
        try:
            head = self._chara_data[self._chara_string.get()]
            body = self._class_data[self._class_string.get()]
            sprite_utils.FixPath(ROOT_OUTPUT_DIRECTORY)

            output = filedialog.asksaveasfilename(
                initialfile="{}_{}.png".format(head, body),
                initialdir=ROOT_OUTPUT_DIRECTORY,
                title="Save As",
                filetypes=FILETYPES
                )

            sprite_splitter.Main(head, body, output, )

        except KeyError:
            pass


    def rebuild_body(self):
        pass


    def rebuild_head(self):
        pass


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
