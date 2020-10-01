from __future__ import absolute_import

from contextlib import contextmanager
from copy import copy

from flask import g, request
from flask.globals import _app_ctx_stack, _request_ctx_stack

from .base import VersioningManager as BaseVersioningManager


class VersioningManager(BaseVersioningManager):
    _actor_cls = 'User'

    def get_transaction_values(self):
        values = copy(self.values)
        if context_available() and hasattr(g, 'activity_values'):
            values.update(g.activity_values)
        if (
            'client_addr' not in values and
            self.default_client_addr is not None
        ):
            values['client_addr'] = self.default_client_addr
        if (
            'actor_id' not in values and
            self.default_actor_id is not None
        ):
            values['actor_id'] = self.default_actor_id
        return values

    @property
    def default_actor_id(self):
        from flask_login import current_user

        # Return None if we are outside of request context.
        if not context_available():
            return

        try:
            return current_user.id
        except AttributeError:
            return

    @property
    def default_client_addr(self):
        # Return None if we are outside of request context.
        if not context_available():
            return
        return request.remote_addr or None


def context_available():
    return (
        _app_ctx_stack.top is not None and
        _request_ctx_stack.top is not None
    )


@contextmanager
def activity_values(**values):
    if not context_available():
        return
    g.activity_values = values
    yield
    del g.activity_values


versioning_manager = VersioningManager()
