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

import fixtures

from keystoneauth1 import discover
from keystoneauth1 import loading
from keystoneauth1 import plugin

__all__ = (
    'LoadingFixture',
    'TestPlugin',
)


DEFAULT_TEST_ENDPOINT = 'https://openstack.example.com/%(service_type)s'


def _format_endpoint(endpoint, **kwargs):
    # can't format AUTH_INTERFACE object so replace with string
    if kwargs.get('service_type') is plugin.AUTH_INTERFACE:
        kwargs['service_type'] = 'identity'

    version = kwargs.get('version')
    if version:
        discover.normalize_version_number(version)
        kwargs['version'] = ".".join(str(v) for v in version)

    return endpoint % kwargs  # pass kwargs ok?


class TestPlugin(plugin.BaseAuthPlugin):
    """A simple plugin that returns what you gave it for testing.

    When testing services that use authentication plugins you often want to
    stub out the authentication calls and focus on the important part of your
    service. This plugin acts like a real keystoneauth plugin and returns known
    standard values without having to stub out real keystone responses.

    Note that this plugin is a BaseAuthPlugin and not a BaseIdentityPlugin.
    This means it implements the basic plugin interface that services should be
    using but does not implement get_auth_ref. get_auth_ref should not be
    relied upon by services because a user could always configure the service
    to use a non-keystone auth.

    :param str token: The token to include in authenticated requests.
    :param str endpoint: The endpoint to respond to service lookups with.
    :param str user_id: The user_id to report for the authenticated user.
    :param str project_id: The project_id to report for the authenticated user.
    """

    auth_type = 'test_plugin'

    def __init__(self,
                 token=None,
                 endpoint=None,
                 user_id=None,
                 project_id=None):
        super(TestPlugin, self).__init__()

        self.token = token or uuid.uuid4().hex
        self.endpoint = endpoint or DEFAULT_TEST_ENDPOINT
        self.user_id = user_id or uuid.uuid4().hex
        self.project_id = project_id or uuid.uuid4().hex

    def get_endpoint(self, session, **kwargs):
        return _format_endpoint(self.endpoint, **kwargs)

    def get_token(self, session, **kwargs):
        return self.token

    def get_user_id(self, session, **kwargs):
        return self.user_id

    def get_project_id(self, session, **kwargs):
        return self.project_id

    def invalidate(self):
        self.token = uuid.uuid4().hex
        return True

    # NOTE(jamielennox): You'll notice there's no get_access/get_auth_ref
    # function here. These functions are only part of identity plugins, which
    # whilst the most common are not the only way you can authenticate. You're
    # application should really only rely on the presence of the above
    # functions, everything else is on a best effort basis.


class _TestPluginLoader(loading.BaseLoader):

    def __init__(self, plugin):
        super(_TestPluginLoader, self).__init__()
        self._plugin = plugin

    def create_plugin(self, **kwargs):
        return self._plugin

    def get_options(self):
        return []


class LoadingFixture(fixtures.Fixture):
    """A fixture that will stub out all plugin loading calls.

    When using keystoneauth plugins loaded from config, CLI or elsewhere it is
    often difficult to handle the plugin parts in tests because we don't have a
    reasonable default.

    This fixture will create a :py:class:`TestPlugin` that will be
    returned for all calls to plugin loading so you can simply bypass the
    authentication steps and return something well known.

    :param str token: The token to include in authenticated requests.
    :param str endpoint: The endpoint to respond to service lookups with.
    :param str user_id: The user_id to report for the authenticated user.
    :param str project_id: The project_id to report for the authenticated user.
    """

    MOCK_POINT = 'keystoneauth1.loading.base.get_plugin_loader'

    def __init__(self,
                 token=None,
                 endpoint=None,
                 user_id=None,
                 project_id=None):
        super(LoadingFixture, self).__init__()

        # these are created and saved here so that a test could use them
        self.token = token or uuid.uuid4().hex
        self.endpoint = endpoint or DEFAULT_TEST_ENDPOINT
        self.user_id = user_id or uuid.uuid4().hex
        self.project_id = project_id or uuid.uuid4().hex

    def setUp(self):
        super(LoadingFixture, self).setUp()

        self.useFixture(fixtures.MonkeyPatch(self.MOCK_POINT,
                                             self.get_plugin_loader))

    def create_plugin(self):
        return TestPlugin(token=self.token,
                          endpoint=self.endpoint,
                          user_id=self.user_id,
                          project_id=self.project_id)

    def get_plugin_loader(self, auth_type):
        plugin = self.create_plugin()
        plugin.auth_type = auth_type
        return _TestPluginLoader(plugin)

    def get_endpoint(self, path=None, **kwargs):
        """Utility function to get the endpoint the plugin would return.

        This function is provided as a convenience so you can do comparisons in
        your tests. Overriding it will not affect the endpoint returned by the
        plugin.

        :param str path: The path to append to the plugin endpoint.
        """
        endpoint = _format_endpoint(self.endpoint, **kwargs)

        if path:
            endpoint = "%s/%s" % (endpoint.rstrip('/'), path.lstrip('/'))

        return endpoint
