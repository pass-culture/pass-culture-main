# -*- coding: utf-8 -*-

#    Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
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
Eventlet utils helper module.

.. versionadded:: 1.3
"""

import threading
import warnings

from oslo_utils import importutils
from oslo_utils import timeutils


# These may or may not exist; so carefully import them if we can...
_eventlet = importutils.try_import('eventlet')
_patcher = importutils.try_import('eventlet.patcher')

# Attribute that can be used by others to see if eventlet is even currently
# useable (can be used in unittests to skip test cases or test classes that
# require eventlet to work).
EVENTLET_AVAILABLE = all((_eventlet, _patcher))

# Taken from eventlet.py (v0.16.1) patcher code (it's not a accessible set
# for some reason...)
_ALL_PATCH = frozenset(['__builtin__', 'MySQLdb', 'os',
                        'psycopg', 'select', 'socket', 'thread', 'time'])


def fetch_current_thread_functor():
    """Get the current thread.

    If eventlet is used to monkey-patch the threading module, return the
    current eventlet greenthread. Otherwise, return the current Python thread.

    .. versionadded:: 1.5
    """
    # Until https://github.com/eventlet/eventlet/issues/172 is resolved
    # or addressed we have to use complicated workaround to get a object
    # that will not be recycled; the usage of threading.current_thread()
    # doesn't appear to currently be monkey patched and therefore isn't
    # reliable to use (and breaks badly when used as all threads share
    # the same current_thread() object)...
    if not EVENTLET_AVAILABLE:
        return threading.current_thread
    else:
        green_threaded = _patcher.is_monkey_patched('thread')
        if green_threaded:
            return _eventlet.getcurrent
        else:
            return threading.current_thread


def warn_eventlet_not_patched(expected_patched_modules=None,
                              what='this library'):
    """Warns if eventlet is being used without patching provided modules.

    :param expected_patched_modules: list of modules to check to ensure that
                                     they are patched (and to warn if they
                                     are not); these names should correspond
                                     to the names passed into the eventlet
                                     monkey_patch() routine. If not provided
                                     then *all* the modules that could be
                                     patched are checked. The currently valid
                                     selection is one or multiple of
                                     ['MySQLdb', '__builtin__', 'all', 'os',
                                     'psycopg', 'select', 'socket', 'thread',
                                     'time'] (where 'all' has an inherent
                                     special meaning).
    :type expected_patched_modules: list/tuple/iterable
    :param what: string to merge into the warnings message to identify
                 what is being checked (used in forming the emitted warnings
                 message).
    :type what: string
    """
    if not expected_patched_modules:
        expanded_patched_modules = _ALL_PATCH.copy()
    else:
        expanded_patched_modules = set()
        for m in expected_patched_modules:
            if m == 'all':
                expanded_patched_modules.update(_ALL_PATCH)
            else:
                if m not in _ALL_PATCH:
                    raise ValueError("Unknown module '%s' requested to check"
                                     " if patched" % m)
                else:
                    expanded_patched_modules.add(m)
    if EVENTLET_AVAILABLE:
        try:
            # The patcher code stores a dictionary here of all modules
            # names -> whether it was patched...
            #
            # Example:
            #
            # >>> _patcher.monkey_patch(os=True)
            # >>> print(_patcher.already_patched)
            # {'os': True}
            maybe_patched = bool(_patcher.already_patched)
        except AttributeError:
            # Assume it is patched (the attribute used here doesn't appear
            # to be a public documented API so we will assume that everything
            # is patched when that attribute isn't there to be safe...)
            maybe_patched = True
        if maybe_patched:
            not_patched = []
            for m in sorted(expanded_patched_modules):
                if not _patcher.is_monkey_patched(m):
                    not_patched.append(m)
            if not_patched:
                warnings.warn("It is highly recommended that when eventlet"
                              " is used that the %s modules are monkey"
                              " patched when using %s (to avoid"
                              " spurious or unexpected lock-ups"
                              " and/or hangs)" % (not_patched, what),
                              RuntimeWarning, stacklevel=3)


def is_monkey_patched(module):
    """Determines safely is eventlet patching for module enabled or not
    :param module: String, module name
    :return Bool: True if module is patched, False otherwise
    """

    if _patcher is None:
        return False
    return _patcher.is_monkey_patched(module)


class EventletEvent(object):
    """A class that provides consistent eventlet/threading Event API.

    This wraps the eventlet.event.Event class to have the same API as
    the standard threading.Event object.
    """
    def __init__(self, *args, **kwargs):
        super(EventletEvent, self).__init__()
        self.clear()

    def clear(self):
        if getattr(self, '_set', True):
            self._set = False
            self._event = _eventlet.event.Event()

    def is_set(self):
        return self._set

    isSet = is_set

    def set(self):
        if not self._set:
            self._set = True
            self._event.send(True)

    def wait(self, timeout=None):
        with timeutils.StopWatch(timeout) as sw:
            while True:
                event = self._event
                with _eventlet.timeout.Timeout(sw.leftover(return_none=True),
                                               False):
                    event.wait()
                    if event is not self._event:
                        continue
                return self.is_set()


def Event():
    if is_monkey_patched("thread"):
        return EventletEvent()
    else:
        return threading.Event()
