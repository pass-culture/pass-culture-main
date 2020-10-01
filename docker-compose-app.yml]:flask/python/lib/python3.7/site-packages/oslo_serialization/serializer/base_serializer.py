#    Copyright 2016 Mirantis, Inc.
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
Unified and simplified API for oslo.serialization's serializers.
"""


import abc


class BaseSerializer(object, metaclass=abc.ABCMeta):
    """Generic (de-)serialization definition abstract base class."""

    @abc.abstractmethod
    def dump(self, obj, fp):
        """Serialize ``obj`` as a stream to ``fp``.

        :param obj: python object to be serialized
        :param fp: ``.write()``-supporting file-like object
        """

    @abc.abstractmethod
    def dump_as_bytes(self, obj):
        """Serialize ``obj`` to a byte string.

        :param obj: python object to be serialized
        :returns: byte string
        """

    @abc.abstractmethod
    def load(self, fp):
        """Deserialize ``fp`` to a python object.

        :param fp: ``.read()``-supporting file-like object
        :returns: python object
        """

    @abc.abstractmethod
    def load_from_bytes(self, s):
        """Deserialize ``s`` to a python object.

        :param s: byte string to be deserialized
        :returns: python object
        """
