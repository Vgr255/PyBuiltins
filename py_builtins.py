"""Pure Python implementations of built-in functions.
This can be used to get a good idea of how built-in types and functions work."""

__author__ = "'Vgr' E. Barry"

# all of the built-in functions and types which could be implemented
# in pure Python has been done, with the exception of compile.
# compile will take some time to do, so for now this will do

import sys as _sys
import _codecs

_builtin_slice = slice # need to keep it around for proper slice checking

_characters = ("\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f" +
               "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f" +
               " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`" +
               "abcdefghijklmnopqrstuvwxyz{|}~\x7f" +
               "\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f" +
               "\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0" +
               "¡¢£¤¥¦§¨©ª«¬\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞ" +
               "ßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ")

# private behind-the-scenes functions

def _argument(func):
    """Single-argument decorator."""
    def inner(*arg, **keyword):
        for name in keyword:
            if name != arg_name:
                raise TypeError("%s() got an unexpected keyword argument: %r" % (func_name, name))
        if len(arg) > arg_count + 1:
            raise TypeError("%s expected at most %i arguments, got %i" % (func_name, arg_count + 1, len(arg)))
        if arg and keyword:
            raise TypeError("%s() got multiple values for argument %r" % (func_name, arg_name))

        if keyword:
            return func(*arg + (keyword[arg_name],))
        return func(*arg)

    code = func.__code__
    arg_count = code.co_argcount
    func_name = code.co_name
    arg_name = code.co_varnames[arg_count]

    inner.__name__ = func.__name__
    inner.__doc__ = func.__doc__

    if _sys.version_info >= (3, 3):
        inner.__qualname__ = func.__qualname__

    return inner

def _max_min_caller(func):
    """Proper handler for the max() and min() functions."""
    def inner(*iterable, key=None, **default):
        for name in default:
            if name != "default":
                raise TypeError("%s() got an unexpected keyword argument: %r" % (func_name, name))
        if not iterable and not default:
            raise TypeError("%s expected at least 1 arguments, got 0" % func_name)
        if not iterable and default:
            return default["default"]

        if len(iterable) == 1:
            iterable = iterable[0]

        return func(iterable, key)

    code = func.__code__
    arg_count = code.co_argcount
    func_name = code.co_name

    inner.__name__ = func.__name__
    inner.__doc__ = func.__doc__

    if _sys.version_info >= (3, 3):
        inner.__qualname__ = func.__qualname__

    return inner

def _iter(callable, sentinel):
    """Two-arguments form of iter()."""
    while True:
        result = callable()
        if result != sentinel:
            yield result
        else:
            return

def _change_base(number, base, fill=1):
    """Function behind bin(), hex() and oct()."""
    if not hasattr(number, "__index__"):
        raise TypeError("%r object cannot be interpreted as an integer" % type(num).__name__)
    if not (2 <= base <= 36):
        raise ValueError("base must be >= 2 and <= 36")

    values = ("0123456789abcdefghijklmnopqrstuvwxyz")[:base]

    num = 0
    while base ** num < number + 1:
        num += 1

    total = [0] * num

    while num:
        value = number // base ** (num - 1)
        total[-num] = values[value]
        number -= base ** (num - 1) * value
        num -= 1

    if len(total) % fill:
        return "".join(total).zfill(len(total) + (fill - len(total) % fill))

    return "".join(total)

# Actual functions and classes in alphabetical order from this point on

def abs(num):
    """abs(number) -> number

    Return the absolute value of the argument.

    Changes over built-in function:
    None
    """

    if hasattr(type(num), "__abs__"):
        return type(num).__abs__(num)

    raise TypeError("bad operand type for abs(): %r" % type(num).__name__)

def all(*iterable):
    """all(iterable[, items]) -> bool

    Return True if bool(x) is True for all values x in the iterable.
    If the iterable is empty, return True.

    Changes over built-in function:
    + Support for multiple arguments

    all(a, b, c) == all((a, b, c))
    """

    if not iterable:
        raise TypeError("all expected at least 1 arguments, got 0")
    if len(iterable) == 1:
        iterable = iterable[0]
    for item in iterable:
        if not item:
            return False
    return True

