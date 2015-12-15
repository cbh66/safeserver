
class SafeString:
    """ A SafeString contains the same information and supports the same
        operations as normal strings, with one crucial difference:
        it keeps track of the unsafe pieces that were used to create it.

        Internally, it is maintained as a binary tree of strings, where the
        represented string is built by an in-order traversal of the tree.

        As with built-in strings, SafeStrings are immutable.
    """
    def __init__(self, *args, **kwargs):
        """ Creates a SafeString.  The first argument, which is optional, is
            the string from which this object will derive its value.
            The following named argument can also be given:
            safe=True (Boolean) - Whether the string should be considered safe.
                For inputs that came from a user, this should be False.
                Defaults to True.
        """
        self._val = str(*args)
        # set obj next and prev, or array or something
        self._prev = kwargs["prev"] if "prev" in kwargs else None
        self._next = kwargs["next"] if "next" in kwargs else None
        if self._prev is not None and not isinstance(self._prev, SafeString):
            self._prev = SafeString(self._prev)
        if self._next is not None and not isinstance(self._next, SafeString):
            self._next = SafeString(self._next)
        self._safe = kwargs["safe"] if "safe" in kwargs else True


    def __instancecheck__(self, instance):
        print "here1"
        return isinstance(self, str) or isinstance(self, SafeString)

    def unsafe_substrings(self):
        """ Returns a list of all of the unsafe portions of this string,
            as an array of strings.
        """
        lst = []
        if self._prev is not None:
            lst.extend(self._prev.unsafe_substrings())
        if not self._safe:
            lst.append(self._val)
        if self._next is not None:
            lst.extend(self._next.unsafe_substrings())
        return lst

    def __str__(self):
        """ Transforms the SafeString into a string.  Note that this removes
            any information regarding safety, so should only be done if you
            are totally, 100%, completely sure that the string is safe for
            your purposes.
        """
        representation = ""
        if self._prev is not None:
            representation += self._prev.__str__()
        representation += self._val.__str__()
        if self._next is not None:
            representation += self._next.__str__()
        return representation

    def __repr__(self):
        """ Mainly for debugging.  Prints the representation of the string.
        """
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
        """ Returns the number of characters in the string.
        """
        return (self._val.__len__() +
            (0 if self._prev is None else self._prev.__len__()) +
            (0 if self._next is None else self._next.__len__()))

    def __add__(self, other):
        """ Concatenates another string onto this SafeString
        """
        if not isinstance(other, SafeString):
            other = SafeString(other)
        if len(other) == 0:
            return self
        if self._next is None:
                return SafeString(self._val, safe=self._safe,
                                    prev=self._prev, next=other)
        return SafeString(self._val, safe=self._safe,
                                prev=self._prev,
                                next=self._next.__add__(other))

    def __radd__(self, other):
        """ Concatenates this SafeString onto another string
        """
        if not isinstance(other, SafeString):
            other = SafeString(other)
        if len(other) == 0:
            return self
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
            rval = self + rval
        return rval

    def __contains__(self, other):
        return str(other) in str(self)

    def __eq__(self, other):
        if isinstance(other, SafeString):  # Special case to match str behavior
            other = str(other)
        return str(self) == other

    def __ge__(self, other):
        if isinstance(other, SafeString):  # Special case to match str behavior
            other = str(other)
        return str(self) >= other

    def __gt__(self, other):
        if isinstance(other, SafeString):  # Special case to match str behavior
            other = str(other)
        return str(self) > other

    def __le__(self, other):
        if isinstance(other, SafeString):  # Special case to match str behavior
            other = str(other)
        return str(self) <= other

    def __lt__(self, other):
        if isinstance(other, SafeString):  # Special case to match str behavior
            other = str(other)
        return str(self) < other

    def __ne__(self, other):
        if isinstance(other, SafeString):  # Special case to match str behavior
            other = str(other)
        return str(self) != other

    def capitalize(self):
        if self._prev is not None:
            return SafeString(self._val, safe=self._safe, next=self._next,
                                prev=capitalize(self._prev))
        return SafeString(capitalize(self._val), safe=self._safe,
                                next=self._next)

    def casefold(self):
        prev = self._prev.casefold() if self._prev is not None else None
        next = self._next.casefold() if self._next is not None else None
        return SafeString(self._val.casefold(), safe=self._safe,
                                prev=prev, next=next)

    #### - center() not supported; a bit too tricky to deal with
    #         the separate pieces of the string

    def count(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).count(sub, *args, **kwargs)

    def encode(self, *args, **kwargs):
        prev = self._prev.encode(*args, **kwargs) if self._prev is not None else None
        next = self._next.encode(*args, **kwargs) if self._next is not None else None
        return SafeString(self._val.encode(*args, **kwargs), safe=self._safe,
                                prev=prev, next=next)

    def endswith(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).endswith(sub, *args, **kwargs)

    def expandtabs(self, *args, **kwargs):
        prev = self._prev.expandtabs(*args, **kwargs) if self._prev is not None else None
        next = self._next.expandtabs(*args, **kwargs) if self._next is not None else None
        return SafeString(self._val.expandtabs(*args, **kwargs),
                                safe=self._safe, prev=prev, next=next)

    def find(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).find(sub, *args, **kwargs)

    def index(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).index(sub, *args, **kwargs)

    def isalnum(self):
        return str(self).isalnum()

    def isalpha(self):
        return str(self).isalpha()

    def isdecimal(self):
        return str(self).isdecimal()

    def isdigit(self):
        return str(self).isdecimal()

    def isidentifier(self):
        return str(self).isidentifier()

    def islower(self):
        return str(self).islower()

    def isnumeric(self):
        return str(self).isnumeric()

    def isprintable(self):
        return str(self).isprintable()

    def isspace(self):
        return str(self).isspace()

    def istitle(self):
        return str(self).istitle()

    def isupper(self):
        return str(self).isupper()

    def join(self, iterable):
        rval = ""
        delim = ""
        for i in iterable:
            rval += delim + i
            delim = self
        return rval

    def ljust(self, width, *args, **kwargs):
        fill = width - len(self)
        return self + "".ljust(fill, *args, **kwargs)

    def lower(self):
        prev = self._prev.lower() if self._prev is not None else None
        next = self._next.lower() if self._next is not None else None
        return SafeString(self._val.lower(), safe=self._safe,
                                prev=prev, next=next)

    #### - lstrip() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
    #         for future, lstrip each piece, recurse if it strips everything
    
    #### - partition() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
    #         for future, can find position with index, then do slicing

    #### - replace() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
    
    def rfind(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).rfind(sub, *args, **kwargs)

    def rindex(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).rfind(sub, *args, **kwargs)

    def rjust(self, width, *args, **kwargs):
        fill = width - len(self)
        return "".rjust(fill, *args, **kwargs) + self

    #### - rpartition() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
    #         for future, can find position with rindex, then do slicing

    #### - rsplit() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
  
    #### - rstrip() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
    #         for future, rstrip each piece, do self if it strips everything

    #### - splitlines() not supported; a bit too tricky to deal with
    #         the separate pieces of the string

    def startswith(self, sub, *args, **kwargs):
        if isinstance(sub, SafeString):
            sub = str(sub)
        return str(self).startswith(sub, *args, **kwargs)

    #### - strip() not supported; a bit too tricky to deal with
    #         the separate pieces of the string
    #         for future, rstrip each piece, do self if it strips everything

    def swapcase(self):
        prev = self._prev.swapcase() if self._prev is not None else None
        next = self._next.swapcase() if self._next is not None else None
        return SafeString(self._val.swapcase(), safe=self._safe,
                                prev=prev, next=next)

    #### - title() not supported; a bit too tricky to deal with
    #         the separate pieces of the string

    def translate(self, t):
        prev = self._prev.translate(t) if self._prev is not None else None
        next = self._next.translate(t) if self._next is not None else None
        return SafeString(self._val.translate(t), safe=self._safe,
                                prev=prev, next=next)

    def upper(self):
        prev = self._prev.upper() if self._prev is not None else None
        next = self._next.upper() if self._next is not None else None
        return SafeString(self._val.upper(), safe=self._safe,
                                prev=prev, next=next)

    def zfill(self, width):
        fill = width - len(self)
        return ('0' * fill) + self

