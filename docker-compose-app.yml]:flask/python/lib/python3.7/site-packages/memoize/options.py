from functools import partial
from collections import Callable


def call_or_pass(value, args, kwargs):
    if isinstance(value, Callable):
        return value(*args, **kwargs)
    return value


class OptionProperty(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    def __get__(self, obj, cls):
        return partial(self, obj)

    def __set__(self, obj, value):
        obj.opts[self.name] = value

    def __call__(self, obj, *args, **kwargs):

        # As a decorator.
        if len(args) == 1 and not kwargs and isinstance(args[0], Callable):
            obj.opts[self.name] = args[0]
            return args[0]

        else:
            value = obj.opts.get(self.name)
            return call_or_pass(value, args, kwargs)
