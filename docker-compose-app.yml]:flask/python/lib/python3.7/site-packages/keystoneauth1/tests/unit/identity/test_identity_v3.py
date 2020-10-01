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

import copy
import json
import time
import uuid

from keystoneauth1 import _utils as ksa_utils
from keystoneauth1 import access
from keystoneauth1 import exceptions
from keystoneauth1 import fixture
from keystoneauth1.identity import v3
from keystoneauth1.identity.v3 import base as v3_base
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils


class V3IdentityPlugin(utils.TestCase):

    TEST_ROOT_URL = 'http://127.0.0.1:5000/'
    TEST_URL = '%s%s' % (TEST_ROOT_URL, 'v3')
    TEST_ROOT_ADMIN_URL = 'http://127.0.0.1:35357/'
    TEST_ADMIN_URL = '%s%s' % (TEST_ROOT_ADMIN_URL, 'v3')

    TEST_PASS = 'password'

    TEST_APP_CRED_ID = 'appcredid'
    TEST_APP_CRED_SECRET = 'secret'

    TEST_SERVICE_CATALOG = [{
        "endpoints": [{
            "url": "http://cdn.admin-nets.local:8774/v1.0/",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://127.0.0.1:8774/v1.0",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://cdn.admin-nets.local:8774/v1.0",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "nova_compat"
    }, {
        "endpoints": [{
            "url": "http://nova/novapi/public",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://nova/novapi/internal",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://nova/novapi/admin",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "compute",
        "name": "nova",
    }, {
        "endpoints": [{
            "url": "http://glance/glanceapi/public",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://glance/glanceapi/internal",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://glance/glanceapi/admin",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "image",
        "name": "glance"
    }, {
        "endpoints": [{
            "url": "http://127.0.0.1:5000/v3",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://127.0.0.1:5000/v3",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": TEST_ADMIN_URL,
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "identity"
    }, {
        "endpoints": [{
            "url": "http://swift/swiftapi/public",
            "region": "RegionOne",
            "interface": "public"
        }, {
            "url": "http://swift/swiftapi/internal",
            "region": "RegionOne",
            "interface": "internal"
        }, {
            "url": "http://swift/swiftapi/admin",
            "region": "RegionOne",
            "interface": "admin"
        }],
        "type": "object-store"
    }]

    TEST_SERVICE_PROVIDERS = [
        {
            "auth_url": "https://sp1.com/v3/OS-FEDERATION/"
                        "identity_providers/acme/protocols/saml2/auth",
            "id": "sp1",
            "sp_url": "https://sp1.com/Shibboleth.sso/SAML2/ECP"
        }, {
            "auth_url": "https://sp2.com/v3/OS-FEDERATION/"
                        "identity_providers/acme/protocols/saml2/auth",
            "id": "sp2",
            "sp_url": "https://sp2.com/Shibboleth.sso/SAML2/ECP"
        }
    ]

    def setUp(self):
        super(V3IdentityPlugin, self).setUp()

        self.TEST_DISCOVERY_RESPONSE = {
            'versions': {'values': [fixture.V3Discovery(self.TEST_URL)]}}

        nextyear = 1 + time.gmtime().tm_year
        self.TEST_RESPONSE_DICT = {
            "token": {
                "methods": [
                    "token",
                    "password"
                ],

                "expires_at": "%i-02-01T00:00:10.000123Z" % nextyear,
                "project": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME
                    },
                    "id": self.TEST_TENANT_ID,
                    "name": self.TEST_TENANT_NAME
                },
                "user": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME
                    },
                    "id": self.TEST_USER,
                    "name": self.TEST_USER
                },
                "issued_at": "2013-05-29T16:55:21.468960Z",
                "catalog": self.TEST_SERVICE_CATALOG,
                "service_providers": self.TEST_SERVICE_PROVIDERS
            },
        }
        self.TEST_PROJECTS_RESPONSE = {
            "projects": [
                {
                    "domain_id": "1789d1",
                    "enabled": "True",
                    "id": "263fd9",
                    "links": {
                        "self": "https://identity:5000/v3/projects/263fd9"
                    },
                    "name": "Dev Group A"
                },
                {
                    "domain_id": "1789d1",
                    "enabled": "True",
                    "id": "e56ad3",
                    "links": {
                        "self": "https://identity:5000/v3/projects/e56ad3"
                    },
                    "name": "Dev Group B"
                }
            ],
            "links": {
                "self": "https://identity:5000/v3/projects",
            }
        }
        self.TEST_APP_CRED_TOKEN_RESPONSE = {
            "token": {
                "methods": [
                    "application_credential"
                ],

                "expires_at": "%i-02-01T00:00:10.000123Z" % nextyear,
                "project": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME
                    },
                    "id": self.TEST_TENANT_ID,
                    "name": self.TEST_TENANT_NAME
                },
                "user": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME
                    },
                    "id": self.TEST_USER,
                    "name": self.TEST_USER
                },
                "issued_at": "2013-05-29T16:55:21.468960Z",
                "catalog": self.TEST_SERVICE_CATALOG,
                "service_providers": self.TEST_SERVICE_PROVIDERS,
                "application_credential_restricted": True
            },
        }
        self.TEST_RECEIPT_RESPONSE = {
            "receipt": {
                "methods": ["password"],
                "expires_at": "%i-02-01T00:00:10.000123Z" % nextyear,
                "user": {
                    "domain": {
                        "id": self.TEST_DOMAIN_ID,
                        "name": self.TEST_DOMAIN_NAME,
                    },
                    "id": self.TEST_USER,
                    "name": self.TEST_USER,
                },
                "issued_at": "2013-05-29T16:55:21.468960Z",
            },
            "required_auth_methods": [["password", "totp"]],
        }

    def stub_auth(self, subject_token=None, **kwargs):
        if not subject_token:
            subject_token = self.TEST_TOKEN

        self.stub_url('POST', ['auth', 'tokens'],
                      headers={'X-Subject-Token': subject_token}, **kwargs)

    def stub_receipt(self, receipt=None, receipt_data=None, **kwargs):
        if not receipt:
            receipt = self.TEST_RECEIPT

        if not receipt_data:
            receipt_data = self.TEST_RECEIPT_RESPONSE

        self.stub_url('POST', ['auth', 'tokens'],
                      headers={'Openstack-Auth-Receipt': receipt},
                      status_code=401,
                      json=receipt_data,
                      **kwargs)

    def test_authenticate_with_username_password(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        a = v3.Password(self.TEST_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS)
        self.assertFalse(a.has_scope_parameters)
        s = session.Session(auth=a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}}}}}

        self.assertRequestBodyIs(json=req)
        self.assertRequestHeaderEqual('Content-Type', 'application/json')
        self.assertRequestHeaderEqual('Accept', 'application/json')
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_authenticate_with_username_password_domain_scoped(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS, domain_id=self.TEST_DOMAIN_ID)
        self.assertTrue(a.has_scope_parameters)
        s = session.Session(a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}}},
               'scope': {'domain': {'id': self.TEST_DOMAIN_ID}}}}
        self.assertRequestBodyIs(json=req)
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_authenticate_with_username_password_project_scoped(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS,
                        project_id=self.TEST_TENANT_ID)
        self.assertTrue(a.has_scope_parameters)
        s = session.Session(a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}}},
               'scope': {'project': {'id': self.TEST_TENANT_ID}}}}
        self.assertRequestBodyIs(json=req)
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)
        self.assertEqual(s.auth.auth_ref.project_id, self.TEST_TENANT_ID)

    def test_authenticate_with_token(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        a = v3.Token(self.TEST_URL, self.TEST_TOKEN)
        s = session.Session(auth=a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['token'],
                'token': {'id': self.TEST_TOKEN}}}}

        self.assertRequestBodyIs(json=req)

        self.assertRequestHeaderEqual('Content-Type', 'application/json')
        self.assertRequestHeaderEqual('Accept', 'application/json')
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_with_expired(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)

        d = copy.deepcopy(self.TEST_RESPONSE_DICT)
        d['token']['expires_at'] = '2000-01-01T00:00:10.000123Z'

        a = v3.Password(self.TEST_URL, username='username',
                        password='password')
        a.auth_ref = access.create(body=d)
        s = session.Session(auth=a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        self.assertEqual(a.auth_ref._data['token']['expires_at'],
                         self.TEST_RESPONSE_DICT['token']['expires_at'])

    def test_with_domain_and_project_scoping(self):
        a = v3.Password(self.TEST_URL, username='username',
                        password='password', project_id='project',
                        domain_id='domain')

        self.assertTrue(a.has_scope_parameters)
        self.assertRaises(exceptions.AuthorizationFailure,
                          a.get_token, None)
        self.assertRaises(exceptions.AuthorizationFailure,
                          a.get_headers, None)

    def test_with_trust_id(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS, trust_id='trust')
        self.assertTrue(a.has_scope_parameters)
        s = session.Session(a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}}},
               'scope': {'OS-TRUST:trust': {'id': 'trust'}}}}
        self.assertRequestBodyIs(json=req)
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_with_multiple_mechanisms_factory(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        p = v3.PasswordMethod(username=self.TEST_USER, password=self.TEST_PASS)
        t = v3.TokenMethod(token='foo')
        a = v3.Auth(self.TEST_URL, [p, t], trust_id='trust')
        s = session.Session(a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password', 'token'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}},
                'token': {'id': 'foo'}},
               'scope': {'OS-TRUST:trust': {'id': 'trust'}}}}
        self.assertRequestBodyIs(json=req)
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_with_multiple_mechanisms(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        p = v3.PasswordMethod(username=self.TEST_USER,
                              password=self.TEST_PASS)
        t = v3.TokenMethod(token='foo')
        a = v3.Auth(self.TEST_URL, [p, t], trust_id='trust')
        self.assertTrue(a.has_scope_parameters)
        s = session.Session(auth=a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password', 'token'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}},
                'token': {'id': 'foo'}},
               'scope': {'OS-TRUST:trust': {'id': 'trust'}}}}
        self.assertRequestBodyIs(json=req)
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_with_multiple_scopes(self):
        s = session.Session()

        a = v3.Password(self.TEST_URL,
                        username=self.TEST_USER, password=self.TEST_PASS,
                        domain_id='x', project_id='x')
        self.assertRaises(exceptions.AuthorizationFailure, a.get_auth_ref, s)

        a = v3.Password(self.TEST_URL,
                        username=self.TEST_USER, password=self.TEST_PASS,
                        domain_id='x', trust_id='x')
        self.assertRaises(exceptions.AuthorizationFailure, a.get_auth_ref, s)

    def test_application_credential_method(self):
        self.stub_auth(json=self.TEST_APP_CRED_TOKEN_RESPONSE)
        ac = v3.ApplicationCredential(
            self.TEST_URL, application_credential_id=self.TEST_APP_CRED_ID,
            application_credential_secret=self.TEST_APP_CRED_SECRET)
        req = {'auth': {'identity':
               {'methods': ['application_credential'],
                'application_credential': {
                    'id': self.TEST_APP_CRED_ID,
                    'secret': self.TEST_APP_CRED_SECRET}}}}
        s = session.Session(auth=ac)
        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())
        self.assertRequestBodyIs(json=req)
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def _do_service_url_test(self, base_url, endpoint_filter):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        self.stub_url('GET', ['path'],
                      base_url=base_url,
                      text='SUCCESS', status_code=200)

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session(auth=a)

        resp = s.get('/path', endpoint_filter=endpoint_filter)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.requests_mock.last_request.url,
                         base_url + '/path')

    def test_service_url(self):
        endpoint_filter = {'service_type': 'compute',
                           'interface': 'admin',
                           'service_name': 'nova'}
        self._do_service_url_test('http://nova/novapi/admin', endpoint_filter)

    def test_service_url_defaults_to_public(self):
        endpoint_filter = {'service_type': 'compute'}
        self._do_service_url_test('http://nova/novapi/public', endpoint_filter)

    def test_endpoint_filter_without_service_type_fails(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session(auth=a)

        self.assertRaises(exceptions.EndpointNotFound, s.get, '/path',
                          endpoint_filter={'interface': 'admin'})

    def test_full_url_overrides_endpoint_filter(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        self.stub_url('GET', [],
                      base_url='http://testurl/',
                      text='SUCCESS', status_code=200)

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session(auth=a)

        resp = s.get('http://testurl/',
                     endpoint_filter={'service_type': 'compute'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.text, 'SUCCESS')

    def test_service_providers_urls(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session()
        auth_ref = a.get_auth_ref(s)

        service_providers = auth_ref.service_providers
        self.assertEqual('https://sp1.com/v3/OS-FEDERATION/'
                         'identity_providers/acme/protocols/saml2/auth',
                         service_providers.get_auth_url('sp1'))
        self.assertEqual('https://sp1.com/Shibboleth.sso/SAML2/ECP',
                         service_providers.get_sp_url('sp1'))
        self.assertEqual('https://sp2.com/v3/OS-FEDERATION/'
                         'identity_providers/acme/protocols/saml2/auth',
                         service_providers.get_auth_url('sp2'))
        self.assertEqual('https://sp2.com/Shibboleth.sso/SAML2/ECP',
                         service_providers.get_sp_url('sp2'))

    def test_handle_missing_service_provider(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session()
        auth_ref = a.get_auth_ref(s)

        service_providers = auth_ref.service_providers

        self.assertRaises(exceptions.ServiceProviderNotFound,
                          service_providers._get_service_provider,
                          uuid.uuid4().hex)

    def test_invalid_auth_response_dict(self):
        self.stub_auth(json={'hello': 'world'})

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session(auth=a)

        self.assertRaises(exceptions.InvalidResponse, s.get, 'http://any',
                          authenticated=True)

    def test_invalid_auth_response_type(self):
        self.stub_url('POST', ['auth', 'tokens'], text='testdata')

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session(auth=a)

        self.assertRaises(exceptions.InvalidResponse, s.get, 'http://any',
                          authenticated=True)

    def test_invalidate_response(self):
        auth_responses = [{'status_code': 200, 'json': self.TEST_RESPONSE_DICT,
                           'headers': {'X-Subject-Token': 'token1'}},
                          {'status_code': 200, 'json': self.TEST_RESPONSE_DICT,
                           'headers': {'X-Subject-Token': 'token2'}}]

        self.requests_mock.post('%s/auth/tokens' % self.TEST_URL,
                                auth_responses)

        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=self.TEST_PASS)
        s = session.Session(auth=a)

        self.assertEqual('token1', s.get_token())
        self.assertEqual({'X-Auth-Token': 'token1'}, s.get_auth_headers())
        a.invalidate()
        self.assertEqual('token2', s.get_token())
        self.assertEqual({'X-Auth-Token': 'token2'}, s.get_auth_headers())

    def test_doesnt_log_password(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)

        password = uuid.uuid4().hex
        a = v3.Password(self.TEST_URL, username=self.TEST_USER,
                        password=password)
        s = session.Session(a)
        self.assertEqual(self.TEST_TOKEN, s.get_token())
        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        self.assertNotIn(password, self.logger.output)

    def test_sends_nocatalog(self):
        del self.TEST_RESPONSE_DICT['token']['catalog']
        self.stub_auth(json=self.TEST_RESPONSE_DICT)

        a = v3.Password(self.TEST_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS,
                        include_catalog=False)
        s = session.Session(auth=a)

        s.get_token()

        auth_url = self.TEST_URL + '/auth/tokens'
        self.assertEqual(auth_url, a.token_url)
        self.assertEqual(auth_url + '?nocatalog',
                         self.requests_mock.last_request.url)

    def test_symbols(self):
        self.assertIs(v3.AuthMethod, v3_base.AuthMethod)
        self.assertIs(v3.AuthConstructor, v3_base.AuthConstructor)
        self.assertIs(v3.Auth, v3_base.Auth)

    def test_unscoped_request(self):
        token = fixture.V3Token()
        self.stub_auth(json=token)
        password = uuid.uuid4().hex

        a = v3.Password(self.TEST_URL,
                        user_id=token.user_id,
                        password=password,
                        unscoped=True)
        s = session.Session()

        auth_ref = a.get_access(s)

        self.assertFalse(auth_ref.scoped)
        body = self.requests_mock.last_request.json()

        ident = body['auth']['identity']

        self.assertEqual(['password'], ident['methods'])
        self.assertEqual(token.user_id, ident['password']['user']['id'])
        self.assertEqual(password, ident['password']['user']['password'])

        self.assertEqual('unscoped', body['auth']['scope'])

    def test_unscoped_with_scope_data(self):
        a = v3.Password(self.TEST_URL,
                        user_id=uuid.uuid4().hex,
                        password=uuid.uuid4().hex,
                        unscoped=True,
                        project_id=uuid.uuid4().hex)

        s = session.Session()

        self.assertRaises(exceptions.AuthorizationFailure, a.get_auth_ref, s)

    def test_password_cache_id(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        project_name = uuid.uuid4().hex

        a = v3.Password(self.TEST_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS,
                        user_domain_id=self.TEST_DOMAIN_ID,
                        project_domain_name=self.TEST_DOMAIN_NAME,
                        project_name=project_name)

        b = v3.Password(self.TEST_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS,
                        user_domain_id=self.TEST_DOMAIN_ID,
                        project_domain_name=self.TEST_DOMAIN_NAME,
                        project_name=project_name)

        a_id = a.get_cache_id()
        b_id = b.get_cache_id()

        self.assertEqual(a_id, b_id)

        c = v3.Password(self.TEST_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS,
                        user_domain_id=self.TEST_DOMAIN_ID,
                        project_domain_name=self.TEST_DOMAIN_NAME,
                        project_id=project_name)  # same value different param

        c_id = c.get_cache_id()

        self.assertNotEqual(a_id, c_id)

        self.assertIsNone(a.get_auth_state())
        self.assertIsNone(b.get_auth_state())
        self.assertIsNone(c.get_auth_state())

        s = session.Session()
        self.assertEqual(self.TEST_TOKEN, a.get_token(s))
        self.assertTrue(self.requests_mock.called)

    def test_password_change_auth_state(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)

        expired = ksa_utils.before_utcnow(days=2)
        token = fixture.V3Token(expires=expired)
        token_id = uuid.uuid4().hex

        state = json.dumps({'auth_token': token_id, 'body': token})

        a = v3.Password(self.TEST_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS,
                        user_domain_id=self.TEST_DOMAIN_ID,
                        project_id=uuid.uuid4().hex)

        initial_cache_id = a.get_cache_id()

        self.assertIsNone(a.get_auth_state())
        a.set_auth_state(state)

        self.assertEqual(token_id, a.auth_ref.auth_token)

        s = session.Session()
        self.assertEqual(self.TEST_TOKEN, a.get_token(s))  # updates expired
        self.assertEqual(initial_cache_id, a.get_cache_id())

    def test_receipt_response_is_handled(self):
        self.stub_receipt()

        a = v3.Password(
            self.TEST_URL,
            username=self.TEST_USER,
            password=self.TEST_PASS,
            user_domain_id=self.TEST_DOMAIN_ID,
            project_id=self.TEST_TENANT_ID,
        )

        s = session.Session(a)
        self.assertRaises(exceptions.MissingAuthMethods,
                          s.get_auth_headers, None)

    def test_authenticate_with_receipt_and_totp(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        passcode = "123456"
        auth = v3.TOTP(
            self.TEST_URL,
            username=self.TEST_USER,
            passcode=passcode
        )
        auth.add_method(v3.ReceiptMethod(receipt=self.TEST_RECEIPT))
        self.assertFalse(auth.has_scope_parameters)
        s = session.Session(auth=auth)

        self.assertEqual({"X-Auth-Token": self.TEST_TOKEN},
                         s.get_auth_headers())

        # NOTE(adriant): Here we are confirming the receipt data isn't in the
        # body or listed as a method
        req = {
            "auth": {
                "identity": {
                    "methods": ["totp"],
                    "totp": {"user": {
                        "name": self.TEST_USER, "passcode": passcode}},
                }
            }
        }

        self.assertRequestBodyIs(json=req)
        self.assertRequestHeaderEqual("Openstack-Auth-Receipt",
                                      self.TEST_RECEIPT)
        self.assertRequestHeaderEqual("Content-Type", "application/json")
        self.assertRequestHeaderEqual("Accept", "application/json")
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_authenticate_with_multi_factor(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        passcode = "123456"
        auth = v3.MultiFactor(
            self.TEST_URL,
            auth_methods=['v3password', 'v3totp'],
            username=self.TEST_USER,
            password=self.TEST_PASS,
            passcode=passcode,
            user_domain_id=self.TEST_DOMAIN_ID,
            project_id=self.TEST_TENANT_ID,
        )
        self.assertTrue(auth.has_scope_parameters)
        s = session.Session(auth=auth)

        self.assertEqual({"X-Auth-Token": self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {
            "auth": {
                "identity": {
                    "methods": ["password", "totp"],
                    "totp": {"user": {
                        "name": self.TEST_USER, "passcode": passcode,
                        'domain': {'id': self.TEST_DOMAIN_ID}
                    }},
                    'password': {'user': {
                        'name': self.TEST_USER, 'password': self.TEST_PASS,
                        'domain': {'id': self.TEST_DOMAIN_ID}
                    }},
                },
                'scope': {'project': {'id': self.TEST_TENANT_ID}}
            }
        }

        self.assertRequestBodyIs(json=req)
        self.assertRequestHeaderEqual("Content-Type", "application/json")
        self.assertRequestHeaderEqual("Accept", "application/json")
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)

    def test_authenticate_with_unversioned_endpoint(self):
        self.stub_auth(json=self.TEST_RESPONSE_DICT)
        # We use the root url here because it doesn't reference the API version
        # (e.g., '/v3'). We want to make sure the authentication plugin handles
        # this and appends /v3 if it's not present.
        a = v3.Password(self.TEST_ROOT_URL,
                        username=self.TEST_USER,
                        password=self.TEST_PASS)
        self.assertFalse(a.has_scope_parameters)
        s = session.Session(auth=a)

        self.assertEqual({'X-Auth-Token': self.TEST_TOKEN},
                         s.get_auth_headers())

        req = {'auth': {'identity':
               {'methods': ['password'],
                'password': {'user': {'name': self.TEST_USER,
                                      'password': self.TEST_PASS}}}}}

        self.assertRequestBodyIs(json=req)
        self.assertRequestHeaderEqual('Content-Type', 'application/json')
        self.assertRequestHeaderEqual('Accept', 'application/json')
        self.assertEqual(s.auth.auth_ref.auth_token, self.TEST_TOKEN)
