"""Pure Python implementations of built-in functions and classes.
This can be used to get a good idea of how built-in types and functions work.
This is not meant to be used normally in development."""

__author__ = "'Vgr' E. Barry"

# tags for functions:

# UNSAFE: Do *not* use this function in production
# WRAPPER: Pure Python implementation is too tricky; this is a wrapper around the built-in

# these modules are already imported when Python starts - therefore we waste no time importing them

import sys as _sys
import os as _os

# import the pure Python version of 'open'

from _pyio import OpenWrapper as open

# for eval/exec/compile

import _ast

# help, exit, quit, credits, copyright and license are all defined in the pure Python _sitebuiltins module
# they will only be defined if Python was not started with the -S flag

def _define_sitebuiltins():
    import _sitebuiltins

    global help, exit, quit, credits, copyright, license

    help = _sitebuiltins._Helper()

    if _os.sep == ":":
        prompt = "Cmd-Q"
    elif _os.sep == "\\":
        prompt = "Ctrl-Z plus Return"
    else:
        prompt = "Ctrl-D (i.e. EOF)"

    exit = _sitebuiltins.Quitter("exit", prompt)
    quit = _sitebuiltins.Quitter("quit", prompt)

    if _sys.platform[:4] == "java":
        credits = _sitebuiltins._Printer("credits",
        "Jython is maintained by the Jython developers (www.jython.org).")
    else:
        credits = _sitebuiltins._Printer("credits",
        "    Thanks to CWI, CNRI, BeOpen.com, Zope Corporation and a cast of thousands\n"
        "    for supporting Python development.  See www.python.org for more information.")

    copyright = _sitebuiltins._Printer("copyright", _sys.copyright)

    try:
        _os.__file__
    except AttributeError:
        files, dirs = [], []
    else:
        files = ["LICENSE.txt", "LICENSE"]
        dirs = [_os.path.join(_os.path.dirname(_os.__file__), _os.pardir), _os.path.dirname(_os.__file__), _os.curdir]

    license = _sitebuiltins._Printer("license", "See http://www.python.org/download/releases/%.5s/license" % _sys.version, files, dirs)

if not _sys.flags.no_site: _define_sitebuiltins()

_builtin_slice = slice # need to keep it around for proper slice checking

# decorator functions

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

    co = func.__code__
    arg_count = co.co_argcount
    func_name = co.co_name
    arg_name = co.co_varnames[arg_count]

    inner.__name__ = func.__name__
    inner.__doc__ = func.__doc__

    if _sys.version_info >= (3, 3):
        inner.__qualname__ = func.__qualname__

    return inner

def _eval_exec_handler(func):
    """Handle eval() and exec() properly."""
    def inner(source, *dicts, **keywords):
        for name in keywords:
            if name not in ("globals", "locals"):
                raise TypeError("%s() got an unexpected keyword argument: %r" % (func_name, name))
        if len(dicts) > 2:
            raise TypeError("%s expected at most 3 arguments, got %i" % (func_name, len(dicts) + 1))
        if "globals" in keywords and dicts:
            raise TypeError("%s() got multiple values for argument 'globals'" % func_name)
        if "locals" in keywords and len(dicts) > 1:
            raise TypeError("%s() got multiple values for argument 'locals'" % func_name)

        globals = keywords.get("globals", dicts[0] if dicts else _sys._getframe(1).f_globals)
        locals = keywords.get("locals", dicts[1] if len(dicts) > 1 else globals)

        return func(source, globals, locals)

    func_name = func.__code__.co_name

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

    co = func.__code__
    arg_count = co.co_argcount
    func_name = co.co_name

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

def _filler(string, fill, filler="0"):
    """Fill the string with 'filler' so that len(string) % fill == 0."""
    if not len(string) % fill:
        return string
    return filler * (fill - len(string) % fill) + string

# Functions in alphabetical order

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
        if 0x7F < ord(char) <= 0xFF:
            string[i] = "\\x" + _filler(hex(ord(char)), 2)
        elif 0xFF < ord(char) <= 0xFFFF:
            string[i] = "\\u" + _filler(hex(ord(char)), 4)
        elif 0xFFFF < ord(char):
            string[i] = "\\U" + _filler(hex(ord(char)), 8)

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

