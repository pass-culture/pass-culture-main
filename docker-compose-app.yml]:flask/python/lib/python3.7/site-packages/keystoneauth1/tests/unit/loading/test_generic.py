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

from keystoneauth1 import fixture
from keystoneauth1 import identity
from keystoneauth1.loading._plugins.identity import generic
from keystoneauth1 import session
from keystoneauth1.tests.unit.loading import utils


class PasswordTests(utils.TestCase):

    def test_options(self):
        opts = [o.name for o in generic.Password().get_options()]

        allowed_opts = ['username',
                        'user-domain-id',
                        'user-domain-name',
                        'user-id',
                        'password',

                        'system-scope',
                        'domain-id',
                        'domain-name',
                        'project-id',
                        'project-name',
                        'project-domain-id',
                        'project-domain-name',
                        'trust-id',
                        'auth-url',
                        'default-domain-id',
                        'default-domain-name',
                        ]

        self.assertEqual(set(allowed_opts), set(opts))
        self.assertEqual(len(allowed_opts), len(opts))

    def test_loads_v3_with_user_domain(self):
        auth_url = 'http://keystone.test:5000'
        disc = fixture.DiscoveryList(href=auth_url)
        sess = session.Session()
        self.requests_mock.get(auth_url, json=disc)

        plugin = generic.Password().load_from_options(
            auth_url=auth_url,
            user_id=uuid.uuid4().hex,
            password=uuid.uuid4().hex,
            project_id=uuid.uuid4().hex,
            user_domain_id=uuid.uuid4().hex)

        inner_plugin = plugin._do_create_plugin(sess)

        self.assertIsInstance(inner_plugin, identity.V3Password)
        self.assertEqual(inner_plugin.auth_url, auth_url + '/v3')


class TokenTests(utils.TestCase):

    def test_options(self):
        opts = [o.name for o in generic.Token().get_options()]

        allowed_opts = ['token',
                        'system-scope',
                        'domain-id',
                        'domain-name',
                        'project-id',
                        'project-name',
                        'project-domain-id',
                        'project-domain-name',
                        'trust-id',
                        'auth-url',
                        'default-domain-id',
                        'default-domain-name',
                        ]

        self.assertEqual(set(allowed_opts), set(opts))
        self.assertEqual(len(allowed_opts), len(opts))
