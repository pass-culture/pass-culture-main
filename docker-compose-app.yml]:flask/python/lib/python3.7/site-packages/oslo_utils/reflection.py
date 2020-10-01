# -*- coding: utf-8 -*-

#    Copyright (C) 2012-2013 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Reflection module.

.. versionadded:: 1.1
"""

import inspect
import types

import six

try:
    _TYPE_TYPE = types.TypeType
except AttributeError:
    _TYPE_TYPE = type

# See: https://docs.python.org/2/library/__builtin__.html#module-__builtin__
# and see https://docs.python.org/2/reference/executionmodel.html (and likely
# others)...
_BUILTIN_MODULES = ('builtins', '__builtin__', '__builtins__', 'exceptions')

if six.PY3:
    Parameter = inspect.Parameter
    Signature = inspect.Signature
    get_signature = inspect.signature
else:
    # Provide an equivalent but use funcsigs instead...
    import funcsigs
    Parameter = funcsigs.Parameter
    Signature = funcsigs.Signature
    get_signature = funcsigs.signature


def get_members(obj, exclude_hidden=True):
    """Yields the members of an object, filtering by hidden/not hidden.

    .. versionadded:: 2.3
    """
    for (name, value) in inspect.getmembers(obj):
        if name.startswith("_") and exclude_hidden:
            continue
        yield (name, value)


def get_member_names(obj, exclude_hidden=True):
    """Get all the member names for a object."""
    return [name for (name, _obj) in
            get_members(obj, exclude_hidden=exclude_hidden)]


def get_class_name(obj, fully_qualified=True, truncate_builtins=True):
    """Get class name for object.

    If object is a type, returns name of the type. If object is a bound
    method or a class method, returns its ``self`` object's class name.
    If object is an instance of class, returns instance's class name.
    Else, name of the type of the object is returned. If fully_qualified
    is True, returns fully qualified name of the type. For builtin types,
    just name is returned. TypeError is raised if can't get class name from
    object.
    """
    if inspect.isfunction(obj):
        raise TypeError("Can't get class name.")

    if inspect.ismethod(obj):
        obj = get_method_self(obj)
    if not isinstance(obj, six.class_types):
        obj = type(obj)
    if truncate_builtins:
        try:
            built_in = obj.__module__ in _BUILTIN_MODULES
        except AttributeError:  # nosec
            pass
        else:
            if built_in:
                return obj.__name__
    if fully_qualified and hasattr(obj, '__module__'):
        return '%s.%s' % (obj.__module__, obj.__name__)
    else:
        return obj.__name__


def get_all_class_names(obj, up_to=object,
                        fully_qualified=True, truncate_builtins=True):
    """Get class names of object parent classes.

    Iterate over all class names object is instance or subclass of,
    in order of method resolution (mro). If up_to parameter is provided,
    only name of classes that are sublcasses to that class are returned.
    """
    if not isinstance(obj, six.class_types):
        obj = type(obj)
    for cls in obj.mro():
        if issubclass(cls, up_to):
            yield get_class_name(cls,
                                 fully_qualified=fully_qualified,
                                 truncate_builtins=truncate_builtins)


def get_callable_name(function):
    """Generate a name from callable.

    Tries to do the best to guess fully qualified callable name.
    """
    method_self = get_method_self(function)
    if method_self is not None:
        # This is a bound method.
        if isinstance(method_self, six.class_types):
            # This is a bound class method.
            im_class = method_self
        else:
            im_class = type(method_self)
        try:
            parts = (im_class.__module__, function.__qualname__)
        except AttributeError:
            parts = (im_class.__module__, im_class.__name__, function.__name__)
    elif inspect.ismethod(function) or inspect.isfunction(function):
        # This could be a function, a static method, a unbound method...
        try:
            parts = (function.__module__, function.__qualname__)
        except AttributeError:
            if hasattr(function, 'im_class'):
                # This is a unbound method, which exists only in python 2.x
                im_class = function.im_class
                parts = (im_class.__module__,
                         im_class.__name__, function.__name__)
            else:
                parts = (function.__module__, function.__name__)
    else:
        im_class = type(function)
        if im_class is _TYPE_TYPE:
            im_class = function
        try:
            parts = (im_class.__module__, im_class.__qualname__)
        except AttributeError:
            parts = (im_class.__module__, im_class.__name__)
    return '.'.join(parts)


def get_method_self(method):
    """Gets the ``self`` object attached to this method (or none)."""
    if not inspect.ismethod(method):
        return None
    try:
        return six.get_method_self(method)
    except AttributeError:
        return None


def is_same_callback(callback1, callback2, strict=True):
    """Returns if the two callbacks are the same."""
    if callback1 is callback2:
        # This happens when plain methods are given (or static/non-bound
        # methods).
        return True
    if callback1 == callback2:
        if not strict:
            return True
        # Two bound methods are equal if functions themselves are equal and
        # objects they are applied to are equal. This means that a bound
        # method could be the same bound method on another object if the
        # objects have __eq__ methods that return true (when in fact it is a
        # different bound method). Python u so crazy!
        try:
            self1 = six.get_method_self(callback1)
            self2 = six.get_method_self(callback2)
            return self1 is self2
        except AttributeError:  # nosec
            pass
    return False


def is_bound_method(method):
    """Returns if the given method is bound to an object."""
    return get_method_self(method) is not None


def is_subclass(obj, cls):
    """Returns if the object is class and it is subclass of a given class."""
    return inspect.isclass(obj) and issubclass(obj, cls)


def get_callable_args(function, required_only=False):
    """Get names of callable arguments.

    Special arguments (like ``*args`` and ``**kwargs``) are not included into
    output.

    If required_only is True, optional arguments (with default values)
    are not included into output.
    """
    sig = get_signature(function)
    function_args = list(six.iterkeys(sig.parameters))
    for param_name, p in six.iteritems(sig.parameters):
        if (p.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD) or
                (required_only and p.default is not Parameter.empty)):
            function_args.remove(param_name)
    return function_args


def accepts_kwargs(function):
    """Returns ``True`` if function accepts kwargs otherwise ``False``."""
    sig = get_signature(function)
    return any(p.kind == Parameter.VAR_KEYWORD
               for p in six.itervalues(sig.parameters))