def chr(num): # WRAPPER
    """chr(i) -> Unicode character

    Return a Unicode string of one character with ordinal i; 0 <= i <= 0x10ffff.

    Changes over built-in function:
    None
    """

    if not hasattr(num, "__index__"):
        raise TypeError("an integer is required (got type %s)" % type(num).__name__)
    if num not in range(0x110000):
        raise ValueError("chr() arg not in range(0x110000)")

    import builtins
    return builtins.chr(num)

#def compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1):
#    """compile(source, filename, mode[, flags[, dont_inherit]]) -> code object
#
#    Compile the source (a Python module, statement or expression)
#    into a code object that can be executed by exec() or eval().
#    The filename will be used for run-time error messages.
#    The mode must be 'exec' to compile a module, 'single' to compile a
#    single (interactive) statement, or 'eval' to compile an expression.
#    The flags argument, if present, controls which future statements influence
#    the compilation of the code.
#    The dont_inherit argument, if non-zero, stops the compilation inheriting
#    the effects of any future statements in effect in the code calling
#    compile; if absent or zero these statements do influence the compilation,
#    in addition to any features explicitly specified.
#
#    Changes over built-in function:
#    None
#    """

# Still TODO - or rather, will it ever get done? Maybe it's a tad too hard for the hassle

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

#@_eval_exec_handler
#def eval(source, globals, locals): # WRAPPER
#    """eval(source[, globals[, locals]]) -> value
#
#    Evaluate the source in the context of globals and locals.
#    The source may be a string representing a Python expression
#    or a code object as returned by compile().
#    The globals must be a dictionary and locals can be any mapping,
#    defaulting to the current globals and locals.
#    If only globals is given, locals defaults to it.
#
#    Changes over built-in function:
#    None
#    """
#
#    if isinstance(source, (str, bytes, _ast.AST)):
#        source = compile(source, "<string>", "eval")
#
#    if not code.is_code(source):
#        raise TypeError("eval() arg 1 must be a string, bytes or code object")
#
#    source = code.from_code(source).to_code()
#
#    import builtins
#    return builtins.eval(source, globals, locals)

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

def input(prompt=""):
    """input([prompt]) -> string

    Read a string from standard input.  The trailing newline is stripped.
    If the user hits EOF (Unix: Ctl-D, Windows: Ctl-Z+Return), raise EOFError.
    On Unix, GNU readline is used if enabled.  The prompt string, if given,
    is printed without a trailing newline before reading.

    Changes over built-in function:
    - Readline is not used
    """

    _sys.stdout.write(prompt.rstrip("\r\n"))
    _sys.stdout.flush()

    result = _sys.stdin.readline()

    if _os.sep == "\\":
        if result.rstrip()[-1] == "\x1a":
            raise EOFError

    return result.rstrip("\r\n")
    
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

