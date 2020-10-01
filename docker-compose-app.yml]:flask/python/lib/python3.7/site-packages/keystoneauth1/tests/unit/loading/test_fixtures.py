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

from oslo_config import fixture as config

from keystoneauth1 import fixture
from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils


class FixturesTests(utils.TestCase):

    GROUP = uuid.uuid4().hex
    AUTH_TYPE = uuid.uuid4().hex

    def setUp(self):
        super(FixturesTests, self).setUp()
        self.conf_fixture = self.useFixture(config.Config())

        # conf loading will still try to read the auth_type from the config
        # object and pass that to the get_plugin_loader method. This value will
        # typically be ignored and the fake plugin returned regardless of name
        # but it could be a useful differentiator and it also ensures that the
        # application has called register_auth_conf_options before simply
        # returning a fake plugin.
        loading.register_auth_conf_options(self.conf_fixture.conf,
                                           group=self.GROUP)

        self.conf_fixture.config(auth_type=self.AUTH_TYPE, group=self.GROUP)

    def useLoadingFixture(self, **kwargs):
        return self.useFixture(fixture.LoadingFixture(**kwargs))

    def test_endpoint_resolve(self):
        endpoint = "http://%(service_type)s/%(version)s/%(interface)s"
        loader = self.useLoadingFixture(endpoint=endpoint)

        endpoint_filter = {'service_type': 'compute',
                           'service_name': 'nova',
                           'version': (2, 1),
                           'interface': 'public'}

        auth = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                   self.GROUP)
        sess = session.Session(auth=auth)

        loader_endpoint = loader.get_endpoint(**endpoint_filter)
        plugin_endpoint = sess.get_endpoint(**endpoint_filter)

        self.assertEqual("http://compute/2.1/public", loader_endpoint)
        self.assertEqual(loader_endpoint, plugin_endpoint)

    def test_conf_loaded(self):
        token = uuid.uuid4().hex
        endpoint_filter = {'service_type': 'compute',
                           'service_name': 'nova',
                           'version': (2, 1)}

        loader = self.useLoadingFixture(token=token)

        url = loader.get_endpoint('/path', **endpoint_filter)

        m = self.requests_mock.get(url)

        auth = loading.load_auth_from_conf_options(self.conf_fixture.conf,
                                                   self.GROUP)
        sess = session.Session(auth=auth)
        self.assertEqual(self.AUTH_TYPE, auth.auth_type)

        sess.get('/path', endpoint_filter=endpoint_filter)

        self.assertTrue(m.called_once)

        self.assertTrue(token, m.last_request.headers['X-Auth-Token'])
        self.assertEqual(loader.project_id, sess.get_project_id())
        self.assertEqual(loader.user_id, sess.get_user_id())
