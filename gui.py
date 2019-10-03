#! usr/bin/env python3
"""
General-purpose Tkinter GUI wrapper class.
"""
import tkinter as tk
import sys
from PIL import Image, ImageTk


class EasyGUI(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        """
        Wrapper around Tkinter GUI functions.

        :param root:   Tkinter instance.
        :param args:   Positional arguments.
        :param kwargs: Keyword arguments.
        """
        super().__init__(root, *args, **kwargs)
        self._Master = root
        self._Master.resizable(self.resize_x, self.resize_y)
        self.winfo_toplevel().title(self.title)

        self._PendingJobs = {
            "event-lock": None,
        }
        self._EventLock = False

        # Menu bar
        self._BooleanVars = {}
        self._Buttons = {}
        self._Canvases = {}
        self._Checkboxes = {}
        self._Entries = {}
        self._Frames = {}
        self._Labels = {}
        self._Menus = {"main-menu": tk.Menu(self._Master)}
        self._OptionMenus = {}
        self._RadioButtons = {}
        self._StringVars = {}

        self.init_all_frames()
        self.init_all_buttons()
        self.init_all_canvases()
        self.init_all_checkboxes()
        self.init_all_entries()
        self.init_all_labels()
        self.init_all_menus()
        self.init_all_optionmenus()
        self.init_all_radiobuttons()

    @property
    def colors(self) -> dict:
        """
        Standard colors for local widgets.

        :return: Dictionary mapping widget keys to respective colors.
        """
        raise NotImplementedError

    @property
    def event_lock_delay(self) -> int:
        """
        Time delay for event locking.

        :return: Event lock delay in milliseconds.
        """
        raise NotImplementedError

    @property
    def grid(self) -> dict:
        """
        Grid positions for local widgets.

        :return: Dictionary mapping widget keys to gridded positions.
        """
        raise NotImplementedError

    @property
    def images(self) -> dict:
        """
        Paths to standardized local images.

        :return: Dictionary mapping widget keys to image paths (if any).
        """
        raise NotImplementedError

    @property
    def labels(self) -> dict:
        """
        String labels for various local widgets.

        :return: Dictionary mapping widget keys to labels (if any).
        """
        raise NotImplementedError

    @property
    def messages(self) -> dict:
        """
        String messages. (Prompts, alerts, etc.)

        :return: Dictionary mapping widget keys to messages (if any).
        """
        raise NotImplementedError

    @property
    def pad(self) -> dict:
        """
        Standard padding for local widgets.

        :return: Dictionary mapping widget keys to padding data.
        """
        raise NotImplementedError

    @property
    def sizes(self) -> dict:
        """
        Standard sizes for local widgets.

        :return:
        """
        raise NotImplementedError

    @property
    def resize_x(self) -> bool:
        """
        Whether to allow horizontal resizing.

        :return: Boolean representing horizontal resizing flag.
        """
        raise NotImplementedError

    @property
    def resize_y(self) -> bool:
        """
        Whether to allow vertical resizing.

        :return: Boolean representing vertical resizing flag.
        """
        raise NotImplementedError

    @property
    def title(self) -> str:
        """
        String title for GUI application.

        :return: String title.
        """
        raise NotImplementedError

    @staticmethod
    def from_rgb(r, g, b) -> str:
        """
        Converts an RGB sequence into a Tkinter-recognized color string.

        :param r: Red channel (0-255).
        :param g: Green channel (0-255).
        :param b: Blue channel (0-255).

        :return: Color string usable by Tkinter.
        """
        return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)

    @staticmethod
    def is_windows() -> bool:
        """
        Checks whether current platform is Windows.

        :return: True if running Windows; false otherwise.
        """
        return sys.platform == "win32"

    @staticmethod
    def is_osx() -> bool:
        """
        Checks whether current platform is OS X.

        :return: True if running Mac OS X; false otherwise.
        """
        return sys.platform == "darwin"

    @staticmethod
    def open_image(path, w, h, antialias=True) -> ImageTk.PhotoImage:
        """
        Opens an image from file into a Tkinter-compatible format.

        :param path:      Relative path to image.
        :param w:         Width to resize to.
        :param h:         Height to resize to.
        :param antialias: Whether to antialias. (Default True).

        :return: Tkinter PhotoImage object.
        """
        image = Image.open(path)
        aliasing = Image.ANTIALIAS if antialias else Image.NEAREST
        return ImageTk.PhotoImage(image.resize((w, h), aliasing))

    @staticmethod
    def replace_widget(container, tag, widget) -> None:
        """
        Replaces a local widget by key.

        :param container: Target container of widgets.
        :param tag:       Tag of widget to replace.
        :param widget:    Widget instance to replace with.

        :return: None.
        """
        try:
            container[tag].destroy()
        except KeyError:
            pass
        container[tag] = widget

    @staticmethod
    def toggle_radio(radiobutton, selected) -> None:
        """
        Toggles a radio button.

        :param radiobutton: Radio button to toggle.
        :param selected:    Whether radio button should be selected.

        :return: None.
        """
        if selected:
            radiobutton.select()
        else:
            radiobutton.deselect()

    def acquire_event_lock(self) -> bool:
        """
        Safely acquires the local event lock.

        :return: True if event lock was set; False otherwise.
        """
        if not self._EventLock:
            self._EventLock = True
            return True
        else:
            return False

    def cancel_pending(self, key) -> bool:
        """
        Cancels a pending callback function.

        :param key: Key of task to cancel.

        :return: True.
        """
        job = self._PendingJobs.get(key, None)
        if job is not None:
            self.after_cancel(job)

        return True

    def do_press_button(self, key) -> bool:
        """

        :param key:

        :return: True.
        """
        try:
            button = self._Buttons[key]
            if self.is_osx():
                button.config(
                    highlightbackground=self.from_rgb(*self.colors[key]["fg"])
                )
            else:
                button.config(relief=tk.SUNKEN)
        except KeyError:
            pass

        return True

    def do_release_event_lock(self) -> bool:
        """

        :return:
        """
        self._EventLock = False
        return True

    def do_unpress_button(self, key) -> bool:
        """

        :param key:
        :return:
        """
        try:
            button = self._Buttons[key]
            if self.is_osx():
                button.config(
                    highlightbackground=self.from_rgb(*self.colors[key]["bg"])
                )
            else:
                button.config(relief=tk.RAISED)
        except KeyError:
            pass

        return True

    def get_boolean_var(self, key) -> tk.BooleanVar:
        """

        :param key:

        :return:
        """
        try:
            var = self._BooleanVars[key]
        except KeyError:
            var = self._BooleanVars[key] = tk.BooleanVar()
        return var

    def get_button(self, key) -> tk.Button:
        """

        :param key:

        :return:
        """
        try:
            button = self._Buttons[key]
        except KeyError:
            button = self._Buttons[key] = tk.Button()
        return button

    def get_canvas(self, key) -> tk.Canvas:
        """

        :param key:

        :return:
        """
        try:
            canvas = self._Canvases[key]
        except KeyError:
            canvas = self._Canvases[key] = tk.Canvas()
        return canvas

    def get_frame(self, key) -> tk.Frame:
        """

        :param key:

        :return: Frame.
        """
        try:
            frame = self._Frames[key]
        except KeyError:
            frame = self._Frames[key] = tk.Frame()
        return frame

    def get_string_var(self, key) -> tk.StringVar:
        """

        :param key:

        :return:
        """
        try:
            var = self._StringVars[key]
        except KeyError:
            var = self._StringVars[key] = tk.StringVar(self._Master)
        return var

    def init_all_buttons(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_canvases(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_checkboxes(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_entries(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_frames(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_labels(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_menus(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_optionmenus(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_all_radiobuttons(self) -> bool:
        """

        :return:
        """
        raise NotImplementedError

    def init_button(self, master, tag, command, pressed=False) -> bool:
        """

        :param master:
        :param tag:
        :param command:
        :param pressed:

        :return:
        """
        w, h = self.sizes.get(tag, self.sizes["default-button"])
        fg = self.from_rgb(*self.colors[tag]["fg"])
        bg = self.from_rgb(*self.colors[tag]["bg"])

        path = self.images.get(tag, "")
        if path:
            image = self.open_image(path, w, h)
        else:
            image = None

        button = tk.Button(master, text=self.labels[tag], command=command)
        button.image = image
        button.config(
            width=w,
            height=h,
            foreground=fg,
            background=bg,
            activebackground=bg,
            activeforeground=fg,
            image=image,
        )

        if self.is_windows():
            if pressed:
                button.config(relief=tk.SUNKEN)
            else:
                button.config(relief=tk.RAISED)
        else:
            if pressed:
                button.config(
                    highlightbackground=fg,
                    highlightcolor=bg,
                )
            else:
                button.config(
                    highlightbackground=bg,
                    highlightcolor=bg,
                )

        button.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
        )

        self.replace_widget(self._Buttons, tag, button)

        return True

    def init_canvas(self, master, tag, border) -> bool:
        """

        :param master:
        :param tag:
        :param border:

        :return:
        """
        canvas = tk.Canvas(
            master,
            width=self.sizes[tag][0],
            height=self.sizes[tag][1],
            background=self.from_rgb(*self.colors[tag]["bg"]),
            relief=tk.SUNKEN,
            borderwidth=border,
        )

        canvas.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
        )

        self.replace_widget(self._Canvases, tag, canvas)

        return True

    def init_checkbox(self, master, tag, sticky, command=None) -> bool:
        """

        :param master:
        :param tag:
        :param sticky:
        :param command:

        :return:
        """
        checkbox = tk.Checkbutton(
            master,
            text=self.labels[tag],
            variable=self.get_boolean_var(tag),
        )

        checkbox.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
            sticky=sticky,
            command=command,
        )

        self.replace_widget(self._Checkboxes, tag, checkbox)

        return True

    def init_entry(self,
                   master,
                   tag,
                   sticky,
                   text="",
                   disabled=True,
                   justify=tk.LEFT) -> bool:
        """

        :param master:
        :param tag:
        :param sticky:
        :param text:
        :param disabled:
        :param justify:

        :return:
        """
        var = self.get_string_var(tag)
        var.set(text)

        entry = tk.Entry(
            master,
            textvariable=var,
            width=self.sizes[tag][0],
            justify=justify,
        )

        entry.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
            sticky=sticky,
        )

        if disabled:
            entry.config(state="readonly")

        self.replace_widget(self._Entries, tag, entry)

        return True

    def init_frame(self, master, tag) -> bool:
        """

        :param master:
        :param tag:

        :return:
        """
        frame = tk.Frame(
            master,
            width=self.sizes[tag][0],
            height=self.sizes[tag][1],
        )

        frame.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
        )

        self.replace_widget(self._Frames, tag, frame)

        return True

    def init_label(self, master, tag, font, sticky, *args) -> bool:
        """

        :param master:
        :param tag:
        :param font:
        :param sticky:
        :param args:

        :return:
        """
        try:
            text = self.labels[tag].format(*args)
        except IndexError:
            text = self.labels[tag]

        label = tk.Label(master, font=font, text=text)
        label.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
            sticky=sticky,
        )

        self.replace_widget(self._Labels, tag, label)

        return True

    def init_menu(self, master, tag, *commands, **kwargs) -> bool:
        """

        :param master:
        :param tag:
        :param commands:
        :param kwargs:

        :return:
        """
        assert tag != "main-menu"

        get_string_var = self.get_string_var
        menu = tk.Menu(master, tearoff=0)
        labels = self.labels

        for command in commands:
            ntag = command.get("label", "")
            fnc = command.get("command", lambda: print())
            menu.add_command(label=ntag, command=fnc)

        self.replace_widget(self._Menus, tag, menu)
        self._Menus["main-menu"].add_cascade(label=labels[tag], menu=menu)

        # Initialize radiobuttons (if any)
        radiobuttons = kwargs.get("radio", {})
        if radiobuttons:
            for k, v in radiobuttons.items():
                label = labels[k]
                variable = get_string_var(v["variable"])
                command = v.get("command", None)
                value = v.get("value", "")
                menu.add_radiobutton(
                    label=label,
                    value=value,
                    variable=variable,
                    command=command,
                )

        return True

    def init_option_menu(self, master, tag, options) -> bool:
        """

        :param master:
        :param tag:
        :param options:

        :return:
        """
        width = self.sizes["default-menu"][0]
        fg = self.from_rgb(*self.colors[tag]["fg"])
        bg = self.from_rgb(*self.colors[tag]["bg"])
        var = self.get_string_var(tag)
        var.set(self.labels[tag])

        optionmenu = tk.OptionMenu(master, var, *options)
        optionmenu.config(
            width=width,
            foreground=fg,
            background=bg,
            activeforeground=fg,
            activebackground=bg,
        )

        optionmenu.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
        )

        self.replace_widget(self._OptionMenus, tag, optionmenu)

        return True

    def init_radio(self,
                   master,
                   tag,
                   variable,
                   value,
                   sticky,
                   *,
                   select=False,
                   command=None) -> bool:
        """

        :param master:
        :param tag:
        :param variable:
        :param value:
        :param sticky:
        :param select:
        :param command:

        :return:
        """
        radio = tk.Radiobutton(
            master,
            text=self.labels[tag],
            variable=variable,
            value=value,
            command=command,
        )

        radio.grid(
            row=self.grid[tag][0],
            column=self.grid[tag][1],
            padx=self.pad[tag][0],
            pady=self.pad[tag][1],
            sticky=sticky,
        )

        self.toggle_radio(radio, select)
        self.replace_widget(self._RadioButtons, tag, radio)

        return True

    def release_event_lock(self) -> bool:
        """

        :return: True
        """
        self.cancel_pending("event-lock")
        self.set_pending(
            "event-lock",
            self.do_release_event_lock,
            self.event_lock_delay
        )
        return True

    def set_pending(self, key, callback, delay) -> bool:
        """

        :param key:
        :param callback:
        :param delay:

        :return: True
        """
        self._PendingJobs[key] = self.after(delay, callback)
        return True

    def thread_it(self, callback):
        """

        :param callback:

        :return:
        """
        def function():
            self.acquire_event_lock()
            callback()
            # threading.Thread(target=callback).start()
            self.release_event_lock()

        return function