def repr(object):
    """repr(object) -> string

    Return the canonical string representation of the object.
    For most object types, eval(repr(object)) == object.

    Changes over built-in function:
    None
    """

    return type(object).__repr__(object)








    None
    """


# special decorator classes

class _descriptor:

    def __init__(self, func):
        self.__doc__ = func.__doc__
        if hasattr(func, "tb_frame"):
            func = func.tb_frame
        if hasattr(func, "f_code"):
            func = func.f_code
        if hasattr(func, "gi_code"):
            func = func.gi_code
        if hasattr(func, "__func__"):
            func = func.__func__
        if hasattr(func, "__code__"):
            func = func.__code__
        if hasattr(func, "co_name"):
            self.__name__ = func.co_name
        elif hasattr(func, "__name__"):
            self.__name__ = func.__name__
        else:
            raise TypeError("could not find a name for func")

    def __get__(self, instance, owner):
        self.__objclass__ = owner
        return self

class member_descriptor(_descriptor):

    # A member descriptor is a read-only access to an instance variable
    # They are defined at the class level, and become read-only after one assignment
    # In theory, at least. It does not work

    def __repr__(self):
        return "<member %r of %r objects>" % (self.__name__, self.__objclass__.__name__)

class wrapper_descriptor(_descriptor):

    def __set__(self, instance, value):
        raise AttributeError("cannot override a slot wrapper")

    def __delete__(self, instance):
        raise AttributeError("cannot delete a slot wrapper")

    def __repr__(self):
        return "<slot wrapper %r of %r object>" % (self.__name__, self.__objclass__.__name__)

    def __call__(self, *args, **kwargs):
        return getattr(self.__objclass__, self.__name__)(*args, **kwargs)

class getset_descriptor(_descriptor):

    # A getset descriptor is used for attributes that can be modified after their initial assignment

    def __repr__(self):
        return "<attribute %r of %r objects>" % (self.__name__, self.__objclass__.__name__)

class method_descriptor(_descriptor):

    def __repr__(self):
        return "<method %r of %r objects>" % (self.__name__, self.__objclass__.__name__)

    def __call__(self, *args, **kwargs):
        return getattr(self.__objclass__, self.__name__)(*args, **kwargs)

class method_wrapper(_descriptor):

    def __get__(self, instance, owner):
        self.__objclass__ = owner
        self.__self__ = instance
        return self

    def __repr__(self):
        mem_index = object.__repr__(self)[object.__repr__(self).index("0x"):-1]
        return "<method-wrapper %r of %s object at %s>" % (self.__name__, self.__objclass__.__name__, mem_index)

    def __call__(self, *args, **kwargs):
        if self.__self__ is None:
            return getattr(self.__objclass__, self.__name__)(*args, **kwargs)
        return getattr(self.__objclass__, self.__name__)(self.__self__, *args, **kwargs)

# decorator classes present in the 'builtins' module

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
        self.__isabstractmethod__ = bool(getattr(function, "__isabstractmethod__", False))
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

    @getset_descriptor
    def __isabstractmethd__(self):
        return False

    @member_descriptor
    def __func__(self):
        return self

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

    def __init__(self, func):
        """Initialize self. See help(type(self)) for accurate signature."""
        self.__isabstractmethod__ = bool(getattr(func, "__isabstractmethod__", False))
        self.__func__ = func

    def __get__(self, instance, owner):
        """Return an attribute of instance, which is of type owner."""
        return self.__func__

    @getset_descriptor
    def __isabstractmethod__(self):
        return False

    @member_descriptor
    def __func__(self):
        return self

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
        self.__isabstractmethod__ = bool(getattr(fget, "__isabstractmethod__", False))
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
        return type(self)(fget, self.fset, self.fdel, self.__doc__ or fget.__doc__)

    def setter(self, fset):
        """Descriptor to change the setter on a property."""
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        """Descriptor to change the deleter on a property."""
        return type(self)(self.fget, self.fset, fdel, self.__doc__)

    @member_descriptor
    def fget(self):
        return self

    @member_descriptor
    def fset(self):
        return self

    @member_descriptor
    def fdel(self):
        return self

# special classes

class code:
    """code(argcount, kwonlyargcount, nlocals, stacksize, flags, codestring,
            constants, names, varnames, filename, name, firstlineno,
            lnotab[, freevars[, cellvars]])

    Create a code object.  Not for the faint of heart.

    Changes over built-in type:
    + to_code method, to convert the instance into a built-in code object
    + from_code class method, to create an instance from a built-in code object
    + is_code static method, to detect if an object is a code object
    """

    def __init__(self, argcount, kwonlyargcount, nlocals, stacksize, flags,
                 codestring, constants, names, varnames, filename, name,
                 firstlineno, lnotab, freevars=(), cellvars=()):

        self.co_argcount = argcount
        self.co_kwonlyargcount = kwonlyargcount
        self.co_nlocals = nlocals
        self.co_stacksize = stacksize
        self.co_flags = flags
        self.co_code = codestring
        self.co_consts = constants
        self.co_names = names
        self.co_varnames = varnames
        self.co_filename = filename
        self.co_name = name
        self.co_firstlineno = firstlineno
        self.co_lnotab = lnotab
        self.co_freevars = freevars
        self.co_cellvars = cellvars

    def to_code(co):
        """Convert into a built-in code object for some workings."""
        return _argument.__code__.__class__(co.co_argcount,
                         co.co_kwonlyargcount, co.co_nlocals,
                         co.co_stacksize, co.co_flags, co.co_code,
                         co.co_consts, co.co_names, co.co_varnames,
                         co.co_filename, co.co_name, co.co_firstlineno,
                         co.co_lnotab, co.co_freevars, co.co_cellvars)

    @classmethod
    def from_code(cls, co):
        """Convert a built-in code object into this object."""
        return cls(co.co_argcount, co.co_kwonlyargcount, co.co_nlocals,
                   co.co_stacksize, co.co_flags, co.co_code, co.co_consts,
                   co.co_names, co.co_varnames, co.co_filename, co.co_name,
                   co.co_firstlineno, co.co_lnotab, co.co_freevars, co.co_cellvars)

    @staticmethod
    def is_code(other):
        try:
            other.co_argcount, other.co_kwonlyargcount
            other.co_nlocals, other.co_stacksize
            other.co_flags, other.co_code, other.co_consts
            other.co_names, other.co_varnames
            other.co_filename, other.co_name
            other.co_firstlineno, other.co_lnotab
            other.co_freevars, other.co_cellvars
        except AttributeError:
            return False

        return True

    @member_descriptor
    def co_argcount(self):
        """The number of positional arguments."""

    @member_descriptor
    def co_kwonlyargcount(self):
        """The number of keyword-only arguments."""

    @member_descriptor
    def co_nlocals(self):
        """Equivalent to len(co_varnames)."""

    @member_descriptor
    def co_stacksize(self):
        """How many stacks are needed to execute the bytecode."""

    @member_descriptor
    def co_flags(self):
        """The code flags. As follow:

        1  = CO_OPTIMIZED   - Code is optimized
        2  = CO_NEWLOCALS   - Create a new local scope
        4  = CO_VARARGS     - Use of *args
        8  = CO_VARKEYWORDS - Use of **kwargs
        16 = CO_NESTED      - Function is nested
        32 = CO_GENERATOR   - Function is a generator
        64 = CO_NOFREE      - No space left to modify bytecode (?)
        """

    @member_descriptor
    def co_code(self):
        """Compiled bytecode."""

    @member_descriptor
    def co_consts(self):
        """Constants used in the code."""

    @member_descriptor
    def co_names(self):
        """Functions and other names used in the code."""

    @member_descriptor
    def co_varnames(self):
        """All the variable names used, including the arguments."""

    @member_descriptor
    def co_filename(self):
        """Filename the function was defined in."""

    @member_descriptor
    def co_name(self):
        """Name of the function."""

    @member_descriptor
    def co_firstlineno(self):
        """The line at which the function begins."""

    @member_descriptor
    def co_lnotab(self):
        """Mapping of lines to indents."""

    @member_descriptor
    def co_freevars(self):
        """Variables used in the function but defined outside of it."""

    @member_descriptor
    def co_cellvars(self):
        """Variables used in nested scopes."""

class frame:

    def __init__(self, caller, builtins, code, globals,
                 lasti, lineno, locals, trace=None):

        self.f_back = caller
        self.f_builtins = builtins
        self.f_code = code
        self.f_globals = globals
        self.f_lasti = lasti
        self.f_lineno = lineno
        self.f_locals = locals
        self.f_trace = trace

    def clear(self): # I really don't know what it's meant to do. this is a guess
        self.f_trace = None

    def to_frame(f):
        raise TypeError("cannot create 'frame' instance")

    @classmethod
    def from_frame(cls, f):
        return cls(f.f_back, f.f_builtins, f.f_code, f.f_globals,
                   f.f_lasti, f.f_lineno, f.f_locals, f.f_trace)

    @staticmethod
    def is_frame(f):
        try:
            f.f_back, f.f_builtins, f.f_code, f.f_globals
            f.f_lasti, f.f_lineno, f.f_locals, f.f_trace
        except AttributeError:
            return False

        return True

    @member_descriptor
    def f_back(self):
        """This frame's caller."""

    @member_descriptor
    def f_builtins(self):
        """Built-in scope seen by this frame."""

    @member_descriptor
    def f_code(self):
        """Code object ran by this frame."""

    @member_descriptor
    def f_globals(self):
        """Global scope seen by this frame."""

    @member_descriptor
    def f_lasti(self):
        """Last index attempted in bytecode."""

    @member_descriptor
    def f_lineno(self):
        """Line number where frame begins (?)."""

    @member_descriptor
    def f_locals(self):
        """Local scope seen by this frame."""

    @member_descriptor
    def f_trace(self):
        """Tracing function for this frame, or None."""