def any(*iterable):
    """any(iterable) -> bool

    Return True if bool(x) is True for any x in the iterable.
    If the iterable is empty, return False.

    Changes over built-in function:
    + Support for multiple arguments

    any(a, b, c) == any((a, b, c))
    """

    if not iterable:
        raise TypeError("any expected at least 1 arguments, got 0")
    if len(iterable) == 1:
        iterable = iterable[0]
    for item in iterable:
        if item:
            return True
    return False

def ascii(object):
    r"""ascii(object) -> string

    As repr(), return a string containing a printable representation of an
    object, but escape the non-ASCII characters in the string returned by
    repr() using \x, \u or \U escapes.  This generates a string similar
    to that returned by repr() in Python 2.

    Changes over built-in function:
    None
    """

    string = list(repr(object))
    for i, char in enumerate(string):
        if 127 < ord(char) < 256:
            x = hex(ord(char)).replace("0x", "\\x")
        elif 255 < ord(char):
            x = hex(ord(char)).replace("0x", "\\u")
        else:
            continue

        if len(x) % 2:
            x = x[:2] + "0" + x[2:]
        string[i] = x

    return "".join(string)

def bin(number):
    """bin(number) -> string

    Return the binary representation of an integer.

       >>> bin(2796202)
       '0b1010101010101010101010'

    Changes over built-in function:
    None
    """

    return "0b" + _change_base(number, 2)

def callable(object):
    """callable(object) -> bool

    Return whether the object is callable (i.e., some kind of function).
    Note that classes are callable, as are instances of classes with a
    __call__() method.

    Changes over built-in function:
    None
    """

    return hasattr(object, "__call__")

def chr(num):
    """chr(i) -> Unicode character

    Return a Unicode string of one character with ordinal i; 0 <= i <= 0x10ffff.

    Changes over built-in function:
    None
    """

    if not hasattr(num, "__index__"):
        raise TypeError("an integer is required (got type %s)" % type(num).__name__)
    if num not in range(0x110000):
        raise ValueError("chr() arg not in range(0x110000)")
    if num < 256:
        return _characters[num]

    return _codecs.unicode_escape_decode("\\u" + _change_base(num, 16, 4))[0]

class classmethod:
    """classmethod(function) -> method

    Convert a function to be a class method.

    A class method receives the class as implicit first argument,
    just like an instance method receives the instance.
    To declare a class method, use this idiom:

      class C:
          def f(cls, arg1, arg2, ...): ...
          f = classmethod(f)

    It can be called either on the class (e.g. C.f()) or on an instance
    (e.g. C().f()).  The instance is ignored except for its class.
    If a class method is called for a derived class, the derived class
    object is passed as the implied first argument.

    Class methods are different than C++ or Java static methods.
    If you want those, see the staticmethod class.

    Changes over built-in type:
    None
    """

    def __init__(self, function):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.__isabstractmethod__ = getattr(function, "__isabstractmethod__", False)
        self.__func__ = function

    def __get__(self, instance, owner):
        """Return an attribute of instance, which is of type owner."""
        def inner(*args, **kwargs):
            return self.__func__(owner, *args, **kwargs)

        inner.__name__ = self.__func__.__name__
        inner.__doc__ = self.__func__.__doc__

        if _sys.version_info >= (3, 3):
            inner.__qualname__ = self.__func__.__qualname__

        return inner

# def compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1):
# the most ironic of all functions; compiled bytecode to create compiled bytecode - genius!
# this one is still to-do... will get around to it sooner or later

def delattr(object, attribute):
    """delattr(object, name)

    Delete a named attribute on an object; delattr(x, 'y') is equivalent to
    ``del x.y''.

    Changes over built-in function:
    None
    """

    type(object).__delattr__(object, attribute)

@_argument
def dir(*object):
    """dir([object]) -> list of strings

    If called without an argument, return the names in the current scope.
    Else, return an alphabetized list of names comprising (some of) the attributes
    of the given object, and of attributes reachable from it.
    If the object supplies a method named __dir__, it will be used; otherwise
    the default dir() logic is used and returns:
      for a module object: the module's attributes.
      for a class object:  its attributes, and recursively the attributes
        of its bases.
      for any other object: its attributes, its class's attributes, and
        recursively the attributes of its class's base classes.

    Changes over built-in function:
    + Support for the 'object' keyword argument as well as positional
    """

    if object:
        return sorted(type(object[0]).__dir__(object[0]))

    return sorted(_sys._getframe(2).f_locals) # need to go out of the decorator scope

