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

from keystoneauth1 import _utils as utils
from keystoneauth1 import plugin

LOG = utils.get_logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class TokenlessAuth(plugin.BaseAuthPlugin):
    """A plugin for authenticating with Tokenless Auth.

    This is for Tokenless Authentication. Scoped information
    like domain name and project ID will be passed in the headers and
    token validation request will be authenticated based on
    the provided HTTPS certificate along with the scope information.
    """

    def __init__(self, auth_url,
                 domain_id=None,
                 domain_name=None,
                 project_id=None,
                 project_name=None,
                 project_domain_id=None,
                 project_domain_name=None):
        """A init method for TokenlessAuth.

        :param string auth_url: Identity service endpoint for authentication.
                                The URL must include a version or any request
                                will result in a 404 NotFound error.
        :param string domain_id: Domain ID for domain scoping.
        :param string domain_name: Domain name for domain scoping.
        :param string project_id: Project ID for project scoping.
        :param string project_name: Project name for project scoping.
        :param string project_domain_id: Project's domain ID for project.
        :param string project_domain_name: Project's domain name for project.
        """
        self.auth_url = auth_url
        self.domain_id = domain_id
        self.domain_name = domain_name
        self.project_id = project_id
        self.project_name = project_name
        self.project_domain_id = project_domain_id
        self.project_domain_name = project_domain_name

    def get_headers(self, session, **kwargs):
        """Fetch authentication headers for message.

        This is to override the default get_headers method to provide
        tokenless auth scope headers if token is not provided in the
        session.

        :param session: The session object that the auth_plugin belongs to.
        :type session: keystoneauth1.session.Session

        :returns: Headers that are set to authenticate a message or None for
                  failure. Note that when checking this value that the empty
                  dict is a valid, non-failure response.
        :rtype: dict
        """
        scope_headers = {}
        if self.project_id:
            scope_headers['X-Project-Id'] = self.project_id
        elif self.project_name:
            scope_headers['X-Project-Name'] = self.project_name
            if self.project_domain_id:
                scope_headers['X-Project-Domain-Id'] = (
                    self.project_domain_id)
            elif self.project_domain_name:
                scope_headers['X-Project-Domain-Name'] = (
                    self.project_domain_name)
            else:
                LOG.warning(
                    'Neither Project Domain ID nor Project Domain Name was '
                    'provided.')
                return None
        elif self.domain_id:
            scope_headers['X-Domain-Id'] = self.domain_id
        elif self.domain_name:
            scope_headers['X-Domain-Name'] = self.domain_name
        else:
            LOG.warning(
                'Neither Project nor Domain scope was provided.')
            return None
        return scope_headers

    def get_endpoint(self, session, service_type=None, **kwargs):
        """Return a valid endpoint for a service.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param string service_type: The type of service to lookup the endpoint
                                    for. This plugin will return None (failure)
                                    if service_type is not provided.
        :return: A valid endpoint URL or None if not available.
        :rtype: string or None
        """
        if (service_type is plugin.AUTH_INTERFACE or
                service_type.lower() == 'identity'):
            return self.auth_url

        return None