class traceback:

    def __init__(self, frame, lasti, lineno, next=None):
        self.tb_frame = frame
        self.tb_lasti = lasti
        self.tb_lineno = lineno
        self.tb_next = next

    def to_traceback(tb):
        raise TypeError("cannot create 'traceback' instance")

    @classmethod
    def from_traceback(cls, tb):
        return cls(tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)

    @staticmethod
    def is_traceback(tb):
        try:
            tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next
        except AttributeError:
            return False

        return True

    @member_descriptor
    def tb_frame(self):
        """Frame object associated with this traceback."""

    @member_descriptor
    def tb_lasti(self):
        """Last index attempted in bytecode."""

    @member_descriptor
    def tb_lineno(self):
        """Line number where error occurred."""

    @member_descriptor
    def tb_next(self):
        """Inner traceback level (called by this level)."""

class cell:

    def __init__(self, contents):
        self.cell_contents = contents

    def __repr__(self):
        mem_index = object.__repr__(self)[object.__repr__(self).index("0x"):-1]
        mem_cell = object.__repr__(self.cell_contents)[object.__repr__(self.cell_contents).index("0x"):-1]
        return "<cell at %s: %s object at %s>" % (mem_index, self.cell_contents.__class__.__name__, mem_cell)

    def to_cell(cell):
        raise TypeError("cannot create 'cell' instance")

    @classmethod
    def from_cell(cls, cell):
        return cls(cell.cell_contents)

    @staticmethod
    def is_cell(cell):
        return hasattr(cell, "cell_contents")

    @getset_descriptor
    def cell_contents(self):
        """Contents of the cell."""

