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

from lxml import etree
from six.moves import urllib

from keystoneauth1 import exceptions
from keystoneauth1.extras import _saml2 as saml2
from keystoneauth1.tests.unit import client_fixtures
from keystoneauth1.tests.unit.extras.saml2 import fixtures as saml2_fixtures
from keystoneauth1.tests.unit.extras.saml2 import utils
from keystoneauth1.tests.unit import matchers


class AuthenticateviaADFSTests(utils.TestCase):

    GROUP = 'auth'

    NAMESPACES = {
        's': 'http://www.w3.org/2003/05/soap-envelope',
        'trust': 'http://docs.oasis-open.org/ws-sx/ws-trust/200512',
        'wsa': 'http://www.w3.org/2005/08/addressing',
        'wsp': 'http://schemas.xmlsoap.org/ws/2004/09/policy',
        'a': 'http://www.w3.org/2005/08/addressing',
        'o': ('http://docs.oasis-open.org/wss/2004/01/oasis'
              '-200401-wss-wssecurity-secext-1.0.xsd')
    }

    USER_XPATH = ('/s:Envelope/s:Header'
                  '/o:Security'
                  '/o:UsernameToken'
                  '/o:Username')
    PASSWORD_XPATH = ('/s:Envelope/s:Header'
                      '/o:Security'
                      '/o:UsernameToken'
                      '/o:Password')
    ADDRESS_XPATH = ('/s:Envelope/s:Body'
                     '/trust:RequestSecurityToken'
                     '/wsp:AppliesTo/wsa:EndpointReference'
                     '/wsa:Address')
    TO_XPATH = ('/s:Envelope/s:Header'
                '/a:To')

    TEST_TOKEN = uuid.uuid4().hex

    PROTOCOL = 'saml2'

    @property
    def _uuid4(self):
        return '4b911420-4982-4009-8afc-5c596cd487f5'

    def setUp(self):
        super(AuthenticateviaADFSTests, self).setUp()

        self.IDENTITY_PROVIDER = 'adfs'
        self.IDENTITY_PROVIDER_URL = ('http://adfs.local/adfs/service/trust/13'
                                      '/usernamemixed')
        self.FEDERATION_AUTH_URL = '%s/%s' % (
            self.TEST_URL,
            'OS-FEDERATION/identity_providers/adfs/protocols/saml2/auth')
        self.SP_ENDPOINT = 'https://openstack4.local/Shibboleth.sso/ADFS'
        self.SP_ENTITYID = 'https://openstack4.local'

        self.adfsplugin = saml2.V3ADFSPassword(
            self.TEST_URL, self.IDENTITY_PROVIDER,
            self.IDENTITY_PROVIDER_URL, self.SP_ENDPOINT,
            self.TEST_USER, self.TEST_TOKEN, self.PROTOCOL)

        self.ADFS_SECURITY_TOKEN_RESPONSE = utils._load_xml(
            'ADFS_RequestSecurityTokenResponse.xml')
        self.ADFS_FAULT = utils._load_xml('ADFS_fault.xml')

    def test_get_adfs_security_token(self):
        """Test ADFSPassword._get_adfs_security_token()."""
        self.requests_mock.post(
            self.IDENTITY_PROVIDER_URL,
            content=utils.make_oneline(self.ADFS_SECURITY_TOKEN_RESPONSE),
            status_code=200)

        self.adfsplugin._prepare_adfs_request()
        self.adfsplugin._get_adfs_security_token(self.session)

        adfs_response = etree.tostring(self.adfsplugin.adfs_token)
        fixture_response = self.ADFS_SECURITY_TOKEN_RESPONSE

        self.assertThat(fixture_response,
                        matchers.XMLEquals(adfs_response))

    def test_adfs_request_user(self):
        self.adfsplugin._prepare_adfs_request()
        user = self.adfsplugin.prepared_request.xpath(
            self.USER_XPATH, namespaces=self.NAMESPACES)[0]
        self.assertEqual(self.TEST_USER, user.text)

    def test_adfs_request_password(self):
        self.adfsplugin._prepare_adfs_request()
        password = self.adfsplugin.prepared_request.xpath(
            self.PASSWORD_XPATH, namespaces=self.NAMESPACES)[0]
        self.assertEqual(self.TEST_TOKEN, password.text)

    def test_adfs_request_to(self):
        self.adfsplugin._prepare_adfs_request()
        to = self.adfsplugin.prepared_request.xpath(
            self.TO_XPATH, namespaces=self.NAMESPACES)[0]
        self.assertEqual(self.IDENTITY_PROVIDER_URL, to.text)

    def test_prepare_adfs_request_address(self):
        self.adfsplugin._prepare_adfs_request()
        address = self.adfsplugin.prepared_request.xpath(
            self.ADDRESS_XPATH, namespaces=self.NAMESPACES)[0]
        self.assertEqual(self.SP_ENDPOINT, address.text)

    def test_prepare_adfs_request_custom_endpointreference(self):
        self.adfsplugin = saml2.V3ADFSPassword(
            self.TEST_URL, self.IDENTITY_PROVIDER,
            self.IDENTITY_PROVIDER_URL, self.SP_ENDPOINT,
            self.TEST_USER, self.TEST_TOKEN, self.PROTOCOL, self.SP_ENTITYID)
        self.adfsplugin._prepare_adfs_request()
        address = self.adfsplugin.prepared_request.xpath(
            self.ADDRESS_XPATH, namespaces=self.NAMESPACES)[0]
        self.assertEqual(self.SP_ENTITYID, address.text)

    def test_prepare_sp_request(self):
        assertion = etree.XML(self.ADFS_SECURITY_TOKEN_RESPONSE)
        assertion = assertion.xpath(
            saml2.V3ADFSPassword.ADFS_ASSERTION_XPATH,
            namespaces=saml2.V3ADFSPassword.ADFS_TOKEN_NAMESPACES)
        assertion = assertion[0]
        assertion = etree.tostring(assertion)

        assertion = assertion.replace(
            b'http://docs.oasis-open.org/ws-sx/ws-trust/200512',
            b'http://schemas.xmlsoap.org/ws/2005/02/trust')
        assertion = urllib.parse.quote(assertion)
        assertion = 'wa=wsignin1.0&wresult=' + assertion

        self.adfsplugin.adfs_token = etree.XML(
            self.ADFS_SECURITY_TOKEN_RESPONSE)
        self.adfsplugin._prepare_sp_request()

        self.assertEqual(assertion, self.adfsplugin.encoded_assertion)

    def test_get_adfs_security_token_authn_fail(self):
        """Test proper parsing XML fault after bad authentication.

        An exceptions.AuthorizationFailure should be raised including
        error message from the XML message indicating where was the problem.
        """
        content = utils.make_oneline(self.ADFS_FAULT)
        self.requests_mock.register_uri('POST',
                                        self.IDENTITY_PROVIDER_URL,
                                        content=content,
                                        status_code=500)

        self.adfsplugin._prepare_adfs_request()
        self.assertRaises(exceptions.AuthorizationFailure,
                          self.adfsplugin._get_adfs_security_token,
                          self.session)
        # TODO(marek-denis): Python3 tests complain about missing 'message'
        # attributes
        # self.assertEqual('a:FailedAuthentication', e.message)

    def test_get_adfs_security_token_bad_response(self):
        """Test proper handling HTTP 500 and mangled (non XML) response.

        This should never happen yet, keystoneauth1 should be prepared
        and correctly raise exceptions.InternalServerError once it cannot
        parse XML fault message
        """
        self.requests_mock.register_uri('POST',
                                        self.IDENTITY_PROVIDER_URL,
                                        content=b'NOT XML',
                                        status_code=500)
        self.adfsplugin._prepare_adfs_request()
        self.assertRaises(exceptions.InternalServerError,
                          self.adfsplugin._get_adfs_security_token,
                          self.session)

    # TODO(marek-denis): Need to figure out how to properly send cookies
    # from the request_mock methods.
    def _send_assertion_to_service_provider(self):
        """Test whether SP issues a cookie."""
        cookie = uuid.uuid4().hex

        self.requests_mock.post(self.SP_ENDPOINT,
                                headers={"set-cookie": cookie},
                                status_code=302)

        self.adfsplugin.adfs_token = self._build_adfs_request()
        self.adfsplugin._prepare_sp_request()
        self.adfsplugin._send_assertion_to_service_provider(self.session)

        self.assertEqual(1, len(self.session.session.cookies))

    def test_send_assertion_to_service_provider_bad_status(self):
        self.requests_mock.register_uri('POST', self.SP_ENDPOINT,
                                        status_code=500)

        self.adfsplugin.adfs_token = etree.XML(
            self.ADFS_SECURITY_TOKEN_RESPONSE)
        self.adfsplugin._prepare_sp_request()

        self.assertRaises(
            exceptions.InternalServerError,
            self.adfsplugin._send_assertion_to_service_provider,
            self.session)

    def test_access_sp_no_cookies_fail(self):
        # clean cookie jar
        self.session.session.cookies = []

        self.assertRaises(exceptions.AuthorizationFailure,
                          self.adfsplugin._access_service_provider,
                          self.session)

    def test_check_valid_token_when_authenticated(self):
        self.requests_mock.register_uri(
            'GET', self.FEDERATION_AUTH_URL,
            json=saml2_fixtures.UNSCOPED_TOKEN,
            headers=client_fixtures.AUTH_RESPONSE_HEADERS)

        self.session.session.cookies = [object()]
        self.adfsplugin._access_service_provider(self.session)
        response = self.adfsplugin.authenticated_response

        self.assertEqual(client_fixtures.AUTH_RESPONSE_HEADERS,
                         response.headers)

        self.assertEqual(saml2_fixtures.UNSCOPED_TOKEN['token'],
                         response.json()['token'])

    def test_end_to_end_workflow(self):
        self.requests_mock.register_uri(
            'POST', self.IDENTITY_PROVIDER_URL,
            content=self.ADFS_SECURITY_TOKEN_RESPONSE,
            status_code=200)
        self.requests_mock.register_uri(
            'POST', self.SP_ENDPOINT,
            headers={"set-cookie": 'x'},
            status_code=302)
        self.requests_mock.register_uri(
            'GET', self.FEDERATION_AUTH_URL,
            json=saml2_fixtures.UNSCOPED_TOKEN,
            headers=client_fixtures.AUTH_RESPONSE_HEADERS)

        # NOTE(marek-denis): We need to mimic this until self.requests_mock can
        # issue cookies properly.
        self.session.session.cookies = [object()]
        token = self.adfsplugin.get_auth_ref(self.session)
        self.assertEqual(client_fixtures.AUTH_SUBJECT_TOKEN, token.auth_token)
