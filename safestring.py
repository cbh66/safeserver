

class SafeString:
    def __init__(self, *args, **kwargs):
        self._val = str(*args)
        # set obj next and prev, or array or something
        self._prev = kwargs["prev"] if "prev" in kwargs else None
        self._next = kwargs["next"] if "next" in kwargs else None
        if self._prev is not None and not isinstance(self._prev, SafeString):
            self._prev = SafeString(self._prev)
        if self._next is not None and not isinstance(self._next, SafeString):
            self._next = SafeString(self._next)
        self._safe = kwargs["safe"] if "safe" in kwargs else True

    def unsafe_substrings(self):
        lst = []
        if self._prev is not None:
            lst.extend(self._prev.unsafe_substrings())
        if not self._safe:
            lst.append(self._val)
        if self._next is not None:
            lst.extend(self._next.unsafe_substrings())
        return lst

    def __str__(self):
        #return self.__repr__()
        representation = ""
        if self._prev is not None:
            representation += self._prev.__str__()
        representation += self._val.__str__()
        if self._next is not None:
            representation += self._next.__str__()
        return representation

    def __repr__(self):
        representation = "("
        if self._prev is not None:
            representation += "-"
            representation += self._prev.__repr__()
        if not self._safe:
            representation += "{|"
        representation += self._val.__str__()
        if not self._safe:
            representation += "|}"
        if self._next is not None:
            representation += "+"
            representation += self._next.__repr__()
        representation += ")"
        return representation

    def __len__(self):
        return (self._val.__len__() +
            (0 if self._prev is None else self._prev.__len__()) +
            (0 if self._next is None else self._next.__len__()))

    def __add__(self, other):
        if not isinstance(other, SafeString):
            other = SafeString(other)
        if self._next is None:
                return SafeString(self._val, safe=self._safe,
                                    prev=self._prev, next=other)
        return SafeString(self._val, safe=self._safe,
                                prev=self._prev,
                                next=self._next.__add__(other))

    def __radd__(self, other):
        if not isinstance(other, SafeString):
            other = SafeString(other)
        if self._prev is None:
                return SafeString(self._val, safe=self._safe,
                                    prev=other, next=self._next)
        return SafeString(self._val, safe=self._safe,
                                prev=self._prev.__radd__(other),
                                next=self._next)

    def __mul__(self, num):
        num = int(num)
        if num < 1:
            return SafeString("")
        if num == 1:
            return self
        half_num = int(num / 2)
        half = self * half_num
        rval = SafeString("", prev=half, next=half)
        if num % 2 == 1:
            rval += self
        return rval

    def __getitem__(self, key):
        pass

    def __cmp__(self, other):  ##############
        other = str(other)
        if self._prev is not None:
            cmp = self._prev.__cmp__(other[:len(self._prev._val)])
            if cmp != 0:
                return cmp
            other = other[len(self._prev):]
        cmp = str.__cmp__(self._val, other[:str.__len__(self._val)])
        if cmp != 0:
            return cmp
        other = other[str.__len__(self._val):]
        if self._next is not None:
            cmp = self._next.__cmp__(other[:len(self._next._val)])
            if cmp != 0:
                return cmp
            other = other[len(self._next):]
        if len(other) != 0:
            return 1
        return 0

    def __nonzero__(self):
        return (str.__nonzero__(self._val) or
            (self._prev is not None and self._prev.__nonzero__()) or
            (self._next is not None and self._next.__nonzero__()))



