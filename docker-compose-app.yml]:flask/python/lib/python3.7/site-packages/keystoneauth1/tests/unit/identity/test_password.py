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

from keystoneauth1.identity.generic import password
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1.identity.v3 import password as v3_password
from keystoneauth1.tests.unit.identity import utils


class PasswordTests(utils.GenericPluginTestCase):

    PLUGIN_CLASS = password.Password
    V2_PLUGIN_CLASS = v2.Password
    V3_PLUGIN_CLASS = v3.Password

    def new_plugin(self, **kwargs):
        kwargs.setdefault('username', uuid.uuid4().hex)
        kwargs.setdefault('password', uuid.uuid4().hex)
        return super(PasswordTests, self).new_plugin(**kwargs)

    def test_with_user_domain_params(self):
        self.stub_discovery()

        self.assertCreateV3(domain_id=uuid.uuid4().hex,
                            user_domain_id=uuid.uuid4().hex)

    def test_v3_user_params_v2_url(self):
        self.stub_discovery(v3=False)
        self.assertDiscoveryFailure(user_domain_id=uuid.uuid4().hex)

    def test_v3_domain_params_v2_url(self):
        self.stub_discovery(v3=False)
        self.assertDiscoveryFailure(domain_id=uuid.uuid4().hex)

    def test_v3_disocovery_failure_v2_url(self):
        auth_url = self.TEST_URL + 'v2.0'
        self.stub_url('GET', json={}, base_url='/v2.0', status_code=500)
        self.assertDiscoveryFailure(domain_id=uuid.uuid4().hex,
                                    auth_url=auth_url)

    def test_symbols(self):
        self.assertIs(v3.Password, v3_password.Password)
        self.assertIs(v3.PasswordMethod, v3_password.PasswordMethod)

    def test_default_domain_id_with_v3(self):
        default_domain_id = uuid.uuid4().hex

        p = super(PasswordTests, self).test_default_domain_id_with_v3(
            default_domain_id=default_domain_id)

        self.assertEqual(default_domain_id,
                         p._plugin.auth_methods[0].user_domain_id)

    def test_default_domain_name_with_v3(self):
        default_domain_name = uuid.uuid4().hex

        p = super(PasswordTests, self).test_default_domain_name_with_v3(
            default_domain_name=default_domain_name)

        self.assertEqual(default_domain_name,
                         p._plugin.auth_methods[0].user_domain_name)

    def test_password_cache_id(self):
        username = uuid.uuid4().hex
        the_password = uuid.uuid4().hex
        project_name = uuid.uuid4().hex
        default_domain_id = uuid.uuid4().hex

        a = password.Password(self.TEST_URL,
                              username=username,
                              password=the_password,
                              project_name=project_name,
                              default_domain_id=default_domain_id)

        b = password.Password(self.TEST_URL,
                              username=username,
                              password=the_password,
                              project_name=project_name,
                              default_domain_id=default_domain_id)

        a_id = a.get_cache_id()
        b_id = b.get_cache_id()

        self.assertEqual(a_id, b_id)

        c = password.Password(self.TEST_URL,
                              username=username,
                              password=uuid.uuid4().hex,  # different
                              project_name=project_name,
                              default_domain_id=default_domain_id)

        c_id = c.get_cache_id()

        self.assertNotEqual(a_id, c_id)
