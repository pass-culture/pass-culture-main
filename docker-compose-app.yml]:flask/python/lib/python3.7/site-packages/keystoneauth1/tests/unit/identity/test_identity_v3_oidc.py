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

import uuid
import warnings

from six.moves import urllib

from keystoneauth1 import exceptions
from keystoneauth1.identity.v3 import oidc
from keystoneauth1 import session
from keystoneauth1.tests.unit import oidc_fixtures
from keystoneauth1.tests.unit import utils


KEYSTONE_TOKEN_VALUE = uuid.uuid4().hex


class BaseOIDCTests(object):

    def setUp(self):
        super(BaseOIDCTests, self).setUp()
        self.session = session.Session()

        self.AUTH_URL = 'http://keystone:5000/v3'
        self.IDENTITY_PROVIDER = 'bluepages'
        self.PROTOCOL = 'oidc'
        self.USER_NAME = 'oidc_user@example.com'
        self.PROJECT_NAME = 'foo project'
        self.PASSWORD = uuid.uuid4().hex
        self.CLIENT_ID = uuid.uuid4().hex
        self.CLIENT_SECRET = uuid.uuid4().hex
        self.ACCESS_TOKEN = uuid.uuid4().hex
        self.ACCESS_TOKEN_ENDPOINT = 'https://localhost:8020/oidc/token'
        self.FEDERATION_AUTH_URL = '%s/%s' % (
            self.AUTH_URL,
            'OS-FEDERATION/identity_providers/bluepages/protocols/oidc/auth')
        self.REDIRECT_URL = 'urn:ietf:wg:oauth:2.0:oob'
        self.CODE = '4/M9TNz2G9WVwYxSjx0w9AgA1bOmryJltQvOhQMq0czJs.cnLNVAfqwG'

        self.DISCOVERY_URL = ('https://localhost:8020/oidc/.well-known/'
                              'openid-configuration')
        self.GRANT_TYPE = None

    def test_grant_type_and_plugin_missmatch(self):
        self.assertRaises(
            exceptions.OidcGrantTypeMissmatch,
            self.plugin.__class__,
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            grant_type=uuid.uuid4().hex
        )

    def test_can_pass_grant_type_but_warning_is_issued(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.plugin.__class__(
                self.AUTH_URL,
                self.IDENTITY_PROVIDER,
                self.PROTOCOL,
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
                grant_type=self.GRANT_TYPE)
            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "grant_type" in str(w[-1].message)

    def test_discovery_not_found(self):
        self.requests_mock.get("http://not.found",
                               status_code=404)

        plugin = self.plugin.__class__(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            discovery_endpoint="http://not.found")

        self.assertRaises(exceptions.http.NotFound,
                          plugin._get_discovery_document,
                          self.session)

    def test_no_discovery(self):

        plugin = self.plugin.__class__(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            access_token_endpoint=self.ACCESS_TOKEN_ENDPOINT,
        )
        self.assertEqual(self.ACCESS_TOKEN_ENDPOINT,
                         plugin.access_token_endpoint)

    def test_load_discovery(self):
        self.requests_mock.get(self.DISCOVERY_URL,
                               json=oidc_fixtures.DISCOVERY_DOCUMENT)

        plugin = self.plugin.__class__(self.AUTH_URL,
                                       self.IDENTITY_PROVIDER,
                                       self.PROTOCOL,
                                       client_id=self.CLIENT_ID,
                                       client_secret=self.CLIENT_SECRET,
                                       discovery_endpoint=self.DISCOVERY_URL)
        self.assertEqual(
            oidc_fixtures.DISCOVERY_DOCUMENT["token_endpoint"],
            plugin._get_access_token_endpoint(self.session)
        )

    def test_no_access_token_endpoint(self):
        plugin = self.plugin.__class__(self.AUTH_URL,
                                       self.IDENTITY_PROVIDER,
                                       self.PROTOCOL,
                                       client_id=self.CLIENT_ID,
                                       client_secret=self.CLIENT_SECRET)

        self.assertRaises(exceptions.OidcAccessTokenEndpointNotFound,
                          plugin._get_access_token_endpoint,
                          self.session)

    def test_invalid_discovery_document(self):
        self.requests_mock.get(self.DISCOVERY_URL,
                               json={})

        plugin = self.plugin.__class__(self.AUTH_URL,
                                       self.IDENTITY_PROVIDER,
                                       self.PROTOCOL,
                                       client_id=self.CLIENT_ID,
                                       client_secret=self.CLIENT_SECRET,
                                       discovery_endpoint=self.DISCOVERY_URL)

        self.assertRaises(exceptions.InvalidOidcDiscoveryDocument,
                          plugin._get_discovery_document,
                          self.session)

    def test_load_discovery_override_by_endpoints(self):
        self.requests_mock.get(self.DISCOVERY_URL,
                               json=oidc_fixtures.DISCOVERY_DOCUMENT)

        access_token_endpoint = uuid.uuid4().hex
        plugin = self.plugin.__class__(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            discovery_endpoint=self.DISCOVERY_URL,
            access_token_endpoint=access_token_endpoint
        )
        self.assertEqual(access_token_endpoint,
                         plugin._get_access_token_endpoint(self.session))

    def test_wrong_grant_type(self):
        self.requests_mock.get(self.DISCOVERY_URL,
                               json={"grant_types_supported": ["foo", "bar"]})

        plugin = self.plugin.__class__(self.AUTH_URL,
                                       self.IDENTITY_PROVIDER,
                                       self.PROTOCOL,
                                       client_id=self.CLIENT_ID,
                                       client_secret=self.CLIENT_SECRET,
                                       discovery_endpoint=self.DISCOVERY_URL)

        self.assertRaises(exceptions.OidcPluginNotSupported,
                          plugin.get_unscoped_auth_ref,
                          self.session)


class OIDCClientCredentialsTests(BaseOIDCTests, utils.TestCase):
    def setUp(self):
        super(OIDCClientCredentialsTests, self).setUp()

        self.GRANT_TYPE = 'client_credentials'

        self.plugin = oidc.OidcClientCredentials(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            access_token_endpoint=self.ACCESS_TOKEN_ENDPOINT,
            project_name=self.PROJECT_NAME)

    def test_initial_call_to_get_access_token(self):
        """Test initial call, expect JSON access token."""
        # Mock the output that creates the access token
        self.requests_mock.post(
            self.ACCESS_TOKEN_ENDPOINT,
            json=oidc_fixtures.ACCESS_TOKEN_VIA_PASSWORD_RESP)

        # Prep all the values and send the request
        scope = 'profile email'
        payload = {'grant_type': self.GRANT_TYPE, 'scope': scope}
        self.plugin._get_access_token(self.session, payload)

        # Verify the request matches the expected structure
        last_req = self.requests_mock.last_request
        self.assertEqual(self.ACCESS_TOKEN_ENDPOINT, last_req.url)
        self.assertEqual('POST', last_req.method)
        encoded_payload = urllib.parse.urlencode(payload)
        self.assertEqual(encoded_payload, last_req.body)

    def test_second_call_to_protected_url(self):
        """Test subsequent call, expect Keystone token."""
        # Mock the output that creates the keystone token
        self.requests_mock.post(
            self.FEDERATION_AUTH_URL,
            json=oidc_fixtures.UNSCOPED_TOKEN,
            headers={'X-Subject-Token': KEYSTONE_TOKEN_VALUE})

        res = self.plugin._get_keystone_token(self.session,
                                              self.ACCESS_TOKEN)

        # Verify the request matches the expected structure
        self.assertEqual(self.FEDERATION_AUTH_URL, res.request.url)
        self.assertEqual('POST', res.request.method)

        headers = {'Authorization': 'Bearer ' + self.ACCESS_TOKEN}
        self.assertEqual(headers['Authorization'],
                         res.request.headers['Authorization'])

    def test_end_to_end_workflow(self):
        """Test full OpenID Connect workflow."""
        # Mock the output that creates the access token
        self.requests_mock.post(
            self.ACCESS_TOKEN_ENDPOINT,
            json=oidc_fixtures.ACCESS_TOKEN_VIA_PASSWORD_RESP)

        # Mock the output that creates the keystone token
        self.requests_mock.post(
            self.FEDERATION_AUTH_URL,
            json=oidc_fixtures.UNSCOPED_TOKEN,
            headers={'X-Subject-Token': KEYSTONE_TOKEN_VALUE})

        response = self.plugin.get_unscoped_auth_ref(self.session)
        self.assertEqual(KEYSTONE_TOKEN_VALUE, response.auth_token)


class OIDCPasswordTests(BaseOIDCTests, utils.TestCase):
    def setUp(self):
        super(OIDCPasswordTests, self).setUp()

        self.GRANT_TYPE = 'password'

        self.plugin = oidc.OidcPassword(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            access_token_endpoint=self.ACCESS_TOKEN_ENDPOINT,
            project_name=self.PROJECT_NAME,
            username=self.USER_NAME,
            password=self.PASSWORD)

    def test_initial_call_to_get_access_token(self):
        """Test initial call, expect JSON access token."""
        # Mock the output that creates the access token
        self.requests_mock.post(
            self.ACCESS_TOKEN_ENDPOINT,
            json=oidc_fixtures.ACCESS_TOKEN_VIA_PASSWORD_RESP)

        # Prep all the values and send the request
        grant_type = 'password'
        scope = 'profile email'
        payload = {'grant_type': grant_type, 'username': self.USER_NAME,
                   'password': self.PASSWORD, 'scope': scope}
        self.plugin._get_access_token(self.session, payload)

        # Verify the request matches the expected structure
        last_req = self.requests_mock.last_request
        self.assertEqual(self.ACCESS_TOKEN_ENDPOINT, last_req.url)
        self.assertEqual('POST', last_req.method)
        encoded_payload = urllib.parse.urlencode(payload)
        self.assertEqual(encoded_payload, last_req.body)

    def test_second_call_to_protected_url(self):
        """Test subsequent call, expect Keystone token."""
        # Mock the output that creates the keystone token
        self.requests_mock.post(
            self.FEDERATION_AUTH_URL,
            json=oidc_fixtures.UNSCOPED_TOKEN,
            headers={'X-Subject-Token': KEYSTONE_TOKEN_VALUE})

        res = self.plugin._get_keystone_token(self.session,
                                              self.ACCESS_TOKEN)

        # Verify the request matches the expected structure
        self.assertEqual(self.FEDERATION_AUTH_URL, res.request.url)
        self.assertEqual('POST', res.request.method)

        headers = {'Authorization': 'Bearer ' + self.ACCESS_TOKEN}
        self.assertEqual(headers['Authorization'],
                         res.request.headers['Authorization'])

    def test_end_to_end_workflow(self):
        """Test full OpenID Connect workflow."""
        # Mock the output that creates the access token
        self.requests_mock.post(
            self.ACCESS_TOKEN_ENDPOINT,
            json=oidc_fixtures.ACCESS_TOKEN_VIA_PASSWORD_RESP)

        # Mock the output that creates the keystone token
        self.requests_mock.post(
            self.FEDERATION_AUTH_URL,
            json=oidc_fixtures.UNSCOPED_TOKEN,
            headers={'X-Subject-Token': KEYSTONE_TOKEN_VALUE})

        response = self.plugin.get_unscoped_auth_ref(self.session)
        self.assertEqual(KEYSTONE_TOKEN_VALUE, response.auth_token)


class OIDCAuthorizationGrantTests(BaseOIDCTests, utils.TestCase):
    def setUp(self):
        super(OIDCAuthorizationGrantTests, self).setUp()

        self.GRANT_TYPE = 'authorization_code'

        self.plugin = oidc.OidcAuthorizationCode(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            access_token_endpoint=self.ACCESS_TOKEN_ENDPOINT,
            redirect_uri=self.REDIRECT_URL,
            project_name=self.PROJECT_NAME,
            code=self.CODE)

    def test_initial_call_to_get_access_token(self):
        """Test initial call, expect JSON access token."""
        # Mock the output that creates the access token
        self.requests_mock.post(
            self.ACCESS_TOKEN_ENDPOINT,
            json=oidc_fixtures.ACCESS_TOKEN_VIA_AUTH_GRANT_RESP)

        # Prep all the values and send the request
        grant_type = 'authorization_code'
        payload = {'grant_type': grant_type,
                   'redirect_uri': self.REDIRECT_URL,
                   'code': self.CODE}
        self.plugin._get_access_token(self.session, payload)

        # Verify the request matches the expected structure
        last_req = self.requests_mock.last_request
        self.assertEqual(self.ACCESS_TOKEN_ENDPOINT, last_req.url)
        self.assertEqual('POST', last_req.method)
        encoded_payload = urllib.parse.urlencode(payload)
        self.assertEqual(encoded_payload, last_req.body)


# NOTE(aloga): This is a special case, as we do not need all the other openid
# parameters, like client_id, client_secret, access_token_endpoint and so on,
# therefore we do not inherit from the base oidc test class, but from the base
# TestCase
class OIDCTokenTests(utils.TestCase):
    def setUp(self):
        super(OIDCTokenTests, self).setUp()

        self.session = session.Session()

        self.AUTH_URL = 'http://keystone:5000/v3'
        self.IDENTITY_PROVIDER = 'bluepages'
        self.PROTOCOL = 'oidc'
        self.PROJECT_NAME = 'foo project'
        self.ACCESS_TOKEN = uuid.uuid4().hex

        self.FEDERATION_AUTH_URL = '%s/%s' % (
            self.AUTH_URL,
            'OS-FEDERATION/identity_providers/bluepages/protocols/oidc/auth')

        self.plugin = oidc.OidcAccessToken(
            self.AUTH_URL,
            self.IDENTITY_PROVIDER,
            self.PROTOCOL,
            access_token=self.ACCESS_TOKEN,
            project_name=self.PROJECT_NAME)

    def test_end_to_end_workflow(self):
        """Test full OpenID Connect workflow."""
        # Mock the output that creates the keystone token
        self.requests_mock.post(
            self.FEDERATION_AUTH_URL,
            json=oidc_fixtures.UNSCOPED_TOKEN,
            headers={'X-Subject-Token': KEYSTONE_TOKEN_VALUE})

        response = self.plugin.get_unscoped_auth_ref(self.session)
        self.assertEqual(KEYSTONE_TOKEN_VALUE, response.auth_token)
