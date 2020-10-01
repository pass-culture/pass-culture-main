import time

from django.conf import settings
from django.core.cache import caches


class Cache(object):
    """
    Will simply proxy cache calls to django's internal
    cache framework
    """
    def __init__(self, name='default'):
        self._cache = caches[name]

    def get(self, key):
        return self._cache.get(key)

    def delete(self, key):
        return self._cache.delete(key)

    def expire_at(self, key, max_age):
        raise NotImplementedError('Unsupported by django cache backend')

    def exists(self, key):
        return self.get(key) is not None

    def __getitem__(self):
        return self.get(key)

    def __setitem__(self, key, value):
        expiry = value[2]
        seconds = None
        if expiry:
            # this is a bit ugly, but django's cache framework
            # requires an expiry in seconds
            # to we reverse-compute that value from the expiry given in the
            # data tuple
            now = time.time()
            seconds = int(expiry - now)
        return self._cache.set(key, value, seconds)

    def __delitem__(key):
        return self.delete(key)
