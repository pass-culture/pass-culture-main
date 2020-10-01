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

import datetime
import uuid

from oslo_utils import timeutils

from keystoneauth1 import access
from keystoneauth1 import fixture
from keystoneauth1.tests.unit import utils


class AccessV3Test(utils.TestCase):

    def test_building_unscoped_accessinfo(self):
        token = fixture.V3Token()
        token_id = uuid.uuid4().hex

        auth_ref = access.create(body=token, auth_token=token_id)

        self.assertIn('methods', auth_ref._data['token'])
        self.assertFalse(auth_ref.has_service_catalog())
        self.assertNotIn('catalog', auth_ref._data['token'])

        self.assertEqual(token_id, auth_ref.auth_token)
        self.assertEqual(token.user_name, auth_ref.username)
        self.assertEqual(token.user_id, auth_ref.user_id)

        self.assertEqual(auth_ref.role_ids, [])
        self.assertEqual(auth_ref.role_names, [])

        self.assertIsNone(auth_ref.project_name)
        self.assertIsNone(auth_ref.project_id)

        self.assertFalse(auth_ref.domain_scoped)
        self.assertFalse(auth_ref.project_scoped)
        self.assertIsNone(auth_ref.project_is_domain)

        self.assertEqual(token.user_domain_id, auth_ref.user_domain_id)
        self.assertEqual(token.user_domain_name, auth_ref.user_domain_name)

        self.assertIsNone(auth_ref.project_domain_id)
        self.assertIsNone(auth_ref.project_domain_name)

        self.assertEqual(auth_ref.expires, timeutils.parse_isotime(
                         token['token']['expires_at']))
        self.assertEqual(auth_ref.issued, timeutils.parse_isotime(
                         token['token']['issued_at']))

        self.assertEqual(auth_ref.expires, token.expires)
        self.assertEqual(auth_ref.issued, token.issued)

        self.assertEqual(auth_ref.audit_id, token.audit_id)
        self.assertIsNone(auth_ref.audit_chain_id)
        self.assertIsNone(token.audit_chain_id)
        self.assertIsNone(auth_ref.bind)

    def test_will_expire_soon(self):
        expires = timeutils.utcnow() + datetime.timedelta(minutes=5)
        token = fixture.V3Token(expires=expires)
        auth_ref = access.create(body=token)
        self.assertFalse(auth_ref.will_expire_soon(stale_duration=120))
        self.assertTrue(auth_ref.will_expire_soon(stale_duration=301))
        self.assertFalse(auth_ref.will_expire_soon())

    def test_building_system_scoped_assessinfo(self):
        token = fixture.V3Token()
        token.set_system_scope()

        s = token.add_service(type='identity')
        s.add_standard_endpoints(public='http://url')

        token_id = uuid.uuid4().hex

        auth_ref = access.create(body=token, auth_token=token_id)

        self.assertTrue(auth_ref)
        self.assertIn('methods', auth_ref._data['token'])
        self.assertIn('catalog', auth_ref._data['token'])
        self.assertTrue(auth_ref.has_service_catalog())
        self.assertTrue(auth_ref._data['token']['catalog'])

        self.assertEqual(token_id, auth_ref.auth_token)
        self.assertEqual(token.user_name, auth_ref.username)
        self.assertEqual(token.user_id, auth_ref.user_id)

        self.assertEqual(token.role_ids, auth_ref.role_ids)
        self.assertEqual(token.role_names, auth_ref.role_names)

        self.assertEqual(token.domain_name, auth_ref.domain_name)
        self.assertEqual(token.domain_id, auth_ref.domain_id)

        self.assertEqual(token.user_domain_id, auth_ref.user_domain_id)
        self.assertEqual(token.user_domain_name, auth_ref.user_domain_name)

        self.assertIsNone(auth_ref.project_name)
        self.assertIsNone(auth_ref.project_id)

        self.assertIsNone(auth_ref.project_domain_id)
        self.assertIsNone(auth_ref.project_domain_name)

        self.assertIsNone(auth_ref.domain_name)
        self.assertIsNone(auth_ref.domain_id)

        self.assertEqual(token.system, auth_ref.system)

        self.assertTrue(auth_ref.system_scoped)
        self.assertFalse(auth_ref.domain_scoped)
        self.assertFalse(auth_ref.project_scoped)

        self.assertEqual(token.audit_id, auth_ref.audit_id)
        self.assertEqual(token.audit_chain_id, auth_ref.audit_chain_id)

    def test_building_domain_scoped_accessinfo(self):
        token = fixture.V3Token()
        token.set_domain_scope()

        s = token.add_service(type='identity')
        s.add_standard_endpoints(public='http://url')

        token_id = uuid.uuid4().hex

        auth_ref = access.create(body=token, auth_token=token_id)

        self.assertTrue(auth_ref)
        self.assertIn('methods', auth_ref._data['token'])
        self.assertIn('catalog', auth_ref._data['token'])
        self.assertTrue(auth_ref.has_service_catalog())
        self.assertTrue(auth_ref._data['token']['catalog'])

        self.assertEqual(token_id, auth_ref.auth_token)
        self.assertEqual(token.user_name, auth_ref.username)
        self.assertEqual(token.user_id, auth_ref.user_id)

        self.assertEqual(token.role_ids, auth_ref.role_ids)
        self.assertEqual(token.role_names, auth_ref.role_names)

        self.assertEqual(token.domain_name, auth_ref.domain_name)
        self.assertEqual(token.domain_id, auth_ref.domain_id)

        self.assertIsNone(auth_ref.project_name)
        self.assertIsNone(auth_ref.project_id)

        self.assertEqual(token.user_domain_id, auth_ref.user_domain_id)
        self.assertEqual(token.user_domain_name, auth_ref.user_domain_name)

        self.assertIsNone(auth_ref.project_domain_id)
        self.assertIsNone(auth_ref.project_domain_name)

        self.assertTrue(auth_ref.domain_scoped)
        self.assertFalse(auth_ref.project_scoped)
        self.assertIsNone(auth_ref.project_is_domain)

        self.assertEqual(token.audit_id, auth_ref.audit_id)
        self.assertEqual(token.audit_chain_id, auth_ref.audit_chain_id)

    def test_building_project_scoped_accessinfo(self):
        token = fixture.V3Token()
        token.set_project_scope()

        s = token.add_service(type='identity')
        s.add_standard_endpoints(public='http://url')

        token_id = uuid.uuid4().hex

        auth_ref = access.create(body=token, auth_token=token_id)

        self.assertIn('methods', auth_ref._data['token'])
        self.assertIn('catalog', auth_ref._data['token'])
        self.assertTrue(auth_ref.has_service_catalog())
        self.assertTrue(auth_ref._data['token']['catalog'])

        self.assertEqual(token_id, auth_ref.auth_token)
        self.assertEqual(token.user_name, auth_ref.username)
        self.assertEqual(token.user_id, auth_ref.user_id)

        self.assertEqual(token.role_ids, auth_ref.role_ids)
        self.assertEqual(token.role_names, auth_ref.role_names)

        self.assertIsNone(auth_ref.domain_name)
        self.assertIsNone(auth_ref.domain_id)

        self.assertEqual(token.project_name, auth_ref.project_name)
        self.assertEqual(token.project_id, auth_ref.project_id)

        self.assertEqual(auth_ref.tenant_name, auth_ref.project_name)
        self.assertEqual(auth_ref.tenant_id, auth_ref.project_id)

        self.assertEqual(token.project_domain_id, auth_ref.project_domain_id)
        self.assertEqual(token.project_domain_name,
                         auth_ref.project_domain_name)

        self.assertEqual(token.user_domain_id, auth_ref.user_domain_id)
        self.assertEqual(token.user_domain_name, auth_ref.user_domain_name)

        self.assertFalse(auth_ref.domain_scoped)
        self.assertTrue(auth_ref.project_scoped)
        self.assertIsNone(auth_ref.project_is_domain)

        self.assertEqual(token.audit_id, auth_ref.audit_id)
        self.assertEqual(token.audit_chain_id, auth_ref.audit_chain_id)

    def test_building_project_as_domain_scoped_accessinfo(self):
        token = fixture.V3Token()
        token.set_project_scope(is_domain=True)

        service = token.add_service(type='identity')
        service.add_standard_endpoints(public='http://url')

        token_id = uuid.uuid4().hex

        auth_ref = access.create(body=token, auth_token=token_id)

        self.assertIn('methods', auth_ref._data['token'])
        self.assertIn('catalog', auth_ref._data['token'])
        self.assertTrue(auth_ref.has_service_catalog())
        self.assertTrue(auth_ref._data['token']['catalog'])

        self.assertEqual(token_id, auth_ref.auth_token)
        self.assertEqual(token.user_name, auth_ref.username)
        self.assertEqual(token.user_id, auth_ref.user_id)

        self.assertEqual(token.role_ids, auth_ref.role_ids)
        self.assertEqual(token.role_names, auth_ref.role_names)

        self.assertIsNone(auth_ref.domain_name)
        self.assertIsNone(auth_ref.domain_id)

        self.assertEqual(token.project_name, auth_ref.project_name)
        self.assertEqual(token.project_id, auth_ref.project_id)

        self.assertEqual(auth_ref.tenant_name, auth_ref.project_name)
        self.assertEqual(auth_ref.tenant_id, auth_ref.project_id)

        self.assertEqual(token.project_domain_id, auth_ref.project_domain_id)
        self.assertEqual(token.project_domain_name,
                         auth_ref.project_domain_name)

        self.assertEqual(token.user_domain_id, auth_ref.user_domain_id)
        self.assertEqual(token.user_domain_name, auth_ref.user_domain_name)

        self.assertFalse(auth_ref.domain_scoped)
        self.assertTrue(auth_ref.project_scoped)
        self.assertTrue(auth_ref.project_is_domain)

        self.assertEqual(token.audit_id, auth_ref.audit_id)
        self.assertEqual(token.audit_chain_id, auth_ref.audit_chain_id)

    def test_oauth_access(self):
        consumer_id = uuid.uuid4().hex
        access_token_id = uuid.uuid4().hex

        token = fixture.V3Token()
        token.set_project_scope()
        token.set_oauth(access_token_id=access_token_id,
                        consumer_id=consumer_id)

        auth_ref = access.create(body=token)

        self.assertEqual(consumer_id, auth_ref.oauth_consumer_id)
        self.assertEqual(access_token_id, auth_ref.oauth_access_token_id)

        self.assertEqual(consumer_id,
                         auth_ref._data['token']['OS-OAUTH1']['consumer_id'])
        self.assertEqual(
            access_token_id,
            auth_ref._data['token']['OS-OAUTH1']['access_token_id'])

    def test_federated_property_standard_token(self):
        """Check if is_federated property returns expected value."""
        token = fixture.V3Token()
        token.set_project_scope()
        auth_ref = access.create(body=token)
        self.assertFalse(auth_ref.is_federated)

    def test_binding(self):
        token = fixture.V3Token()
        principal = uuid.uuid4().hex
        token.set_bind('kerberos', principal)

        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV3)

        self.assertEqual({'kerberos': principal}, auth_ref.bind)

    def test_is_admin_project_unset(self):
        token = fixture.V3Token()
        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV3)
        self.assertIs(True, auth_ref.is_admin_project)

    def test_is_admin_project_true(self):
        token = fixture.V3Token(is_admin_project=True)
        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV3)
        self.assertIs(True, auth_ref.is_admin_project)

    def test_is_admin_project_false(self):
        token = fixture.V3Token(is_admin_project=False)
        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV3)
        self.assertIs(False, auth_ref.is_admin_project)