def divmod(number, mod):
    """divmod(x, y) -> (div, mod)

    Return the tuple ((x-x%y)/y, x%y).  Invariant: div*y + mod == x.

    Changes over built-in function:
    None
    """

    if hasattr(type(number), "__divmod__"):
        result = type(number).__divmod__(number, mod)
        if result is not NotImplemented:
            return result

    raise TypeError("unsupported operand type(s) for divmod(): %r and %r" % (type(number).__name__, type(mod).__name__))

class enumerate:
    """enumerate(iterable[, start]) -> iterator for index, value of iterable

    Return an enumerate object.  iterable must be another object that supports
    iteration.  The enumerate object yields pairs containing a count (from
    start, which defaults to zero) and a value yielded by the iterable argument.
    enumerate is useful for obtaining an indexed list:
        (0, seq[0]), (1, seq[1]), (2, seq[2]), ...

    Changes over built-in type:
    None
    """

    def __init__(self, iterable, start=0):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.iterator = iter(iterable)
        self.index = start

    def __iter__(self):
        """Implement iter(self)."""
        return self

    def __next__(self):
        """Implement next(self)."""
        self.index += 1
        return self.index - 1, next(self.iterator)

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), (self.iterator, self.index)

class filter:
    """filter(function or None, iterable) --> filter object

    Return an iterator yielding those items of iterable for which function(item)
    is true. If function is None, return the items that are true.

    Changes over built-in type:
    None
    """

    def __init__(self, callable, iterable):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.callable = callable
        self.iterator = iter(iterable)

    def __iter__(self):
        """Implement iter(self)."""
        return self

    def __next__(self):
        """Implement next(self)."""
        caller = bool if self.callable is None else self.callable
        value = next(self.iterator)
        if caller(value):
            return value
        return next(self)

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), (self.callable, self.iterator)

def format(value, format_spec=""):
    """format(value[, format_spec]) -> string

    Returns value.__format__(format_spec)
    format_spec defaults to ""

    Changes over built-in function:
    None
    """

    return type(value).__format__(value, format_spec)

@_argument
def getattr(object, attribute, *fallback):
    """getattr(object, name[, default]) -> value

    Get a named attribute from an object; getattr(x, 'y') is equivalent to x.y.
    When a default argument is given, it is returned when the attribute doesn't
    exist; without it, an exception is raised in that case.

    Changes over built-in function:
    + Support for the 'fallback' keyword argument as well as positional
    """

    try:
        return type(object).__getattribute__(object, attribute)
    except AttributeError:
        try:
            return type(object).__getattr__(object, attribute)
        except AttributeError:
            try:
                return object.__dict__[attribute]
            except (AttributeError, KeyError):
                if fallback:
                    return fallback[0]

    raise AttributeError("%r object has no attribute %r" % (type(object).__name__, attribute))

def globals():
    """globals() -> dictionary

    Return the dictionary containing the current scope's global variables.

    Changes over built-in function:
    None
    """

    return _sys._getframe(1).f_globals

def hasattr(object, attribute):
    """hasattr(object, name) -> bool

    Return whether the object has an attribute with the given name.
    (This is done by calling getattr(object, name) and catching AttributeError.)

    Changes over built-in function:
    None
    """

    try:
        getattr(object, attribute)
    except AttributeError:
        return False
    return True

def hash(object):
    """hash(object) -> integer

    Return a hash value for the object.  Two objects with the same value have
    the same hash value.  The reverse is not necessarily true, but likely.

    Changes over built-in function:
    - Hash value is not truncated
    """

    for obj in type(object).__mro__:
        if "__hash__" in obj.__dict__:
            if obj.__dict__["__hash__"] is None:
                break
            return obj.__dict__["__hash__"](object)

    raise TypeError("unhashable type: %r" % obj.__name__)

def hex(number):
    """hex(number) -> string

    Return the hexadecimal representation of an integer.

       >>> hex(3735928559)
       '0xdeadbeef'

    Changes over built-in function:
    None
    """

    return "0x" + _change_base(number, 16)

