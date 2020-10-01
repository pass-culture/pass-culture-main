# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from keystoneauth1.exceptions import base


__all__ = ('ConnectionError',
           'ConnectTimeout',
           'ConnectFailure',
           'SSLError',
           'RetriableConnectionFailure',
           'UnknownConnectionError')


class RetriableConnectionFailure(Exception):
    """A mixin class that implies you can retry the most recent request."""

    pass


class ConnectionError(base.ClientException):
    message = "Cannot connect to API service."


class ConnectTimeout(ConnectionError, RetriableConnectionFailure):
    message = "Timed out connecting to service."


class ConnectFailure(ConnectionError, RetriableConnectionFailure):
    message = "Connection failure that may be retried."


class SSLError(ConnectionError):
    message = "An SSL error occurred."


class UnknownConnectionError(ConnectionError):
    """An error was encountered but we don't know what it is."""

    def __init__(self, msg, original):
        super(UnknownConnectionError, self).__init__(msg)
        self.original = original
