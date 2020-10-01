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

from unittest import mock

import betamax
from betamax import exceptions
import testtools

from keystoneauth1.fixture import keystoneauth_betamax
from keystoneauth1.fixture import serializer
from keystoneauth1.fixture import v2 as v2Fixtures
from keystoneauth1.identity import v2
from keystoneauth1 import session


class TestBetamaxFixture(testtools.TestCase):

    TEST_USERNAME = 'test_user_name'
    TEST_PASSWORD = 'test_password'
    TEST_TENANT_NAME = 'test_tenant_name'
    TEST_AUTH_URL = 'http://keystoneauth-betamax.test/v2.0/'

    V2_TOKEN = v2Fixtures.Token(tenant_name=TEST_TENANT_NAME,
                                user_name=TEST_USERNAME)

    def setUp(self):
        super(TestBetamaxFixture, self).setUp()
        self.ksa_betamax_fixture = self.useFixture(
            keystoneauth_betamax.BetamaxFixture(
                cassette_name='ksa_betamax_test_cassette',
                cassette_library_dir='keystoneauth1/tests/unit/data/',
                record=False))

    def _replay_cassette(self):
        plugin = v2.Password(
            auth_url=self.TEST_AUTH_URL,
            password=self.TEST_PASSWORD,
            username=self.TEST_USERNAME,
            tenant_name=self.TEST_TENANT_NAME)
        s = session.Session()
        s.get_token(auth=plugin)

    def test_keystoneauth_betamax_fixture(self):
        self._replay_cassette()

    def test_replay_of_bad_url_fails(self):
        plugin = v2.Password(
            auth_url='http://invalid-auth-url/v2.0/',
            password=self.TEST_PASSWORD,
            username=self.TEST_USERNAME,
            tenant_name=self.TEST_TENANT_NAME)
        s = session.Session()
        self.assertRaises(exceptions.BetamaxError, s.get_token, auth=plugin)


class TestBetamaxFixtureSerializerBehaviour(testtools.TestCase):
    """Test the fixture's logic, not its monkey-patching.

    The setUp method of our BetamaxFixture monkey-patches the function to
    construct a session. We don't need to test that particular bit of logic
    here so we do not need to call useFixture in our setUp method.
    """

    @mock.patch.object(betamax.Betamax, 'register_serializer')
    def test_can_pass_custom_serializer(self, register_serializer):
        serializer = mock.Mock()
        serializer.name = 'mocked-serializer'
        fixture = keystoneauth_betamax.BetamaxFixture(
            cassette_name='fake',
            cassette_library_dir='keystoneauth1/tests/unit/data',
            serializer=serializer,
        )

        register_serializer.assert_called_once_with(serializer)
        self.assertIs(serializer, fixture.serializer)
        self.assertEqual('mocked-serializer', fixture.serializer_name)

    def test_can_pass_serializer_name(self):
        fixture = keystoneauth_betamax.BetamaxFixture(
            cassette_name='fake',
            cassette_library_dir='keystoneauth1/tests/unit/data',
            serializer_name='json',
        )

        self.assertIsNone(fixture.serializer)
        self.assertEqual('json', fixture.serializer_name)

    def test_no_serializer_options_provided(self):
        fixture = keystoneauth_betamax.BetamaxFixture(
            cassette_name='fake',
            cassette_library_dir='keystoneauth1/tests/unit/data',
        )

        self.assertIs(serializer.YamlJsonSerializer, fixture.serializer)
        self.assertEqual('yamljson', fixture.serializer_name)

    def test_no_request_matchers_provided(self):
        fixture = keystoneauth_betamax.BetamaxFixture(
            cassette_name='fake',
            cassette_library_dir='keystoneauth1/tests/unit/data',
        )

        self.assertDictEqual({}, fixture.use_cassette_kwargs)

    def test_request_matchers(self):
        fixture = keystoneauth_betamax.BetamaxFixture(
            cassette_name='fake',
            cassette_library_dir='keystoneauth1/tests/unit/data',
            request_matchers=['method', 'uri', 'json-body'],
        )

        self.assertDictEqual(
            {'match_requests_on': ['method', 'uri', 'json-body']},
            fixture.use_cassette_kwargs,
        )
