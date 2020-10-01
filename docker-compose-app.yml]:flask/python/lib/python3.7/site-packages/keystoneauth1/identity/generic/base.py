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

import abc

import six
import six.moves.urllib.parse as urlparse

from keystoneauth1 import _utils as utils
from keystoneauth1 import discover
from keystoneauth1 import exceptions
from keystoneauth1.identity import base


LOG = utils.get_logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseGenericPlugin(base.BaseIdentityPlugin):
    """An identity plugin that is not version dependent.

    Internally we will construct a version dependent plugin with the resolved
    URL and then proxy all calls from the base plugin to the versioned one.
    """

    def __init__(self, auth_url,
                 tenant_id=None,
                 tenant_name=None,
                 project_id=None,
                 project_name=None,
                 project_domain_id=None,
                 project_domain_name=None,
                 domain_id=None,
                 domain_name=None,
                 system_scope=None,
                 trust_id=None,
                 default_domain_id=None,
                 default_domain_name=None,
                 reauthenticate=True):
        super(BaseGenericPlugin, self).__init__(auth_url=auth_url,
                                                reauthenticate=reauthenticate)

        self._project_id = project_id or tenant_id
        self._project_name = project_name or tenant_name
        self._project_domain_id = project_domain_id
        self._project_domain_name = project_domain_name
        self._domain_id = domain_id
        self._domain_name = domain_name
        self._system_scope = system_scope
        self._trust_id = trust_id
        self._default_domain_id = default_domain_id
        self._default_domain_name = default_domain_name

        self._plugin = None

    @abc.abstractmethod
    def create_plugin(self, session, version, url, raw_status=None):
        """Create a plugin from the given parameters.

        This function will be called multiple times with the version and url
        of a potential endpoint. If a plugin can be constructed that fits the
        params then it should return it. If not return None and then another
        call will be made with other available URLs.

        :param session: A session object.
        :type session: keystoneauth1.session.Session
        :param tuple version: A tuple of the API version at the URL.
        :param str url: The base URL for this version.
        :param str raw_status: The status that was in the discovery field.

        :returns: A plugin that can match the parameters or None if nothing.
        """
        return None

    @property
    def _has_domain_scope(self):
        """Are there domain parameters.

        Domain parameters are v3 only so returns if any are set.

        :returns: True if a domain parameter is set, false otherwise.
        """
        return any([self._domain_id, self._domain_name,
                    self._project_domain_id, self._project_domain_name])

    @property
    def _v2_params(self):
        """Return the parameters that are common to v2 plugins."""
        return {'trust_id': self._trust_id,
                'tenant_id': self._project_id,
                'tenant_name': self._project_name,
                'reauthenticate': self.reauthenticate}

    @property
    def _v3_params(self):
        """Return the parameters that are common to v3 plugins."""
        return {'trust_id': self._trust_id,
                'system_scope': self._system_scope,
                'project_id': self._project_id,
                'project_name': self._project_name,
                'project_domain_id': self.project_domain_id,
                'project_domain_name': self.project_domain_name,
                'domain_id': self._domain_id,
                'domain_name': self._domain_name,
                'reauthenticate': self.reauthenticate}

    @property
    def project_domain_id(self):
        return self._project_domain_id or self._default_domain_id

    @project_domain_id.setter
    def project_domain_id(self, value):
        self._project_domain_id = value

    @property
    def project_domain_name(self):
        return self._project_domain_name or self._default_domain_name

    @project_domain_name.setter
    def project_domain_name(self, value):
        self._project_domain_name = value

    def _do_create_plugin(self, session):
        plugin = None

        try:
            disc = self.get_discovery(session,
                                      self.auth_url,
                                      authenticated=False)
        except (exceptions.DiscoveryFailure,
                exceptions.HttpError,
                exceptions.SSLError,
                exceptions.ConnectionError) as e:
            LOG.warning('Failed to discover available identity versions when '
                        'contacting %s. Attempting to parse version from URL.',
                        self.auth_url)

            url_parts = urlparse.urlparse(self.auth_url)
            path = url_parts.path.lower()

            if path.startswith('/v2.0'):
                if self._has_domain_scope:
                    raise exceptions.DiscoveryFailure(
                        'Cannot use v2 authentication with domain scope')
                plugin = self.create_plugin(session, (2, 0), self.auth_url)
            elif path.startswith('/v3'):
                plugin = self.create_plugin(session, (3, 0), self.auth_url)
            else:
                raise exceptions.DiscoveryFailure(
                    'Could not find versioned identity endpoints when '
                    'attempting to authenticate. Please check that your '
                    'auth_url is correct. %s' % e)

        else:
            # NOTE(jamielennox): version_data is always in oldest to newest
            # order. This is fine normally because we explicitly skip v2 below
            # if there is domain data present. With default_domain params
            # though we want a v3 plugin if available and fall back to v2 so we
            # have to process in reverse order.  FIXME(jamielennox): if we ever
            # go for another version we should reverse this logic as we always
            # want to favour the newest available version.
            reverse = self._default_domain_id or self._default_domain_name
            disc_data = disc.version_data(reverse=bool(reverse))

            v2_with_domain_scope = False
            for data in disc_data:
                version = data['version']

                if (discover.version_match((2,), version) and
                        self._has_domain_scope):
                    # NOTE(jamielennox): if there are domain parameters there
                    # is no point even trying against v2 APIs.
                    v2_with_domain_scope = True
                    continue

                plugin = self.create_plugin(session,
                                            version,
                                            data['url'],
                                            raw_status=data['raw_status'])

                if plugin:
                    break
            if not plugin and v2_with_domain_scope:
                raise exceptions.DiscoveryFailure(
                    'Cannot use v2 authentication with domain scope')

        if plugin:
            return plugin

        # so there were no URLs that i could use for auth of any version.
        raise exceptions.DiscoveryFailure(
            'Could not find versioned identity endpoints when attempting '
            'to authenticate. Please check that your auth_url is correct.')

    def get_auth_ref(self, session, **kwargs):
        if not self._plugin:
            self._plugin = self._do_create_plugin(session)

        return self._plugin.get_auth_ref(session, **kwargs)

    def get_cache_id_elements(self, _implemented=False):
        # NOTE(jamielennox): implemented here is just a way to make sure that
        # something overrides this method. We don't want the base
        # implementation to respond with a dict without the subclass modifying
        # it to add their own data in case the subclass doesn't support caching
        if not _implemented:
            raise NotImplementedError()

        return {'auth_url': self.auth_url,
                'project_id': self._project_id,
                'project_name': self._project_name,
                'project_domain_id': self.project_domain_id,
                'project_domain_name': self.project_domain_name,
                'domain_id': self._domain_id,
                'domain_name': self._domain_name,
                'trust_id': self._trust_id}