def id(obj):
    """id(object) -> integer

    Return the identity of an object.  This is guaranteed to be unique among
    simultaneously existing objects.  (Hint: it's the object's memory address.)

    Changes over built-in function:
    None
    """

    return int(object.__repr__(obj)[object.__repr__(obj).index("0x"):-1], 16)

def isinstance(object, types):
    """isinstance(object, class-or-type-or-tuple) -> bool

    Return whether an object is an instance of a class or of a subclass thereof.
    With a type as second argument, return whether that is the object's type.
    The form using a tuple, isinstance(x, (A, B, ...)), is a shortcut for
    isinstance(x, A) or isinstance(x, B) or ... (etc.).

    Changes over built-in function:
    None
    """

    if "__instancecheck__" in type(types).__dict__:
        return type(types).__dict__["__instancecheck__"](types, object)

    if type(object) == types:
        return True

    if isinstance(types, tuple): # this is a recursive call
        for type_ in types:
            if isinstance(object, type_):
                return True

    if not isinstance(types, (tuple, type)):
        raise TypeError("isinstance() arg 2 must be a type or tuple of types")

    return False

def issubclass(cls, classes):
    """issubclass(C, B) -> bool

    Return whether class C is a subclass (i.e., a derived class) of class B.
    When using a tuple as the second argument issubclass(X, (A, B, ...)),
    is a shortcut for issubclass(X, A) or issubclass(X, B) or ... (etc.).

    Changes over built-in function:
    None
    """

    if "__subclasscheck__" in type(classes).__dict__:
        return type(classes).__dict__["__subclasscheck__"](classes, cls)

    if not isinstance(cls, type):
        raise TypeError("issubclass() arg 1 must be a class")

    if not isinstance(classes, (tuple, type)):
        raise TypeError("issubclass() arg 2 must be a class or tuple of classes")

    if classes in cls.__mro__:
        return True

    if isinstance(classes, tuple):
        for class_ in classes:
            if issubclass(cls, class_):
                return True

    return False

@_argument
def iter(iterable, *sentinel):
    """iter(iterable) -> iterator
    iter(callable, sentinel) -> iterator

    Get an iterator from an object.  In the first form, the argument must
    supply its own iterator, or be a sequence.
    In the second form, the callable is called until it returns the sentinel.

    Changes over built-in function:
    + Support for the 'sentinel' keyword argument as well as parameter
    """

    if sentinel:
        it = _iter(iterable, sentinel[0])
        it.send(None)
        return it

    if hasattr(type(iterable), "__iter__"):
        return type(iterable).__iter__(iterable)

    raise TypeError("%r object is not iterable" % type(iterable).__name__)

def len(object):
    """len(object)

    Return the number of items of a sequence or mapping.

    Changes over built-in function:
    None
    """

    if "__len__" in type(object).__dict__:
        return type(object).__dict__["__len__"](object)

    raise TypeError("object of type %r has no len()" % type(object).__name__)

def locals():
    """locals() -> dictionary

    Update and return a dictionary containing the current scope's local variables.

    Changes over built-in function:
    None
    """

    return _sys._getframe(1).f_locals

class map:
    """map(func, *iterables) --> map object

    Make an iterator that computes the function using arguments from
    each of the iterables.  Stops when the shortest iterable is exhausted.

    Changes from the built-in type:
    None
    """

    def __init__(self, func, *iterables):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.function = func
        self.iterators = tuple(iter(iterable) for iterable in iterables)

    def __iter__(self):
        """Implement iter(self)."""
        return self

    def __next__(self):
        """Implement next(self)."""
        args = []
        for iterator in self.iterators:
            try:
                args.append(next(iterator))
            except StopIteration:
                break
        else:
            return self.function(*args)

        raise StopIteration

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), (self.function,) + self.iterators

@_max_min_caller
def max(iterable, key):
    """max(iterable[, key=func]) -> value
    max(a, b, c, ...[, key=func]) -> value

    With a single iterable argument, return its largest item.
    With two or more arguments, return the largest argument.

    Changes over built-in function:
    None
    """

    for item in iterable:
        if "highest" in locals():
            if key is not None:
                if highest < key(item):
                    highest = item
            elif highest < item:
                highest = item
        else:
            highest = item

    return highest