class function:
    """function(code, globals[, name[, argdefs[, closure]]])

    Create a function object from a code object and a dictionary.
    The optional name string overrides the name from the code object.
    The optional argdefs tuple specifies the default argument values.
    The optional closure tuple supplies the bindings for free variables.
    """

    def __init__(self, code, globals, name=None, argdefs=None, closure=None):
        if name is None:
            name = code.co_name
        self.__name__ = name
        self.__code__ = code
        self.__annotations__ = {}
        self.__closure__ = closure
        self.__defaults__ = argdefs
        self.__kwdefaults__ = None
        self.__globals__ = globals
        self.__doc__ = code.co_consts[0] if isinstance(code.co_consts[0], str) else None

    def __get__(self, instance, owner):
        if instance is not None:
            return method(self, instance)
        return self

    def __call__(self, *args, **kwargs):
        locals = dict(_sys._getframe(1).f_locals)
        globals = _sys._getframe(1).f_globals
        defargs = self.__defaults__ or ()
        kwdefargs = self.__kwdefaults__ or {}
        _args = {}
        user_args = {}
        co = self.__code__
        CO_VARARGS = 4
        CO_VARKEYWORDS = 8

        num = total = co.co_argcount + co.co_kwonlyargcount

        if co.co_flags & CO_VARARGS:
            total += 1
        if co.co_flags & CO_VARKEYWORDS:
            total += 1

        args_all = kwargs_all = None

        if co.co_flags & CO_VARKEYWORDS:
            kwargs_all = co.co_varnames[num+bool(co.co_flags & CO_VARARGS)]

        if co.co_flags & CO_VARARGS:
            args_all = co.co_varnames[num]

        elif co.co_kwonlyargcount:
            args_all = ""

        arguments = co.co_varnames[:total]
        index = co.co_argcount - len(defargs) - len(args)

        if co.co_argcount < len(args):
            raise TypeError("%s() takes %i positional arguments but %i were given" % (co.co_name, co.co_argcount, len(args)))

        if co.co_argcount - len(defargs) > len(args):
            raise TypeError("%s() missing %i required positional argument%s: %s" % (co.co_name, index, "s" if index > 1 else "", repr(arguments[index-1]) if
                                                                                    index == 1 else ", ".join(repr(x) for x in arguments[index-1:co.co_argcount-1]) +
                                                                                    (" and %r" % arguments[co.co_argcount-1])))

        for arg in kwargs:
            if arg not in arguments:
                raise TypeError("%s() got an unexpected keyword argument: %r" % (co.co_name, arg))

        if len(defargs) >= co.co_argcount:
            for i, arg in enumerate(arguments):
                if i >= co.co_argcount:
                    break
                _args[arg] = defargs[i]

        elif defargs:
            defargs_index = co.co_argcount - len(defargs)
            for arg in defargs:
                _args[arguments[defargs_index]] = arg

        _args.update(kwdefargs)

        for i, arg in enumerate(args):
            user_args[arguments[i]] = arg

        for arg, value in kwargs.items():
            if arg in args:
                raise TypeError("%s() got multiple values for argument %r" % arg)
            user_args[arg] = value

        _args.update(user_args)

        locals.update(_args)

        try:
            return eval(co, globals, locals)
        except TypeError: # not a code object or something
            return eval(co.to_code(), globals, locals)

    def to_function(func):
        fn = _argument.__class__(func.__code__, func.__globals__,
                                 func.__name__, func.__defaults__,
                                 func.__closure__)

        fn.__kwdefaults__ = func.__kwdefaults__
        fn.__annotations__ = func.__annotations__

        return fn

    @classmethod
    def from_function(cls, func):
        fn = cls(func.__code__, func.__globals__, func.__name__,
                 func.__defaults__, func.__closure__)

        fn.__kwdefaults__ = func.__kwdefaults__
        fn.__annotations__ = func.__annotations__

        return fn

    @staticmethod
    def is_function(func):
        try:
            func.__code__, func.__name__, func.__closure__
            func.__annotations__, func.__globals__
            func.__defaults__, func.__kwdefaults__
        except AttributeError:
            return False

        return True

    @getset_descriptor
    def __code__(self):
        """Code object for this function."""

    @getset_descriptor
    def __annotations__(self):
        """Annotations for the parameters."""

    @member_descriptor
    def __closure__(self):
        """Names accessed in this scope defined in the outer scope."""

    @getset_descriptor
    def __defaults__(self):
        """Default values for the positional arguments."""

    @getset_descriptor
    def __kwdefaults__(self):
        """Default values for the keyword arguments."""

    @member_descriptor
    def __globals__(self):
        """Global scope seen by this function."""

