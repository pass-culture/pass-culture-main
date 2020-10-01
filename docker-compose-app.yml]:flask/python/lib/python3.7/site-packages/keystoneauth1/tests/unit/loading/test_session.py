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

import argparse
import uuid

from oslo_config import cfg
from oslo_config import fixture as config
from testtools import matchers

from keystoneauth1 import loading
from keystoneauth1.tests.unit.loading import utils


class ConfLoadingTests(utils.TestCase):

    GROUP = 'sessiongroup'

    def setUp(self):
        super(ConfLoadingTests, self).setUp()

        self.conf_fixture = self.useFixture(config.Config())
        loading.register_session_conf_options(self.conf_fixture.conf,
                                              self.GROUP)

    def config(self, **kwargs):
        kwargs['group'] = self.GROUP
        self.conf_fixture.config(**kwargs)

    def get_session(self, **kwargs):
        return loading.load_session_from_conf_options(self.conf_fixture.conf,
                                                      self.GROUP,
                                                      **kwargs)

    def test_insecure_timeout(self):
        self.config(insecure=True, timeout=5)
        s = self.get_session()

        self.assertFalse(s.verify)
        self.assertEqual(5, s.timeout)

    def test_client_certs(self):
        cert = '/path/to/certfile'
        key = '/path/to/keyfile'

        self.config(certfile=cert, keyfile=key)
        s = self.get_session()

        self.assertTrue(s.verify)
        self.assertEqual((cert, key), s.cert)

    def test_cacert(self):
        cafile = '/path/to/cacert'

        self.config(cafile=cafile)
        s = self.get_session()

        self.assertEqual(cafile, s.verify)

    def test_deprecated(self):
        def new_deprecated():
            return cfg.DeprecatedOpt(uuid.uuid4().hex, group=uuid.uuid4().hex)

        opt_names = [
            'cafile',
            'certfile',
            'keyfile',
            'insecure',
            'timeout',
            'collect-timing',
            'split-loggers',
        ]
        depr = dict([(n, [new_deprecated()]) for n in opt_names])
        opts = loading.get_session_conf_options(deprecated_opts=depr)

        self.assertThat(opt_names, matchers.HasLength(len(opts)))
        for opt in opts:
            self.assertIn(depr[opt.name][0], opt.deprecated_opts)


class CliLoadingTests(utils.TestCase):

    def setUp(self):
        super(CliLoadingTests, self).setUp()

        self.parser = argparse.ArgumentParser()
        loading.register_session_argparse_arguments(self.parser)

    def get_session(self, val, **kwargs):
        args = self.parser.parse_args(val.split())
        return loading.load_session_from_argparse_arguments(args, **kwargs)

    def test_insecure_timeout(self):
        s = self.get_session('--insecure --timeout 5.5')

        self.assertFalse(s.verify)
        self.assertEqual(5.5, s.timeout)

    def test_client_certs(self):
        cert = '/path/to/certfile'
        key = '/path/to/keyfile'

        s = self.get_session('--os-cert %s --os-key %s' % (cert, key))

        self.assertTrue(s.verify)
        self.assertEqual((cert, key), s.cert)

    def test_cacert(self):
        cacert = '/path/to/cacert'

        s = self.get_session('--os-cacert %s' % cacert)

        self.assertEqual(cacert, s.verify)