@_max_min_caller
def min(iterable, key):
    """min(iterable[, key=func]) -> value
    min(a, b, c, ...[, key=func]) -> value

    With a single iterable argument, return its smallest item.
    With two or more arguments, return the smallest argument.

    Changes over built-in function:
    None
    """

    for item in iterable:
        if "lowest" in locals():
            if key is not None:
                if key(item) < lowest:
                    lowest = item
            elif item < lowest:
                lowest = item
        else:
            lowest = item

    return lowest

@_argument
def next(iterator, *default):
    """next(iterator[, default])

    Return the next item from the iterator. If default is given and the iterator
    is exhausted, it is returned instead of raising StopIteration.

    Changes over built-in function:
    + Support for the 'default' keyword argument as well as positional
    """

    try:
        return iterator.__next__()
    except StopIteration:
        if default:
            return default[0]
        raise

def oct(number):
    """oct(number) -> string

    Return the octal representation of an integer.

       >>> oct(342391)
       '0o1234567'

    Changes over built-in function:
    None
    """

    return "0o" + _change_base(number, 8)

def ord(char):
    """ord(c) -> integer

    Return the integer ordinal of a one-character string.

    Changes over built-in function:
    None
    """

    if not isinstance(char, (str, bytes, bytearray)):
        raise TypeError("ord() expected string of length 1, but %s found" % type(char).__name__)
    if len(char) > 1:
        raise TypeError("ord() expected a character, but string of length %i found" % len(char))
    if isinstance(char, (bytes, bytearray)):
        return char[0]
    if char in _characters:
        return _characters.index(char)
    return int(_codecs.unicode_escape_encode(char)[0].decode("utf-8")[2:], 16)

@_argument
def pow(number, exponent, *modulo):
    """pow(x, y[, z]) -> number

    With two arguments, equivalent to x**y.  With three arguments,
    equivalent to (x**y) % z, but may be more efficient (e.g. for ints).

    Changes over built-in function:
    + Support for the 'modulo' keyword argument as well as positional
    """

    if hasattr(type(number), "__pow__"):
        if modulo:
            result = type(number).__pow__(number, exponent, modulo[0])
        else:
            result = type(number).__pow__(number, exponent)

        if result is not NotImplemented:
            return result

    if hasattr(type(exponent), "__rpow__"):
        result = type(exponent).__rpow__(exponent, number)
        if result is not NotImplemented:
            return result

    raise TypeError("unsupported operand type(s) for ** or pow(): %r and %r" %
                    (type(number).__name__, type(exponent).__name__))

def print(*output, sep=" ", end="\n", file=_sys.stdout, flush=False):
    r"""print(value, ..., sep=' ', end='\n', file=sys.stdout, flush=False)

    Prints the values to a stream, or to sys.stdout by default.
    Optional keyword arguments:
    file:  a file-like object (stream); defaults to the current sys.stdout.
    sep:   string inserted between values, default a space.
    end:   string appended after the last value, default a newline.
    flush: whether to forcibly flush the stream.

    Changes over built-in function:
    None
    """

    file.write(sep.join(str(x) for x in output) + end)
    if flush:
        file.flush()

