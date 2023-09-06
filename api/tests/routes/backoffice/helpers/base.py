import abc

from flask import url_for


class BaseHelper(abc.ABC):
    @property
    @abc.abstractmethod
    def endpoint(self):
        raise NotImplementedError()

    @property
    def endpoint_kwargs(self):
        return {}

    @property
    def path(self):
        return url_for(self.endpoint, **self.endpoint_kwargs)

    @property
    def http_method(self):
        return getattr(self, "method", "get")
