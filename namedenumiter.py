"""
------------------------------------------------------------------------------------------------------------------------
Fire Emblem 3DS Sprite Compositing Tool
(c) 2019 Joey Navarro

Implements an iterable container for enumerated values. Not really necessary, mainly did this just
so I could tell myself I implemented something like it.

------------------------------------------------------------------------------------------------------------------------
"""


class NamedEnumIter:
    def __init__(self, *args, **kwargs):
        """
        A named, enumerated iterable.
        """
        self._iterator = 0
        self._counter = {}
        self._names = {}
        self._indices = {}
        self._num_items = 0

        for arg in args:
            self._register_attr(arg)

        for key, val in kwargs.items():
            self._register_attr(key, val)

    def _register_attr(self, attrname: str, enumeration: int = -1) -> bool:
        """
        Registers a new enumerated attribute into a NamedEnumIter object. (In-place).

        :param attrname: Name of enumeration to set.
        :param enumeration:
        :return: True on success; false otherwise.
        """
        if type(attrname) != str:
            return False
        elif type(enumeration) != int:
            return False
        else:
            if enumeration < 0:
                enumeration = self._num_items

            setattr(self, attrname, enumeration)
            self._indices[attrname] = enumeration
            self._names[enumeration] = attrname
            self._counter[self._num_items] = enumeration

            self._num_items += 1

            return True

    def __call__(self, accessor):
        """ Implements __call__. """
        return self[accessor]

    def __len__(self):
        """ Implements __len__. """
        return self._num_items

    def __iter__(self):
        """ Implements __iter__. """
        self._iterator = 0
        return self

    def __next__(self):
        """ Implements __next__. """
        if self._iterator < self._num_items:
            n = self._iterator
            self._iterator += 1
            return self._names[self._counter[n]]
        else:
            raise StopIteration

    def __getitem__(self, accessor):
        """ Implements __getitem__. """
        container = None

        if type(accessor) == int:
            container = self._names

        elif type(accessor) == str:
            container = self._indices

        if container:
            try:
                return container[accessor]
            except KeyError:
                return None
        else:
            return None
