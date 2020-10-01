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

import uuid

from oauthlib import oauth1
import six
from testtools import matchers

from keystoneauth1.extras import oauth1 as ksa_oauth1
from keystoneauth1 import fixture
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils as test_utils


class OAuth1AuthTests(test_utils.TestCase):

    TEST_ROOT_URL = 'http://127.0.0.1:5000/'
    TEST_URL = '%s%s' % (TEST_ROOT_URL, 'v3')
    TEST_TOKEN = uuid.uuid4().hex

    def stub_auth(self, subject_token=None, **kwargs):
        if not subject_token:
            subject_token = self.TEST_TOKEN

        self.stub_url('POST', ['auth', 'tokens'],
                      headers={'X-Subject-Token': subject_token}, **kwargs)

    def _validate_oauth_headers(self, auth_header, oauth_client):
        """Validate data in the headers.

        Assert that the data in the headers matches the data
        that is produced from oauthlib.
        """
        self.assertThat(auth_header, matchers.StartsWith('OAuth '))
        parameters = dict(
            oauth1.rfc5849.utils.parse_authorization_header(auth_header))

        self.assertEqual('HMAC-SHA1', parameters['oauth_signature_method'])
        self.assertEqual('1.0', parameters['oauth_version'])
        self.assertIsInstance(parameters['oauth_nonce'], six.string_types)
        self.assertEqual(oauth_client.client_key,
                         parameters['oauth_consumer_key'])
        if oauth_client.resource_owner_key:
            self.assertEqual(oauth_client.resource_owner_key,
                             parameters['oauth_token'],)
        if oauth_client.verifier:
            self.assertEqual(oauth_client.verifier,
                             parameters['oauth_verifier'])
        if oauth_client.callback_uri:
            self.assertEqual(oauth_client.callback_uri,
                             parameters['oauth_callback'])
        return parameters

    def test_oauth_authenticate_success(self):
        consumer_key = uuid.uuid4().hex
        consumer_secret = uuid.uuid4().hex
        access_key = uuid.uuid4().hex
        access_secret = uuid.uuid4().hex

        oauth_token = fixture.V3Token(methods=['oauth1'],
                                      oauth_consumer_id=consumer_key,
                                      oauth_access_token_id=access_key)
        oauth_token.set_project_scope()

        self.stub_auth(json=oauth_token)

        a = ksa_oauth1.V3OAuth1(self.TEST_URL,
                                consumer_key=consumer_key,
                                consumer_secret=consumer_secret,
                                access_key=access_key,
                                access_secret=access_secret)

        s = session.Session(auth=a)
        t = s.get_token()

        self.assertEqual(self.TEST_TOKEN, t)

        OAUTH_REQUEST_BODY = {
            "auth": {
                "identity": {
                    "methods": ["oauth1"],
                    "oauth1": {}
                }
            }
        }

        self.assertRequestBodyIs(json=OAUTH_REQUEST_BODY)

        # Assert that the headers have the same oauthlib data
        req_headers = self.requests_mock.last_request.headers
        oauth_client = oauth1.Client(consumer_key,
                                     client_secret=consumer_secret,
                                     resource_owner_key=access_key,
                                     resource_owner_secret=access_secret,
                                     signature_method=oauth1.SIGNATURE_HMAC)
        self._validate_oauth_headers(req_headers['Authorization'],
                                     oauth_client)

    def test_warning_dual_scope(self):
        ksa_oauth1.V3OAuth1(self.TEST_URL,
                            consumer_key=uuid.uuid4().hex,
                            consumer_secret=uuid.uuid4().hex,
                            access_key=uuid.uuid4().hex,
                            access_secret=uuid.uuid4().hex,
                            project_id=uuid.uuid4().hex)

        self.assertIn('ignored by the identity server', self.logger.output)
