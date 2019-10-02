"""
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Implements an iterable container for enumerated values. Not really necessary;
mainly did this just so I could tell myself I implemented something like it.

"""


class EnumItem:
    """
    An entry within a NamedEnumIter container.
    """

    def __init__(self, attr, enum):
        self._Attr = attr
        self._Enum = enum

    def __int__(self):
        return self._Enum

    def __str__(self):
        return self._Attr

    def __float__(self):
        return float(self._Enum)

    def __eq__(self, other):
        return self._Enum == other or self._Attr == other

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return self._Enum > other

    def __lt__(self, other):
        return self._Enum < other

    def __le__(self, other):
        return self._Enum <= other

    def __ge__(self, other):
        return self._Enum >= other

    def __repr__(self):
        return "{}:{}".format(self._Enum, self._Attr)

    def __add__(self, other):
        try:
            return int(self) + other
        except TypeError:
            try:
                return str(self) + other
            except TypeError:
                return NotImplemented

    def __sub__(self, other):
        try:
            return int(self) - other
        except TypeError:
            return NotImplemented

    def __mul__(self, other):
        try:
            return int(self) * other
        except TypeError:
            return NotImplemented

    def __truediv__(self, other):
        try:
            return float(self) / other
        except TypeError:
            return NotImplemented

    def __floordiv__(self, other):
        try:
            return int(self) // other
        except TypeError:
            return NotImplemented

    def __lshift__(self, other):
        try:
            return int(self) << other
        except TypeError:
            return NotImplemented

    def __rshift__(self, other):
        try:
            return int(self) >> other
        except TypeError:
            return NotImplemented

    def __and__(self, other):
        try:
            return int(self) & other
        except TypeError:
            return NotImplemented

    def __or__(self, other):
        try:
            return int(self) | other
        except TypeError:
            return NotImplemented

    def __xor__(self, other):
        try:
            return int(self) ^ other
        except TypeError:
            return NotImplemented

    def __radd__(self, other):
        try:
            return other + int(self)
        except TypeError:
            try:
                return other + str(self)
            except TypeError:
                return NotImplemented

    def __rsub__(self, other):
        try:
            return other - int(self)
        except TypeError:
            return NotImplemented

    def __rmul__(self, other):
        try:
            return other * int(self)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, other):
        try:
            return other / float(self)
        except TypeError:
            return NotImplemented

    def __rfloordiv__(self, other):
        try:
            return other // int(self)
        except TypeError:
            return NotImplemented

    def __rand__(self, other):
        try:
            return other & int(self)
        except TypeError:
            return NotImplemented

    def __ror__(self, other):
        try:
            return other | int(self)
        except TypeError:
            return NotImplemented

    def __rxor__(self, other):
        try:
            return other ^ int(self)
        except TypeError:
            return NotImplemented

    def __index__(self):
        return int(self)

    def __hash__(self):
        return hash(str(self))

    def str(self):
        return str(self)

    def int(self):
        return int(self)

    def float(self):
        return float(self)

    @property
    def string(self):
        return str(self)


class NamedEnumIter:
    """
    A named, enumerated iterable.
    """

    def __init__(self, *args, **kwargs):
        self._Counter = {}
        self._Strings = {}
        self._Indices = {}
        self._NumItems = 0
        self._Iterator = 0

        for arg in args:
            self.RegisterAttr(arg)

        for key, val in kwargs.items():
            self.RegisterAttr(key, val)

    def RegisterAttr(self, attr, enum=-1):
        """
        Registers an attribute into a NamedEnumIter object.
        (In-place).

        :param attr: Name of enumeration to set.
        :param enum: Enumerated value.

        :return: True on success; false otherwise.
        """
        if type(attr) not in (str, int):
            return False
        else:
            if enum < 0:
                enum = self._NumItems

            # Register attribute
            item = EnumItem(attr, enum)

            setattr(self, attr, item)
            self._Indices[attr] = item
            self._Strings[enum] = item

            # Increment local item count
            self._Counter[self._NumItems] = enum
            self._NumItems += 1

            return True

    def __call__(self, accessor):
        """
        Implements __call__.
        """
        return self[accessor]

    def __len__(self):
        """
        Implements __len__.
        """
        return self._NumItems

    def __iter__(self):
        """
        Implements __iter__.
        """
        self._Iterator = 0
        return self

    def __next__(self):
        """
        Implements __next__.
        """
        if self._Iterator < self._NumItems:
            n = self._Iterator
            self._Iterator += 1
            return self._Strings[self._Counter[n]]
        else:
            raise StopIteration

    def __getitem__(self, accessor):
        """
        Implements __getitem__.
        """
        container = None

        if type(accessor) == int:
            # Access by integer
            container = self._Strings

        elif type(accessor) == str:
            # Access by string
            container = self._Indices

        if container:
            try:
                return container[accessor]
            except KeyError:
                return None
        else:
            return None
