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

from oslo_config import cfg
from oslo_config import fixture as config

from keystoneauth1 import loading
from keystoneauth1.tests.unit.loading import utils


class ConfLoadingTests(utils.TestCase):

    GROUP = 'adaptergroup'

    def setUp(self):
        super(ConfLoadingTests, self).setUp()

        self.conf_fx = self.useFixture(config.Config())
        loading.register_adapter_conf_options(self.conf_fx.conf, self.GROUP,
                                              include_deprecated=False)

    def test_load(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='internal',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_valid_interfaces_list(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces=['internal', 'public'],
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal', 'public'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_valid_interfaces_comma_list(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='internal,public',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal', 'public'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_load_bad_valid_interfaces_value(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='bad',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_load_version_range(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='internal',
            region_name='region', endpoint_override='endpoint',
            min_version='2.0', max_version='3.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(['internal'], adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertIsNone(adap.version)
        self.assertEqual('2.0', adap.min_version)
        self.assertEqual('3.0', adap.max_version)

    def test_version_mutex_min(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='iface',
            region_name='region', endpoint_override='endpoint',
            version='2.0', min_version='2.0', group=self.GROUP)

        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_version_mutex_max(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='iface',
            region_name='region', endpoint_override='endpoint',
            version='2.0', max_version='3.0', group=self.GROUP)

        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_version_mutex_minmax(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            valid_interfaces='iface',
            region_name='region', endpoint_override='endpoint',
            version='2.0', min_version='2.0', max_version='3.0',
            group=self.GROUP)

        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')

    def test_load_retries(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            connect_retries=3, status_code_retries=5,
            connect_retry_delay=0.5, status_code_retry_delay=2.0,
            group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual(3, adap.connect_retries)
        self.assertEqual(0.5, adap.connect_retry_delay)
        self.assertEqual(5, adap.status_code_retries)
        self.assertEqual(2.0, adap.status_code_retry_delay)

    def test_get_conf_options(self):
        opts = loading.get_adapter_conf_options()
        for opt in opts:
            if opt.name.endswith('-retries'):
                self.assertIsInstance(opt, cfg.IntOpt)
            elif opt.name.endswith('-retry-delay'):
                self.assertIsInstance(opt, cfg.FloatOpt)
            elif opt.name != 'valid-interfaces':
                self.assertIsInstance(opt, cfg.StrOpt)
            else:
                self.assertIsInstance(opt, cfg.ListOpt)
        self.assertEqual({'service-type', 'service-name',
                          'interface', 'valid-interfaces',
                          'region-name', 'endpoint-override', 'version',
                          'min-version', 'max-version', 'connect-retries',
                          'status-code-retries', 'connect-retry-delay',
                          'status-code-retry-delay'},
                         {opt.name for opt in opts})

    def test_get_conf_options_undeprecated(self):
        opts = loading.get_adapter_conf_options(include_deprecated=False)
        for opt in opts:
            if opt.name.endswith('-retries'):
                self.assertIsInstance(opt, cfg.IntOpt)
            elif opt.name.endswith('-retry-delay'):
                self.assertIsInstance(opt, cfg.FloatOpt)
            elif opt.name != 'valid-interfaces':
                self.assertIsInstance(opt, cfg.StrOpt)
            else:
                self.assertIsInstance(opt, cfg.ListOpt)
        self.assertEqual({'service-type', 'service-name', 'valid-interfaces',
                          'region-name', 'endpoint-override', 'version',
                          'min-version', 'max-version', 'connect-retries',
                          'status-code-retries', 'connect-retry-delay',
                          'status-code-retry-delay'},
                         {opt.name for opt in opts})

    def test_deprecated(self):
        """Test external options that are deprecated by Adapter options.

        Not to be confused with ConfLoadingDeprecatedTests, which tests conf
        options in Adapter which are themselves deprecated.
        """
        def new_deprecated():
            return cfg.DeprecatedOpt(uuid.uuid4().hex, group=uuid.uuid4().hex)

        opt_names = ['service-type', 'valid-interfaces', 'endpoint-override']
        depr = dict([(n, [new_deprecated()]) for n in opt_names])
        opts = loading.get_adapter_conf_options(deprecated_opts=depr)

        for opt in opts:
            if opt.name in opt_names:
                self.assertIn(depr[opt.name][0], opt.deprecated_opts)


class ConfLoadingLegacyTests(ConfLoadingTests):
    """Tests with inclusion of deprecated conf options.

    Not to be confused with ConfLoadingTests.test_deprecated, which tests
    external options that are deprecated in favor of Adapter options.
    """

    GROUP = 'adaptergroup'

    def setUp(self):
        super(ConfLoadingLegacyTests, self).setUp()

        self.conf_fx = self.useFixture(config.Config())
        loading.register_adapter_conf_options(self.conf_fx.conf, self.GROUP)

    def test_load_old_interface(self):
        self.conf_fx.config(
            service_type='type', service_name='name',
            interface='internal',
            region_name='region', endpoint_override='endpoint',
            version='2.0', group=self.GROUP)
        adap = loading.load_adapter_from_conf_options(
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
        self.assertEqual('type', adap.service_type)
        self.assertEqual('name', adap.service_name)
        self.assertEqual('internal', adap.interface)
        self.assertEqual('region', adap.region_name)
        self.assertEqual('endpoint', adap.endpoint_override)
        self.assertEqual('session', adap.session)
        self.assertEqual('auth', adap.auth)
        self.assertEqual('2.0', adap.version)
        self.assertIsNone(adap.min_version)
        self.assertIsNone(adap.max_version)

    def test_interface_conflict(self):
        self.conf_fx.config(
            service_type='type', service_name='name', interface='iface',
            valid_interfaces='internal,public',
            region_name='region', endpoint_override='endpoint',
            group=self.GROUP)

        self.assertRaises(
            TypeError,
            loading.load_adapter_from_conf_options,
            self.conf_fx.conf, self.GROUP, session='session', auth='auth')
