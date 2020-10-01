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

"""A fixture to wrap the session constructor for use with Betamax."""

from functools import partial
from unittest import mock

import betamax
import fixtures
import requests

from keystoneauth1.fixture import hooks
from keystoneauth1.fixture import serializer as yaml_serializer
from keystoneauth1 import session


class BetamaxFixture(fixtures.Fixture):

    def __init__(self, cassette_name, cassette_library_dir=None,
                 serializer=None, record=False,
                 pre_record_hook=hooks.pre_record_hook,
                 serializer_name=None, request_matchers=None):
        """Configure Betamax for the test suite.

        :param str cassette_name:
            This is simply the name of the cassette without any file extension
            or containing directory. For example, to generate
            ``keystoneauth1/tests/unit/data/example.yaml``, one would pass
            only ``example``.
        :param str cassette_library_dir:
            This is the directory that will contain all cassette files. In
            ``keystoneauth1/tests/unit/data/example.yaml`` you would pass
            ``keystoneauth1/tests/unit/data/``.
        :param serializer:
            A class that implements the Serializer API in Betamax. See also:
            https://betamax.readthedocs.io/en/latest/serializers.html
        :param record:
            The Betamax record mode to use. If ``False`` (the default), then
            Betamax will not record anything. For more information about
            record modes, see:
            https://betamax.readthedocs.io/en/latest/record_modes.html
        :param callable pre_record_hook:
            Function or callable to use to perform some handling of the
            request or response data prior to saving it to disk.
        :param str serializer_name:
            The name of a serializer already registered with Betamax to use
            to handle cassettes. For example, if you want to use the default
            Betamax serializer, you would pass ``'json'`` to this parameter.
        :param list request_matchers:
            The list of request matcher names to use with Betamax. Betamax's
            default list is used if none are specified. See also:
            https://betamax.readthedocs.io/en/latest/matchers.html
        """
        self.cassette_library_dir = cassette_library_dir
        self.record = record
        self.cassette_name = cassette_name
        if not (serializer or serializer_name):
            serializer = yaml_serializer.YamlJsonSerializer
            serializer_name = serializer.name
        if serializer:
            betamax.Betamax.register_serializer(serializer)
        self.serializer = serializer
        self._serializer_name = serializer_name
        self.pre_record_hook = pre_record_hook
        self.use_cassette_kwargs = {}
        if request_matchers is not None:
            self.use_cassette_kwargs['match_requests_on'] = request_matchers

    @property
    def serializer_name(self):
        """Determine the name of the selected serializer.

        If a class was specified, use the name attribute to generate this,
        otherwise, use the serializer_name parameter from ``__init__``.

        :returns:
            Name of the serializer
        :rtype:
            str
        """
        if self.serializer:
            return self.serializer.name
        return self._serializer_name

    def setUp(self):
        super(BetamaxFixture, self).setUp()
        self.mockpatch = mock.patch.object(
            session, '_construct_session',
            partial(_construct_session_with_betamax, self))
        self.mockpatch.start()
        # Unpatch during cleanup
        self.addCleanup(self.mockpatch.stop)


def _construct_session_with_betamax(fixture, session_obj=None):
    # NOTE(morganfainberg): This function should contain the logic of
    # keystoneauth1.session._construct_session as it replaces the
    # _construct_session function to apply betamax magic to the requests
    # session object.
    if not session_obj:
        session_obj = requests.Session()
        # Use TCPKeepAliveAdapter to fix bug 1323862
        for scheme in list(session_obj.adapters.keys()):
            session_obj.mount(scheme, session.TCPKeepAliveAdapter())

    with betamax.Betamax.configure() as config:
        config.before_record(callback=fixture.pre_record_hook)
    fixture.recorder = betamax.Betamax(
        session_obj, cassette_library_dir=fixture.cassette_library_dir)

    record = 'none'
    serializer = None

    if fixture.record in ['once', 'all', 'new_episodes']:
        record = fixture.record

    serializer = fixture.serializer_name

    fixture.recorder.use_cassette(fixture.cassette_name,
                                  serialize_with=serializer,
                                  record=record,
                                  **fixture.use_cassette_kwargs)

    fixture.recorder.start()
    fixture.addCleanup(fixture.recorder.stop)
    return session_obj
