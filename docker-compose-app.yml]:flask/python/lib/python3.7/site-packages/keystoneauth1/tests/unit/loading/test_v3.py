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

import random
import uuid

from keystoneauth1 import exceptions
from keystoneauth1 import loading
from keystoneauth1.tests.unit.loading import utils


class V3PasswordTests(utils.TestCase):

    def setUp(self):
        super(V3PasswordTests, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader('v3password')
        return loader.load_from_options(**kwargs)

    def test_basic(self):
        username = uuid.uuid4().hex
        user_domain_id = uuid.uuid4().hex
        password = uuid.uuid4().hex
        project_name = uuid.uuid4().hex
        project_domain_id = uuid.uuid4().hex

        p = self.create(username=username,
                        user_domain_id=user_domain_id,
                        project_name=project_name,
                        project_domain_id=project_domain_id,
                        password=password)

        pw_method = p.auth_methods[0]

        self.assertEqual(username, pw_method.username)
        self.assertEqual(user_domain_id, pw_method.user_domain_id)
        self.assertEqual(password, pw_method.password)

        self.assertEqual(project_name, p.project_name)
        self.assertEqual(project_domain_id, p.project_domain_id)

    def test_without_user_domain(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          username=uuid.uuid4().hex,
                          password=uuid.uuid4().hex)

    def test_without_project_domain(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          username=uuid.uuid4().hex,
                          password=uuid.uuid4().hex,
                          user_domain_id=uuid.uuid4().hex,
                          project_name=uuid.uuid4().hex)


class TOTPTests(utils.TestCase):

    def setUp(self):
        super(TOTPTests, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader('v3totp')
        return loader.load_from_options(**kwargs)

    def test_basic(self):
        username = uuid.uuid4().hex
        user_domain_id = uuid.uuid4().hex
        # passcode is 6 digits
        passcode = ''.join(str(random.randint(0, 9)) for x in range(6))
        project_name = uuid.uuid4().hex
        project_domain_id = uuid.uuid4().hex

        p = self.create(username=username,
                        user_domain_id=user_domain_id,
                        project_name=project_name,
                        project_domain_id=project_domain_id,
                        passcode=passcode)

        totp_method = p.auth_methods[0]

        self.assertEqual(username, totp_method.username)
        self.assertEqual(user_domain_id, totp_method.user_domain_id)
        self.assertEqual(passcode, totp_method.passcode)

        self.assertEqual(project_name, p.project_name)
        self.assertEqual(project_domain_id, p.project_domain_id)

    def test_without_user_domain(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          username=uuid.uuid4().hex,
                          passcode=uuid.uuid4().hex)

    def test_without_project_domain(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          username=uuid.uuid4().hex,
                          passcode=uuid.uuid4().hex,
                          user_domain_id=uuid.uuid4().hex,
                          project_name=uuid.uuid4().hex)


class OpenIDConnectBaseTests(object):

    plugin_name = None

    def setUp(self):
        super(OpenIDConnectBaseTests, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader(self.plugin_name)
        return loader.load_from_options(**kwargs)

    def test_base_options_are_there(self):
        options = loading.get_plugin_loader(self.plugin_name).get_options()
        self.assertTrue(
            set(['client-id', 'client-secret', 'access-token-endpoint',
                 'access-token-type', 'openid-scope',
                 'discovery-endpoint']).issubset(
                     set([o.name for o in options]))
        )
        # openid-scope gets renamed into "scope"
        self.assertIn('scope', [o.dest for o in options])


class OpenIDConnectClientCredentialsTests(OpenIDConnectBaseTests,
                                          utils.TestCase):

    plugin_name = "v3oidcclientcredentials"

    def test_options(self):
        options = loading.get_plugin_loader(self.plugin_name).get_options()
        self.assertTrue(
            set(['openid-scope']).issubset(
                set([o.name for o in options]))
        )

    def test_basic(self):
        access_token_endpoint = uuid.uuid4().hex
        scope = uuid.uuid4().hex
        identity_provider = uuid.uuid4().hex
        protocol = uuid.uuid4().hex
        scope = uuid.uuid4().hex
        client_id = uuid.uuid4().hex
        client_secret = uuid.uuid4().hex

        oidc = self.create(identity_provider=identity_provider,
                           protocol=protocol,
                           access_token_endpoint=access_token_endpoint,
                           client_id=client_id,
                           client_secret=client_secret,
                           scope=scope)

        self.assertEqual(scope, oidc.scope)
        self.assertEqual(identity_provider, oidc.identity_provider)
        self.assertEqual(protocol, oidc.protocol)
        self.assertEqual(access_token_endpoint, oidc.access_token_endpoint)
        self.assertEqual(client_id, oidc.client_id)
        self.assertEqual(client_secret, oidc.client_secret)


class OpenIDConnectPasswordTests(OpenIDConnectBaseTests, utils.TestCase):

    plugin_name = "v3oidcpassword"

    def test_options(self):
        options = loading.get_plugin_loader(self.plugin_name).get_options()
        self.assertTrue(
            set(['username', 'password', 'openid-scope']).issubset(
                set([o.name for o in options]))
        )

    def test_basic(self):
        access_token_endpoint = uuid.uuid4().hex
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        scope = uuid.uuid4().hex
        identity_provider = uuid.uuid4().hex
        protocol = uuid.uuid4().hex
        scope = uuid.uuid4().hex
        client_id = uuid.uuid4().hex
        client_secret = uuid.uuid4().hex

        oidc = self.create(username=username,
                           password=password,
                           identity_provider=identity_provider,
                           protocol=protocol,
                           access_token_endpoint=access_token_endpoint,
                           client_id=client_id,
                           client_secret=client_secret,
                           scope=scope)

        self.assertEqual(username, oidc.username)
        self.assertEqual(password, oidc.password)
        self.assertEqual(scope, oidc.scope)
        self.assertEqual(identity_provider, oidc.identity_provider)
        self.assertEqual(protocol, oidc.protocol)
        self.assertEqual(access_token_endpoint, oidc.access_token_endpoint)
        self.assertEqual(client_id, oidc.client_id)
        self.assertEqual(client_secret, oidc.client_secret)


class OpenIDConnectAuthCodeTests(OpenIDConnectBaseTests, utils.TestCase):

    plugin_name = "v3oidcauthcode"

    def test_options(self):
        options = loading.get_plugin_loader(self.plugin_name).get_options()
        self.assertTrue(
            set(['redirect-uri', 'code']).issubset(
                set([o.name for o in options]))
        )

    def test_basic(self):
        access_token_endpoint = uuid.uuid4().hex
        redirect_uri = uuid.uuid4().hex
        authorization_code = uuid.uuid4().hex
        scope = uuid.uuid4().hex
        identity_provider = uuid.uuid4().hex
        protocol = uuid.uuid4().hex
        client_id = uuid.uuid4().hex
        client_secret = uuid.uuid4().hex

        oidc = self.create(code=authorization_code,
                           redirect_uri=redirect_uri,
                           identity_provider=identity_provider,
                           protocol=protocol,
                           access_token_endpoint=access_token_endpoint,
                           client_id=client_id,
                           client_secret=client_secret,
                           scope=scope)

        self.assertEqual(redirect_uri, oidc.redirect_uri)
        self.assertEqual(authorization_code, oidc.code)
        self.assertEqual(scope, oidc.scope)
        self.assertEqual(identity_provider, oidc.identity_provider)
        self.assertEqual(protocol, oidc.protocol)
        self.assertEqual(access_token_endpoint, oidc.access_token_endpoint)
        self.assertEqual(client_id, oidc.client_id)
        self.assertEqual(client_secret, oidc.client_secret)


class OpenIDConnectAccessToken(utils.TestCase):

    plugin_name = "v3oidcaccesstoken"

    def setUp(self):
        super(OpenIDConnectAccessToken, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader(self.plugin_name)
        return loader.load_from_options(**kwargs)

    def test_options(self):
        options = loading.get_plugin_loader(self.plugin_name).get_options()
        self.assertTrue(
            set(['access-token']).issubset(
                set([o.name for o in options]))
        )

    def test_basic(self):
        access_token = uuid.uuid4().hex
        identity_provider = uuid.uuid4().hex
        protocol = uuid.uuid4().hex

        oidc = self.create(access_token=access_token,
                           identity_provider=identity_provider,
                           protocol=protocol)

        self.assertEqual(identity_provider, oidc.identity_provider)
        self.assertEqual(protocol, oidc.protocol)
        self.assertEqual(access_token, oidc.access_token)


class V3TokenlessAuthTests(utils.TestCase):

    def setUp(self):
        super(V3TokenlessAuthTests, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader('v3tokenlessauth')
        return loader.load_from_options(**kwargs)

    def test_basic(self):
        domain_id = uuid.uuid4().hex
        domain_name = uuid.uuid4().hex
        project_id = uuid.uuid4().hex
        project_name = uuid.uuid4().hex
        project_domain_id = uuid.uuid4().hex
        project_domain_name = uuid.uuid4().hex

        tla = self.create(domain_id=domain_id,
                          domain_name=domain_name,
                          project_id=project_id,
                          project_name=project_name,
                          project_domain_id=project_domain_id,
                          project_domain_name=project_domain_name)

        self.assertEqual(domain_id, tla.domain_id)
        self.assertEqual(domain_name, tla.domain_name)
        self.assertEqual(project_id, tla.project_id)
        self.assertEqual(project_name, tla.project_name)
        self.assertEqual(project_domain_id, tla.project_domain_id)
        self.assertEqual(project_domain_name, tla.project_domain_name)

    def test_missing_parameters(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          domain_id=None)
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          domain_name=None)
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_id=None)
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_name=None)
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_domain_id=None)
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_domain_name=None)
        # only when a project_name is provided, project_domain_id will
        # be use to uniquely identify the project. It's an invalid
        # option when it's just by itself.
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_domain_id=uuid.uuid4().hex)
        # only when a project_name is provided, project_domain_name will
        # be use to uniquely identify the project. It's an invalid
        # option when it's just by itself.
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_domain_name=uuid.uuid4().hex)
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          project_name=uuid.uuid4().hex)