class property:
    """property(fget=None, fset=None, fdel=None, doc=None) -> property attribute

    fget is a function to be used for getting an attribute value, and likewise
    fset is a function for setting, and fdel a function for del'ing, an
    attribute.  Typical use is to define a managed attribute x:

    class C(object):
        def getx(self): return self._x
        def setx(self, value): self._x = value
        def delx(self): del self._x
        x = property(getx, setx, delx, "I'm the 'x' property.")

    Decorators make defining new properties or modifying existing ones easy:

    class C(object):
        @property
        def x(self):
            "I am the 'x' property."
            return self._x
        @x.setter
        def x(self, value):
            self._x = value
        @x.deleter
        def x(self):
            del self._x

    Changes over the built-in type:
    None
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.__isabstractmethod__ = getattr(fget, "__isabstractmethod__", False)
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, instance, owner):
        """Return an attribute of instance, which is of type owner."""
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(instance)

    def __set__(self, instance, value):
        """Set an attribute of instance to value."""
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        """Delete an attribute of instance."""
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget):
        """Descriptor to change the getter on a property."""
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        """Descriptor to change the setter on a property."""
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        """Descriptor to change the deleter on a property."""
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

class range:
    """range(stop) -> range object
    range(start, stop[, step]) -> range object

    Return a virtual sequence of numbers from start to stop by step.

    Changes over built-in type:
    None
    """

    def __init__(self, start, stop=None, step=1):
        """Initialize self. See help(type(self)) for accurate signature."""
        if step == 0:
            raise ValueError("range() arg 3 must not be zero")
        if stop is None:
            start, stop = 0, start
        self.start = start
        self.stop = stop
        self.step = step

    def __iter__(self):
        """Implement iter(self)."""
        index = self.start
        mod = "__lt__" if self.step > 0 else "__gt__"
        while getattr(index, mod)(self.stop):
            yield index
            index += self.step
        raise StopIteration

    def __len__(self):
        """Return len(self)."""
        num = 0
        for i in self:
            num += 1
        return num

    def __getitem__(self, item):
        """Return self[key]."""
        if hasattr(item, "__index__"):
            if item < 0:
                item += len(self)
            for i, value in enumerate(self):
                if i == item:
                    return value

            raise IndexError("range object index out of range")

        if isinstance(item, (_builtin_slice, slice)):
            start = item.start or 0
            stop = item.stop or len(self)
            step = item.step or 1
            return range(start * self.step, stop * self.step, step * self.step)

        raise TypeError("range indices must be integers or slices, not %s" % type(item).__name__)

    def __contains__(self, item):
        """Return key in self."""
        for value in self:
            if value == item:
                return True
        return False

    def __hash__(self):
        """Return hash(self)."""
        return object.__hash__(self)

    def __eq__(self, value):
        """Return self==value."""
        values = iter(value)
        for item in self:
            try:
                if item == next(values):
                    continue
                else:
                    return False
            except StopIteration:
                return False

        return True

    def __ne__(self, value):
        """Return self!=value."""
        return not (self == value)

    def __repr__(self):
        """Return repr(self)."""
        if self.step != 1:
            return "range(%i, %i, %i)" % (self.start, self.stop, self.step)
        return "range(%i, %i)" % (self.start, self.stop)

    def __reduce__(self): # built-in range.__reduce__ method has no __doc__
        """Return state information for pickling."""
        return type(self), (self.start, self.stop, self.step)

    def count(self, value):
        """r.count(value) -> integer -- return number of occurrences of value"""
        cnt = 0
        for i in self:
            if i == value:
                cnt += 1
        return cnt

    def index(self, value, start=None, stop=None):
        """r.index(value, [start, [stop]]) -> integer -- return index of value.
           Raise ValueError if the value is not present."""
        if start is None:
            start = self.start
        if stop is None:
            stop = self.stop

        for i, num in enumerate(self):
            if start <= num < stop and i == value:
                return num

        raise ValueError("%s is not in range" % value)

def repr(object):
    """repr(object) -> string

    Return the canonical string representation of the object.
    For most object types, eval(repr(object)) == object.

    Changes over built-in function:
    None
    """

    return type(object).__repr__(object)

class reversed:
    """reversed(sequence) -> reverse iterator over values of the sequence

    Return a reverse iterator

    Changes over built-in type:
    None
    """

    def __new__(cls, iterable):
        """Create and return a new object. See help(type) for accurate signature."""
        if hasattr(type(iterable), "__reversed__"):
            return type(iterable).__reversed__(iterable)

        instance = super().__new__(cls)
        instance.iterable = iterable
        instance.index = len(iterable) - 1
        return instance

    def __iter__(self):
        """Implement iter(self)."""
        return self

    def __next__(self):
        """Implement next(self)."""
        self.index -= 1
        return self.iterable[self.index+1]

    def __length_hint__(self):
        """Private method returning an estimate of len(list(it))."""
        return self.index + 1

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), (self.iterable,), self.index

@_argument
def round(number, *ndigits):
    """round(number[, ndigits]) -> number

    Round a number to a given precision in decimal digits (default 0 digits).
    This returns an int when called with one argument, otherwise the
    same type as the number. ndigits may be negative.

    Changes over built-in function:
    + Support for the 'ndigits' keyword argument as well as positional
    """

    if hasattr(type(number), "__round__"):
        if ndigits:
            return type(number).__round__(number, ndigits[0])
        return type(number).__round__(number)

    raise TypeError("type %s doesn't define a __round__ method" % type(number).__name__)

def setattr(object, attribute, value):
    """setattr(object, name, value)

    Set a named attribute on an object; setattr(x, 'y', v) is equivalent to
    ``x.y = v''.

    Changes over built-in function:
    None
    """

    type(object).__setattr__(object, attribute, value)

class slice:
    """slice(stop)
    slice(start, stop[, step])

    Create a slice object.

    Changes over built-in type:
    - Extended slicing (e.g. a[0:10:2]
    """

    def __init__(self, stop, *args):
        """Initialize self. See help(type(self)) for accurate signature."""
        if args and len(args) > 2:
            raise TypeError("slice expected at most 3 arguments, got %i" % len(args) + 1)
        if args:
            self.start = stop
            self.stop = args[0]
            if len(args) == 2:
                self.step = args[1]
            else:
                self.step = None
        else:
            self.stop = start
            self.start = self.step = None

    def __eq__(self, value):
        """Return self==value."""
        if isinstance(value, (_builtin_slice, slice)):
            return (self.start == value.start and
                    self.stop == value.stop and
                    self.step == value.step)

        return False

    def __ne__(self, value):
        """Return self!=value."""
        return not (self == value)

    def __lt__(self, value):
        """Return self<value."""
        if isinstance(value, (_builtin_slice, slice)):
            return (self.start < value.start and
                    self.stop < value.stop and
                    self.step < value.step)

        return NotImplemented

    def __le__(self, value):
        """Return self<=value."""
        return (self == value) or self.__lt__(value)

    def __gt__(self, value):
        """Return self>value."""
        if isinstance(value, (_builtin_slice, slice)):
            return (self.start > value.start and
                    self.stop > value.stop and
                    self.step > value.step)

        return NotImplemented

    def __ge__(self, value):
        """Return self>=value."""
        return (self == value) or self.__gt__(value)

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), (self.start, self.stop, self.step)

    def indices(self, length):
        """S.indices(len) -> (start, stop, stride)

        Assuming a sequence of length len, calculate the start and stop
        indices, and the stride length of the extended slice described by
        S. Out of bounds indices are clipped in a manner consistent with the
        handling of normal slices.
        """

        start = self.start or 0
        stop = self.stop
        step = self.step or 1

        if stop is None or stop > length:
            stop = length

        return start, stop, step

def sorted(iterable, *, key=None, reverse=False):
    """sorted(iterable, key=None, reverse=False) --> new sorted list

    Changes over built-in function:
    None
    """

    new = list(iterable)
    new.sort(key=key, reverse=reverse)
    return new

class staticmethod:
    """staticmethod(function) -> method

    Convert a function to be a static method.

    A static method does not receive an implicit first argument.
    To declare a static method, use this idiom:

         class C:
         def f(arg1, arg2, ...): ...
         f = staticmethod(f)

    It can be called either on the class (e.g. C.f()) or on an instance
    (e.g. C().f()). The instance is ignored except for its class.

    Static methods in Python are similar to those found in Java or C++.
    For a more advanced concept, see the classmethod class.

    Changes over built-in type:
    None
    """

    def __init__(self, function):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.__isabstractmethod__ = getattr(function, "__isabstractmethod__", False)
        self.__func__ = function

    def __get__(self, instance, owner):
        """Return an attribute of instance, which is of type owner."""
        return self.__func__

def sum(*iterable, start=0):
    """sum(iterable[, start]) -> value

    Return the sum of an iterable of numbers (NOT strings) plus the value
    of parameter 'start' (which defaults to 0).  When the iterable is
    empty, return start.

    Changes over built-in function:
    + Support for an arbitrary number of parameters

    sum(a, b, c) == sum((a, b, c))
    """

    if isinstance(start, str):
        raise TypeError("sum() can't sum strings [use ''.join(seq) instead]")

    if not iterable:
        raise TypeError("sum expected at least 1 arguments, got 0")

    if len(iterable) == 1:
        iterable = iterable[0]

    for item in iterable:
        start += item
    return start

class super:
    """super() -> same as super(__class__, <first argument>)
    super(type) -> unbound super object
    super(type, obj) -> bound super object; requires isinstance(obj, type)
    super(type, type2) -> bound super object; requires issubclass(type2, type)
    Typical use to call a cooperative superclass method:
    class C(B):
        def meth(self, arg):
            super().meth(arg)
    This works for class methods too:
    class C(B):
        @classmethod
        def cmeth(cls, arg):
            super().cmeth(arg)

    Changes over built-in type:
    None
    """

    def __init__(self, *args):
        """Initialize self. See help(type(self)) for accurate signature."""
        if len(args) > 2:
            raise TypeError("super() takes at most 2 positional arguments (%i given)" % len(args))

        if not args:
            frame = _sys._getframe(1)
            obj = frame.f_locals[frame.f_code.co_varnames[0]]
            args = (type(obj), obj)

        if args[0] is None:
            raise TypeError("must be type, not None")

        if len(args) == 1 and isinstance(args[0], type):
            self.__self__ = None
            self.__self_class__ = None
            self.__thisclass__ = args[0]

        elif isinstance(args[1], args[0]):
            self.__self__ = args[1]
            self.__self_class__ = args[0]
            self.__thisclass__ = args[0]

        elif isinstance(args[0], type) and issubclass(args[1], args[0]):
            self.__self__ = args[1]
            self.__self_class__ = args[1]
            self.__thisclass__ = args[0]

        else:
            raise TypeError("must be type, not %s" % (args[0]).__name__)

    def __getattribute__(self, name):
        """Return getattr(self, name)."""
        def getter(func):
            def inner(*args, **kwargs):
                return func(__self__, *args, **kwargs)

            inner.__name__ = func.__name__
            inner.__doc__ = func.__doc__

            if _sys.version_info >= (3, 3):
                inner.__qualname__ = func.__qualname__

            return inner

        __self__ = object.__getattribute__(self, "__self__")
        __self_class__ = object.__getattribute__(self, "__self_class__")
        __thisclass__ = object.__getattribute__(self, "__thisclass__")

        if __self__ is __self_class__ is None:
            return object.__getattribute__(self, name)

        __mro__ = __thisclass__.__mro__
        class_index = __mro__.index(__thisclass__) + 1
        while class_index < len(__mro__):
            next_class = __mro__[class_index]
            if name in next_class.__dict__:
                if __self_class__ is __thisclass__:
                    return getter(next_class.__dict__[name])
                elif __self__ is __self_class__:
                    return next_class.__dict__[name]
            class_index += 1

        raise AttributeError(name)

    def __repr__(self):
        """Return repr(self)."""
        __self__ = object.__getattribute__(self, "__self__")
        __self_class__ = object.__getattribute__(self, "__self_class__")
        __thisclass__ = object.__getattribute__(self, "__thisclass__")

        if __self__ is __self_class__ is None:
            return "<super: <class %r>, NULL>" % __thisclass__.__name__
        if __self_class__ is __thisclass__:
            return "<super: <class %r>, <%s object>>" % ((__thisclass__.__name__,) * 2)
        if __self__ is __self_class__:
            return "<super: <class %r>, <%s object>>" % (__thisclass__.__name__, __self__.__name__)

@_argument
def vars(*object):
    """vars([object]) -> dictionary

    Without arguments, equivalent to locals().
    With an argument, equivalent to object.__dict__.

    Changes over built-in function:
    + Support for the 'object' keyword argument as well as positional
    """

    if object:
        return object[0].__dict__

    return _sys._getframe(2).f_locals

class zip:
    """zip(iter1 [,iter2 [...]]) --> zip object

    Return a zip object whose .__next__() method returns a tuple where
    the i-th element comes from the i-th iterable argument.  The .__next__()
    method continues until the shortest iterable in the argument sequence
    is exhausted and then it raises StopIteration.

    Changes over built-in type:
    None
    """

    def __init__(self, *iterables):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.iterators = tuple(iter(iterable) for iterable in iterables)
        self.length = len(min(iterables))
        self.index = 0

    def __iter__(self):
        """Implement iter(self)."""
        return self

    def __next__(self):
        """Implement next(self)."""
        if self.length > self.index + 1:
            args = []
            for iterator in self.iterators:
                args.append(next(iterator))

            self.index += 1
            return tuple(args)

        raise StopIteration

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), self.iterators
