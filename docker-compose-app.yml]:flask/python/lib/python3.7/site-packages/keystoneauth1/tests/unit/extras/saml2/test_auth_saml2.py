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

import base64
import uuid

import requests

from keystoneauth1 import exceptions
from keystoneauth1.extras import _saml2 as saml2
from keystoneauth1 import fixture as ksa_fixtures
from keystoneauth1 import session
from keystoneauth1.tests.unit.extras.saml2 import fixtures as saml2_fixtures
from keystoneauth1.tests.unit.extras.saml2 import utils
from keystoneauth1.tests.unit import matchers

PAOS_HEADER = 'application/vnd.paos+xml'
CONTENT_TYPE_PAOS_HEADER = {'Content-Type': PAOS_HEADER}
InvalidResponse = saml2.v3.saml2.InvalidResponse


class SamlAuth2PluginTests(utils.TestCase):
    """These test ONLY the standalone requests auth plugin.

    Tests for the auth plugin are later so that hopefully these can be
    extracted into it's own module.
    """

    HEADER_MEDIA_TYPE_SEPARATOR = ','

    TEST_USER = 'user'
    TEST_PASS = 'pass'
    TEST_SP_URL = 'http://sp.test'
    TEST_IDP_URL = 'http://idp.test'
    TEST_CONSUMER_URL = "https://openstack4.local/Shibboleth.sso/SAML2/ECP"

    def get_plugin(self, **kwargs):
        kwargs.setdefault('identity_provider_url', self.TEST_IDP_URL)
        kwargs.setdefault('requests_auth', (self.TEST_USER, self.TEST_PASS))
        return saml2.v3.saml2._SamlAuth(**kwargs)

    @property
    def calls(self):
        return [r.url.strip('/') for r in self.requests_mock.request_history]

    def basic_header(self, username=TEST_USER, password=TEST_PASS):
        user_pass = ('%s:%s' % (username, password)).encode('utf-8')
        return 'Basic %s' % base64.b64encode(user_pass).decode('utf-8')

    def test_request_accept_headers(self):
        # Include some random Accept header
        random_header = uuid.uuid4().hex
        headers = {'Accept': random_header}
        req = requests.Request('GET', 'http://another.test', headers=headers)

        plugin = self.get_plugin()
        plugin_headers = plugin(req).headers
        self.assertIn('Accept', plugin_headers)

        # Since we have included a random Accept header, the plugin should have
        # added the PAOS_HEADER to it using the correct media type separator
        accept_header = plugin_headers['Accept']
        self.assertIn(self.HEADER_MEDIA_TYPE_SEPARATOR, accept_header)
        self.assertIn(random_header,
                      accept_header.split(self.HEADER_MEDIA_TYPE_SEPARATOR))
        self.assertIn(PAOS_HEADER,
                      accept_header.split(self.HEADER_MEDIA_TYPE_SEPARATOR))

    def test_passed_when_not_200(self):
        text = uuid.uuid4().hex
        test_url = 'http://another.test'
        self.requests_mock.get(test_url,
                               status_code=201,
                               headers=CONTENT_TYPE_PAOS_HEADER,
                               text=text)

        resp = requests.get(test_url, auth=self.get_plugin())
        self.assertEqual(201, resp.status_code)
        self.assertEqual(text, resp.text)

    def test_200_without_paos_header(self):
        text = uuid.uuid4().hex
        test_url = 'http://another.test'
        self.requests_mock.get(test_url, status_code=200, text=text)

        resp = requests.get(test_url, auth=self.get_plugin())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(text, resp.text)

    def test_standard_workflow_302_redirect(self):
        text = uuid.uuid4().hex

        self.requests_mock.get(self.TEST_SP_URL, response_list=[
            dict(headers=CONTENT_TYPE_PAOS_HEADER,
                 content=utils.make_oneline(saml2_fixtures.SP_SOAP_RESPONSE)),
            dict(text=text)
        ])

        authm = self.requests_mock.post(self.TEST_IDP_URL,
                                        content=saml2_fixtures.SAML2_ASSERTION)

        self.requests_mock.post(
            self.TEST_CONSUMER_URL,
            status_code=302,
            headers={'Location': self.TEST_SP_URL})

        resp = requests.get(self.TEST_SP_URL, auth=self.get_plugin())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(text, resp.text)

        self.assertEqual(self.calls, [self.TEST_SP_URL,
                                      self.TEST_IDP_URL,
                                      self.TEST_CONSUMER_URL,
                                      self.TEST_SP_URL])

        self.assertEqual(self.basic_header(),
                         authm.last_request.headers['Authorization'])

        authn_request = self.requests_mock.request_history[1].text
        self.assertThat(saml2_fixtures.AUTHN_REQUEST,
                        matchers.XMLEquals(authn_request))

    def test_standard_workflow_303_redirect(self):
        text = uuid.uuid4().hex

        self.requests_mock.get(self.TEST_SP_URL, response_list=[
            dict(headers=CONTENT_TYPE_PAOS_HEADER,
                 content=utils.make_oneline(saml2_fixtures.SP_SOAP_RESPONSE)),
            dict(text=text)
        ])

        authm = self.requests_mock.post(self.TEST_IDP_URL,
                                        content=saml2_fixtures.SAML2_ASSERTION)

        self.requests_mock.post(
            self.TEST_CONSUMER_URL,
            status_code=303,
            headers={'Location': self.TEST_SP_URL})

        resp = requests.get(self.TEST_SP_URL, auth=self.get_plugin())
        self.assertEqual(200, resp.status_code)
        self.assertEqual(text, resp.text)

        url_flow = [self.TEST_SP_URL,
                    self.TEST_IDP_URL,
                    self.TEST_CONSUMER_URL,
                    self.TEST_SP_URL]

        self.assertEqual(url_flow, [r.url.rstrip('/') for r in resp.history])
        self.assertEqual(url_flow, self.calls)

        self.assertEqual(self.basic_header(),
                         authm.last_request.headers['Authorization'])

        authn_request = self.requests_mock.request_history[1].text
        self.assertThat(saml2_fixtures.AUTHN_REQUEST,
                        matchers.XMLEquals(authn_request))

    def test_initial_sp_call_invalid_response(self):
        """Send initial SP HTTP request and receive wrong server response."""
        self.requests_mock.get(self.TEST_SP_URL,
                               headers=CONTENT_TYPE_PAOS_HEADER,
                               text='NON XML RESPONSE')

        self.assertRaises(InvalidResponse,
                          requests.get,
                          self.TEST_SP_URL,
                          auth=self.get_plugin())

        self.assertEqual(self.calls, [self.TEST_SP_URL])

    def test_consumer_mismatch_error_workflow(self):
        consumer1 = 'http://consumer1/Shibboleth.sso/SAML2/ECP'
        consumer2 = 'http://consumer2/Shibboleth.sso/SAML2/ECP'
        soap_response = saml2_fixtures.soap_response(consumer=consumer1)
        saml_assertion = saml2_fixtures.saml_assertion(destination=consumer2)

        self.requests_mock.get(self.TEST_SP_URL,
                               headers=CONTENT_TYPE_PAOS_HEADER,
                               content=soap_response)

        self.requests_mock.post(self.TEST_IDP_URL, content=saml_assertion)

        # receive the SAML error, body unchecked
        saml_error = self.requests_mock.post(consumer1)

        self.assertRaises(saml2.v3.saml2.ConsumerMismatch,
                          requests.get,
                          self.TEST_SP_URL,
                          auth=self.get_plugin())

        self.assertTrue(saml_error.called)