class method:
    """method(function, instance)

    Create a bound instance method object.
    """

    def __init__(self, function, instance):
        self.__func__ = function
        self.__self__ = instance

    def __call__(self, *args, **kwargs):
        return self.__func__(self.__self__, *args, **kwargs)

    def to_method(met):
        return met.to_method.__class__(met.__func__, met.__self__)

    @classmethod
    def from_method(cls, met):
        return cls(met.__func__, met.__self__)

    @staticmethod
    def is_method(met):
        try:
            met.__func__, met.__self__
        except AttributeError:
            return False

        return True

    @member_descriptor
    def __func__(self):
        """The function associated with the method."""

    @member_descriptor
    def __self__(self):
        """The instance associated with the method."""

class generator:
    """generator(code)

    Create a generator object.

    Changes over built-in class:
    + Support for the context manager
    """

    def __init__(self, code):
        self.gi_code = code
        self.gi_running = 0
        self.gi_frame = frame(
            _sys._getframe(1), globals(), code,
            _sys._getframe(1).f_globals, 1,
            code.co_firstlineno,
            _sys._getframe(1).f_locals)

    def to_generator(gi):
        raise TypeError("cannot create 'generator' instance")

    @classmethod
    def from_generator(cls, gi):
        return cls(gi.gi_code)

    @staticmethod
    def is_generator(gi):
        try:
            gi.gi_code, gi.gi_running, gi.gi_frame
        except AttributeError:
            return False

        return True

    def __del__(self):
        self.close()

    def __enter__(self):
        self.send(None)
        return self

    def __exit__(self, exc, value, tb):
        try:
            self.close()
        except Exception:
            pass

    def __iter__(self):
        return self

    def __next__(self):
        pass # TODO: continue execution, and yield value

    def close(self):
        """close() -> raise GeneratorExit inside generator."""

    def throw(self, exc, value=None, tb=None):
        """throw(exc [, value [, tb]]) -> raise exception in generator,
        return next yielded value or raise StopIteration."""
        # still TODO

    def send(self, value):
        """send(value) -> send 'value' into generator,
        return next yielded value or raise StopIteration."""

    @member_descriptor
    def gi_code(self):
        """Code object for this generator."""

    @member_descriptor
    def gi_running(self):
        """Set to 1 if generator is running, 0 otherwise."""

    @member_descriptor
    def gi_frame(self):
        """Frame object or possibly None once the generator has been exhausted."""

