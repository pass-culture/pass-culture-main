
# Copyright 2015 OpenStack Foundation
# All Rights Reserved.
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
Test fixtures.

.. versionadded:: 1.3
"""

import threading

import fixtures

from oslo_utils import timeutils
from oslo_utils import uuidutils


class TimeFixture(fixtures.Fixture):
    """A fixture for overriding the time returned by timeutils.utcnow().

    :param override_time: datetime instance or list thereof. If not given,
                          defaults to the current UTC time.

    """

    def __init__(self, override_time=None):
        super(TimeFixture, self).__init__()
        self._override_time = override_time

    def setUp(self):
        super(TimeFixture, self).setUp()
        timeutils.set_time_override(self._override_time)
        self.addCleanup(timeutils.clear_time_override)

    def advance_time_delta(self, timedelta):
        """Advance overridden time using a datetime.timedelta."""
        timeutils.advance_time_delta(timedelta)

    def advance_time_seconds(self, seconds):
        """Advance overridden time by seconds."""
        timeutils.advance_time_seconds(seconds)


class _UUIDSentinels(object):
    """Registry of dynamically created, named, random UUID strings.

    An instance of this class will dynamically generate attributes as they are
    referenced, associating a random UUID string with each. Thereafter,
    referring to the same attribute will give the same UUID for the life of the
    instance. Plan accordingly.

    Usage::

        from oslo_utils.fixture import uuidsentinel as uuids
        ...
        foo = uuids.foo
        do_a_thing(foo)
        # Referencing the same sentinel again gives the same value
        assert foo == uuids.foo
        # But a different one will be different
        assert foo != uuids.bar
    """
    def __init__(self):
        self._sentinels = {}
        self._lock = threading.Lock()

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError('Sentinels must not start with _')
        with self._lock:
            if name not in self._sentinels:
                self._sentinels[name] = uuidutils.generate_uuid()
        return self._sentinels[name]


# Singleton sentinel instance. Caveat emptor: using this multiple times in the
# same process (including across multiple modules) will result in the same
# values
uuidsentinel = _UUIDSentinels()
