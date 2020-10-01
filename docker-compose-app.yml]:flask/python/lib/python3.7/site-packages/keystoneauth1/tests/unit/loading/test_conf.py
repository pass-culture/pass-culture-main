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

from unittest import mock
import uuid

from oslo_config import cfg
from oslo_config import fixture as config
import stevedore

from keystoneauth1 import exceptions
from keystoneauth1 import loading
from keystoneauth1.loading._plugins.identity import v2
from keystoneauth1.loading._plugins.identity import v3
from keystoneauth1.tests.unit.loading import utils


class ConfTests(utils.TestCase):

    def setUp(self):
        super(ConfTests, self).setUp()
        self.conf_fixture = self.useFixture(config.Config())

        # NOTE(jamielennox): we register the basic config options first because
        # we need them in place before we can stub them. We will need to run
        # the register again after we stub the auth section and auth plugin so
        # it can load the plugin specific options.
        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)

    def test_loading_v2(self):
        section = uuid.uuid4().hex
        auth_url = uuid.uuid4().hex
        username = uuid.uuid4().hex
        password = uuid.uuid4().hex
        trust_id = uuid.uuid4().hex
        tenant_id = uuid.uuid4().hex

        self.conf_fixture.config(auth_section=section, group=self.GROUP)
        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)

        opts = loading.get_auth_plugin_conf_options(v2.Password())
        self.conf_fixture.register_opts(opts, group=section)

        self.conf_fixture.config(auth_type=self.V2PASS,
                                 auth_url=auth_url,
                                 username=username,
                                 password=password,
                                 trust_id=trust_id,
                                 tenant_id=tenant_id,
                                 group=section)

        a = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                self.GROUP)

        self.assertEqual(auth_url, a.auth_url)
        self.assertEqual(username, a.username)
        self.assertEqual(password, a.password)
        self.assertEqual(trust_id, a.trust_id)
        self.assertEqual(tenant_id, a.tenant_id)

    def test_loading_v3(self):
        section = uuid.uuid4().hex
        auth_url = uuid.uuid4().hex,
        token = uuid.uuid4().hex
        trust_id = uuid.uuid4().hex
        project_id = uuid.uuid4().hex
        project_domain_name = uuid.uuid4().hex

        self.conf_fixture.config(auth_section=section, group=self.GROUP)
        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)

        opts = loading.get_auth_plugin_conf_options(v3.Token())
        self.conf_fixture.register_opts(opts, group=section)

        self.conf_fixture.config(auth_type=self.V3TOKEN,
                                 auth_url=auth_url,
                                 token=token,
                                 trust_id=trust_id,
                                 project_id=project_id,
                                 project_domain_name=project_domain_name,
                                 group=section)

        a = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                self.GROUP)

        self.assertEqual(token, a.auth_methods[0].token)
        self.assertEqual(trust_id, a.trust_id)
        self.assertEqual(project_id, a.project_id)
        self.assertEqual(project_domain_name, a.project_domain_name)

    def test_loading_invalid_plugin(self):
        auth_type = uuid.uuid4().hex
        self.conf_fixture.config(auth_type=auth_type,
                                 group=self.GROUP)

        e = self.assertRaises(exceptions.NoMatchingPlugin,
                              loading.load_auth_from_conf_options,
                              self.conf_fixture.conf,
                              self.GROUP)

        self.assertEqual(auth_type, e.name)

    def test_loading_with_no_data(self):
        lo = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                 self.GROUP)
        self.assertIsNone(lo)

    @mock.patch('stevedore.DriverManager')
    def test_other_params(self, m):
        m.return_value = utils.MockManager(utils.MockLoader())
        driver_name = uuid.uuid4().hex

        opts = loading.get_auth_plugin_conf_options(utils.MockLoader())
        self.conf_fixture.register_opts(opts, group=self.GROUP)
        self.conf_fixture.config(auth_type=driver_name,
                                 group=self.GROUP,
                                 **self.TEST_VALS)

        a = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                self.GROUP)
        self.assertTestVals(a)

        m.assert_called_once_with(namespace=loading.PLUGIN_NAMESPACE,
                                  name=driver_name,
                                  invoke_on_load=True)

    @utils.mock_plugin()
    def test_same_section(self, m):
        opts = loading.get_auth_plugin_conf_options(utils.MockLoader())
        self.conf_fixture.register_opts(opts, group=self.GROUP)

        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)
        self.conf_fixture.config(auth_type=uuid.uuid4().hex,
                                 group=self.GROUP,
                                 **self.TEST_VALS)

        a = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                self.GROUP)
        self.assertTestVals(a)

    @utils.mock_plugin()
    def test_diff_section(self, m):
        section = uuid.uuid4().hex

        self.conf_fixture.config(auth_section=section, group=self.GROUP)
        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)

        opts = loading.get_auth_plugin_conf_options(utils.MockLoader())
        self.conf_fixture.register_opts(opts, group=section)
        self.conf_fixture.config(group=section,
                                 auth_type=uuid.uuid4().hex,
                                 **self.TEST_VALS)

        a = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                self.GROUP)
        self.assertTestVals(a)

    def test_plugins_are_all_opts(self):
        manager = stevedore.ExtensionManager(loading.PLUGIN_NAMESPACE,
                                             propagate_map_exceptions=True)

        def inner(driver):
            for p in driver.plugin().get_options():
                self.assertIsInstance(p, loading.Opt)

        manager.map(inner)

    def test_get_common(self):
        opts = loading.get_auth_common_conf_options()
        for opt in opts:
            self.assertIsInstance(opt, cfg.Opt)
        self.assertEqual(2, len(opts))

    def test_get_named(self):
        loaded_opts = loading.get_plugin_options('v2password')
        plugin_opts = v2.Password().get_options()

        loaded_names = set([o.name for o in loaded_opts])
        plugin_names = set([o.name for o in plugin_opts])

        self.assertEqual(plugin_names, loaded_names)

    def test_register_cfg(self):
        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)

    def test_common_conf_options(self):
        opts = loading.get_auth_common_conf_options()

        self.assertEqual(2, len(opts))
        auth_type = [o for o in opts if o.name == 'auth_type'][0]
        self.assertEqual(1, len(auth_type.deprecated_opts))
        self.assertIsInstance(auth_type.deprecated_opts[0], cfg.DeprecatedOpt)