class module:
    """module(name [,doc])

    Create a module object.
    The name must be a string; the optional doc argument can have any type.
    """

    def __init__(self, name, doc=None):
        if not isinstance(name, str):
            raise TypeError("module.__init__() argument 1 must be str, not %s" % name.__class__.__name__)

        self.__name__ = name
        self.__doc__ = doc
        self.__loader__ = None
        self.__package__ = None
        self.__spec__ = None

    def to_module(mod):
        m = _sys.__class__(mod.__name__, mod.__doc__)

        m.__loader__ = mod.__loader
        m.__package__ = mod.__package__
        m.__spec__ = mod.__spec__

        return m

    @classmethod
    def from_module(cls, mod):
        m = cls(mod.__name__, mod.__doc__)

        m.__loader__ = mod.__loader
        m.__package__ = mod.__package__
        m.__spec__ = mod.__spec__

        return m

    @staticmethod
    def is_module(mod):
        try:
            mod.__name__, mod.__loader__
            mod.__package__, mod.__spec__
        except AttributeError:
            return False

        return True

    def __dir__(self):
        return self.__dict__

    def __repr__(self):
        return "<module %r>" % (self.__name__,)

class namespace:
    """A simple attribute-based namespace.

    namespace(**kwargs)

    Changes over built-in class:
    + Support for subscription
    """

    def __init__(self, **kwargs):
        for arg in kwargs.items():
            setattr(self, *arg)

    def __iter__(self):
        yield from self.__dict__

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, ", ".join("=".join((x, repr(self[x]))) for x in self))

    def __getitem__(self, item):
        if item in self:
            return getattr(self, item)
        raise KeyError(item)

    __setitem__ = setattr
    __delitem__ = delattr

class mappingproxy:

    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, key):
        return self.mapping[key]

    def __iter__(self):
        yield from self.mapping

    def copy(self):
        return self.__class__(self.mapping.copy())

    def get(self, key, default=None):
        return self.mapping.get(key, default)

    def keys(self):
        return self.mapping.keys()

    def values(self):
        return self.mapping.values()

    def items(self):
        return self.mapping.items()

    @member_descriptor
    def mapping(self):
        return {}

# non-decorator classes found in the 'builtins' module

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
        if self.index >= self.length:
            raise StopIteration
        self.index += 1
        return self.index - 1, next(self.iterator)

    def __reduce__(self):
        """Return state information for pickling."""
        return type(self), (self.iterator, self.index)

    @getset_descriptor
    def iterator(self):
        return iter([])

    @getset_descriptor
    def index(self):
        return 0

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

    @getset_descriptor
    def callable(self):
        return bool

    @getset_descriptor
    def iterator(self):
        return iter([])

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

    @getset_descriptor
    def function(self):
        return self

    @getset_descriptor
    def iterators(self):
        return []

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
