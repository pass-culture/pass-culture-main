import inspect
import sys

if sys.version_info[0] >= 3:
    getargspec = lambda func: inspect.getfullargspec(func)[:4]
else:
    getargspec = inspect.getargspec

from .options import OptionProperty


class MemoizedFunction(object):

    etag = OptionProperty('etag')
    max_age = OptionProperty('max_age')
    expiry = OptionProperty('expiry')

    def __init__(self, cache, func, master_key, opts, args=None, kwargs=None):
        self.cache = cache
        self.func = func
        self.master_key = master_key
        self.opts = opts
        self.args = args or ()
        self.kwargs = kwargs or {}

    def __get__(self, obj, owner=None):
        if obj is not None:
            return self.bind(obj)
        else:
            return self

    def __repr__(self):
        return '<%s of %s via %s>' % (self.__class__.__name__, self.func, self.cache)

    def bind(self, *args, **kwargs):
        args, kwargs = self._expand_args(args, kwargs)
        return self.__class__(
            self.cache,
            self.func,
            self.master_key,
            self.opts,
            args,
            kwargs,
        )

    def _expand_args(self, args, new_kwargs):
        args = self.args + args
        kwargs = self.kwargs.copy()
        kwargs.update(new_kwargs or {})
        return args, kwargs

    def _expand_opts(self, opts):
        for k, v in self.opts.items():
            opts.setdefault(k, v)

    def key(self, args=(), kwargs=None):

        # We need to normalize the signature of the function. This is only
        # really possible if we wrap the "real" function.
        kwargs = kwargs or {}
        spec_args, _, _, spec_defaults = getargspec(self.func)

        # Insert kwargs into the args list by name.
        orig_args = list(args)
        args = []
        for i, name in enumerate(spec_args):
            if name in kwargs:
                args.append(kwargs.pop(name))
            elif orig_args:
                args.append(orig_args.pop(0))
            else:
                break

        args.extend(orig_args)

        # Add on as many defaults as we need to.
        if spec_defaults:
            offset = len(spec_args) - len(spec_defaults)
            args.extend(spec_defaults[len(args) - offset:])

        arg_str_chunks = list(map(repr, args))
        for pair in kwargs.items():
            arg_str_chunks.append('%s=%r' % pair)
        arg_str = ', '.join(arg_str_chunks)

        key = '%s.%s(%s)' % (self.func.__module__, self.func.__name__, arg_str)
        return self.master_key + ':' + key if self.master_key else key

    def __call__(self, *args, **kwargs):
        args, copy_kwargs = self._expand_args(args, kwargs)
        return self.cache.get(self.key(args, copy_kwargs), self.func, args, kwargs, **self.opts)

    def get(self, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        return self.cache.get(self.key(args, kwargs), self.func, args, kwargs, **opts)

    def delete(self, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        self.cache.delete(self.key(args, kwargs))

    def expire(self, max_age, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        self.cache.expire(self.key(args, kwargs), max_age)

    def expire_at(self, max_age, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        self.cache.expire_at(self.key(args, kwargs), max_age)

    def ttl(self, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        return self.cache.ttl(self.key(args, kwargs))

    def exists(self, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        return self.cache.exists(self.key(args, kwargs))

    def last_etag(self, args=(), kwargs=None, **opts):
        args, kwargs = self._expand_args(args, kwargs)
        self._expand_opts(opts)
        return self.cache.etag(self.key(args, kwargs))
    