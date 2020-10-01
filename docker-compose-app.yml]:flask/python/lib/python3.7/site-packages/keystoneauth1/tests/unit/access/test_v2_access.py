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


class AccessV2Test(utils.TestCase):

    def test_building_unscoped_accessinfo(self):
        token = fixture.V2Token(expires='2012-10-03T16:58:01Z')

        auth_ref = access.create(body=token)

        self.assertIsInstance(auth_ref, access.AccessInfoV2)
        self.assertFalse(auth_ref.has_service_catalog())

        self.assertEqual(auth_ref.auth_token, token.token_id)
        self.assertEqual(auth_ref.username, token.user_name)
        self.assertEqual(auth_ref.user_id, token.user_id)

        self.assertEqual(auth_ref.role_ids, [])
        self.assertEqual(auth_ref.role_names, [])

        self.assertIsNone(auth_ref.tenant_name)
        self.assertIsNone(auth_ref.tenant_id)

        self.assertFalse(auth_ref.domain_scoped)
        self.assertFalse(auth_ref.project_scoped)
        self.assertFalse(auth_ref.trust_scoped)

        self.assertIsNone(auth_ref.project_domain_id)
        self.assertIsNone(auth_ref.project_domain_name)
        self.assertIsNone(auth_ref.user_domain_id)
        self.assertIsNone(auth_ref.user_domain_name)

        self.assertEqual(auth_ref.expires, token.expires)
        self.assertEqual(auth_ref.issued, token.issued)

        self.assertEqual(token.audit_id, auth_ref.audit_id)
        self.assertIsNone(auth_ref.audit_chain_id)
        self.assertIsNone(token.audit_chain_id)
        self.assertIsNone(auth_ref.bind)

    def test_will_expire_soon(self):
        token = fixture.V2Token()
        expires = timeutils.utcnow() + datetime.timedelta(minutes=5)
        token.expires = expires
        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)
        self.assertFalse(auth_ref.will_expire_soon(stale_duration=120))
        self.assertTrue(auth_ref.will_expire_soon(stale_duration=300))
        self.assertFalse(auth_ref.will_expire_soon())

    def test_building_scoped_accessinfo(self):
        token = fixture.V2Token()
        token.set_scope()
        s = token.add_service('identity')
        s.add_endpoint('http://url')

        role_data = token.add_role()

        auth_ref = access.create(body=token)

        self.assertIsInstance(auth_ref, access.AccessInfoV2)
        self.assertTrue(auth_ref.has_service_catalog())

        self.assertEqual(auth_ref.auth_token, token.token_id)
        self.assertEqual(auth_ref.username, token.user_name)
        self.assertEqual(auth_ref.user_id, token.user_id)

        self.assertEqual(auth_ref.role_ids, [role_data['id']])
        self.assertEqual(auth_ref.role_names, [role_data['name']])

        self.assertEqual(auth_ref.tenant_name, token.tenant_name)
        self.assertEqual(auth_ref.tenant_id, token.tenant_id)

        self.assertEqual(auth_ref.tenant_name, auth_ref.project_name)
        self.assertEqual(auth_ref.tenant_id, auth_ref.project_id)

        self.assertIsNone(auth_ref.project_domain_id, 'default')
        self.assertIsNone(auth_ref.project_domain_name, 'Default')
        self.assertIsNone(auth_ref.user_domain_id, 'default')
        self.assertIsNone(auth_ref.user_domain_name, 'Default')

        self.assertTrue(auth_ref.project_scoped)
        self.assertFalse(auth_ref.domain_scoped)

        self.assertEqual(token.audit_id, auth_ref.audit_id)
        self.assertEqual(token.audit_chain_id, auth_ref.audit_chain_id)

    def test_diablo_token(self):
        diablo_token = {
            'access': {
                'token': {
                    'id': uuid.uuid4().hex,
                    'expires': '2020-01-01T00:00:10.000123Z',
                    'tenantId': 'tenant_id1',
                },
                'user': {
                    'id': 'user_id1',
                    'name': 'user_name1',
                    'roles': [
                        {'name': 'role1'},
                        {'name': 'role2'},
                    ],
                },
            },
        }

        auth_ref = access.create(body=diablo_token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)

        self.assertTrue(auth_ref)
        self.assertEqual(auth_ref.username, 'user_name1')
        self.assertEqual(auth_ref.project_id, 'tenant_id1')
        self.assertEqual(auth_ref.project_name, 'tenant_id1')
        self.assertIsNone(auth_ref.project_domain_id)
        self.assertIsNone(auth_ref.project_domain_name)
        self.assertIsNone(auth_ref.user_domain_id)
        self.assertIsNone(auth_ref.user_domain_name)
        self.assertEqual(auth_ref.role_names, ['role1', 'role2'])

    def test_grizzly_token(self):
        grizzly_token = {
            'access': {
                'token': {
                    'id': uuid.uuid4().hex,
                    'expires': '2020-01-01T00:00:10.000123Z',
                },
                'user': {
                    'id': 'user_id1',
                    'name': 'user_name1',
                    'tenantId': 'tenant_id1',
                    'tenantName': 'tenant_name1',
                    'roles': [
                        {'name': 'role1'},
                        {'name': 'role2'},
                    ],
                },
            },
        }

        auth_ref = access.create(body=grizzly_token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)

        self.assertEqual(auth_ref.project_id, 'tenant_id1')
        self.assertEqual(auth_ref.project_name, 'tenant_name1')
        self.assertIsNone(auth_ref.project_domain_id)
        self.assertIsNone(auth_ref.project_domain_name)
        self.assertIsNone(auth_ref.user_domain_id, 'default')
        self.assertIsNone(auth_ref.user_domain_name, 'Default')
        self.assertEqual(auth_ref.role_names, ['role1', 'role2'])

    def test_v2_roles(self):
        role_id = 'a'
        role_name = 'b'

        token = fixture.V2Token()
        token.set_scope()
        token.add_role(id=role_id, name=role_name)

        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)

        self.assertEqual([role_id], auth_ref.role_ids)
        self.assertEqual([role_id],
                         auth_ref._data['access']['metadata']['roles'])
        self.assertEqual([role_name], auth_ref.role_names)
        self.assertEqual([{'name': role_name}],
                         auth_ref._data['access']['user']['roles'])

    def test_trusts(self):
        user_id = uuid.uuid4().hex
        trust_id = uuid.uuid4().hex

        token = fixture.V2Token(user_id=user_id, trust_id=trust_id)
        token.set_scope()
        token.add_role()

        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)

        self.assertEqual(trust_id, auth_ref.trust_id)
        self.assertEqual(user_id, auth_ref.trustee_user_id)

        self.assertEqual(trust_id, token['access']['trust']['id'])

    def test_binding(self):
        token = fixture.V2Token()
        principal = uuid.uuid4().hex
        token.set_bind('kerberos', principal)

        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)

        self.assertEqual({'kerberos': principal}, auth_ref.bind)

    def test_is_admin_project(self):
        token = fixture.V2Token()
        auth_ref = access.create(body=token)
        self.assertIsInstance(auth_ref, access.AccessInfoV2)
        self.assertIs(True, auth_ref.is_admin_project)