class AuthenticateviaSAML2Tests(utils.TestCase):

    TEST_USER = 'user'
    TEST_PASS = 'pass'
    TEST_IDP = 'tester'
    TEST_PROTOCOL = 'saml2'
    TEST_AUTH_URL = 'http://keystone.test:5000/v3/'

    TEST_IDP_URL = 'https://idp.test'
    TEST_CONSUMER_URL = "https://openstack4.local/Shibboleth.sso/SAML2/ECP"

    def get_plugin(self, **kwargs):
        kwargs.setdefault('auth_url', self.TEST_AUTH_URL)
        kwargs.setdefault('username', self.TEST_USER)
        kwargs.setdefault('password', self.TEST_PASS)
        kwargs.setdefault('identity_provider', self.TEST_IDP)
        kwargs.setdefault('identity_provider_url', self.TEST_IDP_URL)
        kwargs.setdefault('protocol', self.TEST_PROTOCOL)
        return saml2.V3Saml2Password(**kwargs)

    def sp_url(self, **kwargs):
        kwargs.setdefault('base', self.TEST_AUTH_URL.rstrip('/'))
        kwargs.setdefault('identity_provider', self.TEST_IDP)
        kwargs.setdefault('protocol', self.TEST_PROTOCOL)

        templ = ('%(base)s/OS-FEDERATION/identity_providers/'
                 '%(identity_provider)s/protocols/%(protocol)s/auth')
        return templ % kwargs

    @property
    def calls(self):
        return [r.url.strip('/') for r in self.requests_mock.request_history]

    def basic_header(self, username=TEST_USER, password=TEST_PASS):
        user_pass = ('%s:%s' % (username, password)).encode('utf-8')
        return 'Basic %s' % base64.b64encode(user_pass).decode('utf-8')

    def setUp(self):
        super(AuthenticateviaSAML2Tests, self).setUp()
        self.session = session.Session()
        self.default_sp_url = self.sp_url()

    def test_workflow(self):
        token_id = uuid.uuid4().hex
        token = ksa_fixtures.V3Token()

        self.requests_mock.get(self.default_sp_url, response_list=[
            dict(headers=CONTENT_TYPE_PAOS_HEADER,
                 content=utils.make_oneline(saml2_fixtures.SP_SOAP_RESPONSE)),
            dict(headers={'X-Subject-Token': token_id}, json=token)
        ])

        authm = self.requests_mock.post(self.TEST_IDP_URL,
                                        content=saml2_fixtures.SAML2_ASSERTION)

        self.requests_mock.post(
            self.TEST_CONSUMER_URL,
            status_code=302,
            headers={'Location': self.sp_url()})

        auth_ref = self.get_plugin().get_auth_ref(self.session)

        self.assertEqual(token_id, auth_ref.auth_token)

        self.assertEqual(self.calls, [self.default_sp_url,
                                      self.TEST_IDP_URL,
                                      self.TEST_CONSUMER_URL,
                                      self.default_sp_url])

        self.assertEqual(self.basic_header(),
                         authm.last_request.headers['Authorization'])

        authn_request = self.requests_mock.request_history[1].text
        self.assertThat(saml2_fixtures.AUTHN_REQUEST,
                        matchers.XMLEquals(authn_request))

    def test_consumer_mismatch_error_workflow(self):
        consumer1 = 'http://keystone.test/Shibboleth.sso/SAML2/ECP'
        consumer2 = 'http://consumer2/Shibboleth.sso/SAML2/ECP'

        soap_response = saml2_fixtures.soap_response(consumer=consumer1)
        saml_assertion = saml2_fixtures.saml_assertion(destination=consumer2)

        self.requests_mock.get(self.default_sp_url,
                               headers=CONTENT_TYPE_PAOS_HEADER,
                               content=soap_response)

        self.requests_mock.post(self.TEST_IDP_URL, content=saml_assertion)

        # receive the SAML error, body unchecked
        saml_error = self.requests_mock.post(consumer1)

        self.assertRaises(exceptions.AuthorizationFailure,
                          self.get_plugin().get_auth_ref,
                          self.session)

        self.assertTrue(saml_error.called)

    def test_initial_sp_call_invalid_response(self):
        """Send initial SP HTTP request and receive wrong server response."""
        self.requests_mock.get(self.default_sp_url,
                               headers=CONTENT_TYPE_PAOS_HEADER,
                               text='NON XML RESPONSE')

        self.assertRaises(exceptions.AuthorizationFailure,
                          self.get_plugin().get_auth_ref,
                          self.session)

        self.assertEqual(self.calls, [self.default_sp_url])