class V3ApplicationCredentialTests(utils.TestCase):

    def setUp(self):
        super(V3ApplicationCredentialTests, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader('v3applicationcredential')
        return loader.load_from_options(**kwargs)

    def test_basic(self):
        id = uuid.uuid4().hex
        secret = uuid.uuid4().hex

        app_cred = self.create(application_credential_id=id,
                               application_credential_secret=secret)

        ac_method = app_cred.auth_methods[0]

        self.assertEqual(id, ac_method.application_credential_id)
        self.assertEqual(secret, ac_method.application_credential_secret)

    def test_with_name(self):
        name = uuid.uuid4().hex
        secret = uuid.uuid4().hex
        username = uuid.uuid4().hex
        user_domain_id = uuid.uuid4().hex

        app_cred = self.create(application_credential_name=name,
                               application_credential_secret=secret,
                               username=username,
                               user_domain_id=user_domain_id)

        ac_method = app_cred.auth_methods[0]

        self.assertEqual(name, ac_method.application_credential_name)
        self.assertEqual(secret, ac_method.application_credential_secret)
        self.assertEqual(username, ac_method.username)
        self.assertEqual(user_domain_id, ac_method.user_domain_id)

    def test_without_user_domain(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          application_credential_name=uuid.uuid4().hex,
                          username=uuid.uuid4().hex,
                          application_credential_secret=uuid.uuid4().hex)

    def test_without_name_or_id(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          username=uuid.uuid4().hex,
                          user_domain_id=uuid.uuid4().hex,
                          application_credential_secret=uuid.uuid4().hex)

    def test_without_secret(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          application_credential_id=uuid.uuid4().hex,
                          username=uuid.uuid4().hex,
                          user_domain_id=uuid.uuid4().hex)


class MultiFactorTests(utils.TestCase):

    def setUp(self):
        super(MultiFactorTests, self).setUp()

        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader('v3multifactor')
        return loader.load_from_options(**kwargs)

    def test_password_and_totp(self):
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        user_domain_id = uuid.uuid4().hex
        # passcode is 6 digits
        passcode = ''.join(str(random.randint(0, 9)) for x in range(6))
        project_name = uuid.uuid4().hex
        project_domain_id = uuid.uuid4().hex

        p = self.create(
            auth_methods=['v3password', 'v3totp'],
            username=username,
            password=password,
            user_domain_id=user_domain_id,
            project_name=project_name,
            project_domain_id=project_domain_id,
            passcode=passcode)

        password_method = p.auth_methods[0]
        totp_method = p.auth_methods[1]

        self.assertEqual(username, password_method.username)
        self.assertEqual(user_domain_id, password_method.user_domain_id)
        self.assertEqual(password, password_method.password)

        self.assertEqual(username, totp_method.username)
        self.assertEqual(user_domain_id, totp_method.user_domain_id)
        self.assertEqual(passcode, totp_method.passcode)

        self.assertEqual(project_name, p.project_name)
        self.assertEqual(project_domain_id, p.project_domain_id)

    def test_without_methods(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          username=uuid.uuid4().hex,
                          passcode=uuid.uuid4().hex)

    def test_without_user_domain_for_password(self):
        self.assertRaises(exceptions.OptionError,
                          self.create,
                          methods=['v3password'],
                          username=uuid.uuid4().hex,
                          project_name=uuid.uuid4().hex,
                          project_domain_id=uuid.uuid4().hex)
