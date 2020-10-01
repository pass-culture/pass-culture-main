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

from keystoneauth1.extras import kerberos
from keystoneauth1 import fixture as ks_fixture
from keystoneauth1 import session
from keystoneauth1.tests.unit.extras.kerberos import base


class TestMappedAuth(base.TestCase):

    def setUp(self):
        if kerberos.requests_kerberos is None:
            self.skipTest("Kerberos support isn't available.")

        super(TestMappedAuth, self).setUp()

        self.protocol = uuid.uuid4().hex
        self.identity_provider = uuid.uuid4().hex

    @property
    def token_url(self):
        fmt = '%s/OS-FEDERATION/identity_providers/%s/protocols/%s/auth'
        return fmt % (
            self.TEST_V3_URL,
            self.identity_provider,
            self.protocol)

    def test_unscoped_mapped_auth(self):
        token_id, _ = self.kerberos_mock.mock_auth_success(
            url=self.token_url, method='GET')

        plugin = kerberos.MappedKerberos(
            auth_url=self.TEST_V3_URL, protocol=self.protocol,
            identity_provider=self.identity_provider)

        sess = session.Session()
        tok = plugin.get_token(sess)

        self.assertEqual(token_id, tok)

    def test_project_scoped_mapped_auth(self):
        self.kerberos_mock.mock_auth_success(url=self.token_url,
                                             method='GET')

        scoped_id = uuid.uuid4().hex
        scoped_body = ks_fixture.V3Token()
        scoped_body.set_project_scope()

        self.requests_mock.post(
            '%s/auth/tokens' % self.TEST_V3_URL,
            json=scoped_body,
            headers={'X-Subject-Token': scoped_id,
                     'Content-Type': 'application/json'})

        plugin = kerberos.MappedKerberos(
            auth_url=self.TEST_V3_URL, protocol=self.protocol,
            identity_provider=self.identity_provider,
            project_id=scoped_body.project_id)

        sess = session.Session()
        tok = plugin.get_token(sess)
        proj = plugin.get_project_id(sess)

        self.assertEqual(scoped_id, tok)
        self.assertEqual(scoped_body.project_id, proj)

    def test_authenticate_with_mutual_authentication_required(self):
        self.kerberos_mock.mock_auth_success(url=self.token_url,
                                             method='GET')

        scoped_id = uuid.uuid4().hex
        scoped_body = ks_fixture.V3Token()
        scoped_body.set_project_scope()

        self.requests_mock.post(
            '%s/auth/tokens' % self.TEST_V3_URL,
            json=scoped_body,
            headers={'X-Subject-Token': scoped_id,
                     'Content-Type': 'application/json'})

        plugin = kerberos.MappedKerberos(
            auth_url=self.TEST_V3_URL, protocol=self.protocol,
            identity_provider=self.identity_provider,
            project_id=scoped_body.project_id,
            mutual_auth='required')

        sess = session.Session()
        tok = plugin.get_token(sess)
        proj = plugin.get_project_id(sess)

        self.assertEqual(scoped_id, tok)
        self.assertEqual(scoped_body.project_id, proj)
        self.assertEqual(self.kerberos_mock.called_auth_server, True)

    def test_authenticate_with_mutual_authentication_disabled(self):
        self.kerberos_mock.mock_auth_success(url=self.token_url,
                                             method='GET')

        scoped_id = uuid.uuid4().hex
        scoped_body = ks_fixture.V3Token()
        scoped_body.set_project_scope()

        self.requests_mock.post(
            '%s/auth/tokens' % self.TEST_V3_URL,
            json=scoped_body,
            headers={'X-Subject-Token': scoped_id,
                     'Content-Type': 'application/json'})

        plugin = kerberos.MappedKerberos(
            auth_url=self.TEST_V3_URL, protocol=self.protocol,
            identity_provider=self.identity_provider,
            project_id=scoped_body.project_id,
            mutual_auth='disabled')

        sess = session.Session()
        tok = plugin.get_token(sess)
        proj = plugin.get_project_id(sess)

        self.assertEqual(scoped_id, tok)
        self.assertEqual(scoped_body.project_id, proj)
        self.assertEqual(self.kerberos_mock.called_auth_server, False)
