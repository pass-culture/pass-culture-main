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

from keystoneauth1 import discover

# NOTE(jamielennox): The AUTH_INTERFACE is a special value that can be
# requested from get_endpoint. If a plugin receives this as the value of
# 'interface' it should return the initial URL that was passed to the plugin.
AUTH_INTERFACE = object()

IDENTITY_AUTH_HEADER_NAME = 'X-Auth-Token'


class BaseAuthPlugin(object):
    """The basic structure of an authentication plugin.

    .. note::
        See :doc:`/authentication-plugins` for a description of plugins
        provided by this library.

    """

    def __init__(self):
        self._discovery_cache = {}

    def get_token(self, session, **kwargs):
        """Obtain a token.

        How the token is obtained is up to the plugin. If it is still valid
        it may be re-used, retrieved from cache or invoke an authentication
        request against a server.

        There are no required kwargs. They are passed directly to the auth
        plugin and they are implementation specific.

        Returning None will indicate that no token was able to be retrieved.

        This function is misplaced as it should only be required for auth
        plugins that use the 'X-Auth-Token' header. However due to the way
        plugins evolved this method is required and often called to trigger an
        authentication request on a new plugin.

        When implementing a new plugin it is advised that you implement this
        method, however if you don't require the 'X-Auth-Token' header override
        the `get_headers` method instead.

        :param session: A session object so the plugin can make HTTP calls.
        :type session: keystoneauth1.session.Session

        :return: A token to use.
        :rtype: string
        """
        return None

    def get_headers(self, session, **kwargs):
        """Fetch authentication headers for message.

        This is a more generalized replacement of the older get_token to allow
        plugins to specify different or additional authentication headers to
        the OpenStack standard 'X-Auth-Token' header.

        How the authentication headers are obtained is up to the plugin. If the
        headers are still valid they may be re-used, retrieved from cache or
        the plugin may invoke an authentication request against a server.

        The default implementation of get_headers calls the `get_token` method
        to enable older style plugins to continue functioning unchanged.
        Subclasses should feel free to completely override this function to
        provide the headers that they want.

        There are no required kwargs. They are passed directly to the auth
        plugin and they are implementation specific.

        Returning None will indicate that no token was able to be retrieved and
        that authorization was a failure. Adding no authentication data can be
        achieved by returning an empty dictionary.

        :param session: The session object that the auth_plugin belongs to.
        :type session: keystoneauth1.session.Session

        :returns: Headers that are set to authenticate a message or None for
                  failure. Note that when checking this value that the empty
                  dict is a valid, non-failure response.
        :rtype: dict
        """
        token = self.get_token(session)

        if not token:
            return None

        return {IDENTITY_AUTH_HEADER_NAME: token}

    def get_endpoint_data(self, session,
                          endpoint_override=None,
                          discover_versions=True,
                          **kwargs):
        """Return a valid endpoint data for a the service.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param str endpoint_override: URL to use for version discovery.
        :param bool discover_versions: Whether to get version metadata from
                                       the version discovery document even
                                       if it major api version info can be
                                       inferred from the url.
                                       (optional, defaults to True)
        :param kwargs: Ignored.

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: Valid EndpointData or None if not available.
        :rtype: `keystoneauth1.discover.EndpointData` or None
        """
        if not endpoint_override:
            return None
        endpoint_data = discover.EndpointData(catalog_url=endpoint_override)

        if endpoint_data.api_version and not discover_versions:
            return endpoint_data

        return endpoint_data.get_versioned_data(
            session, cache=self._discovery_cache,
            discover_versions=discover_versions)

    def get_api_major_version(self, session, endpoint_override=None, **kwargs):
        """Get the major API version from the endpoint.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param str endpoint_override: URL to use for version discovery.
        :param kwargs: Ignored.

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: Valid EndpointData or None if not available.
        :rtype: `keystoneauth1.discover.EndpointData` or None
        """
        endpoint_data = self.get_endpoint_data(
            session, endpoint_override=endpoint_override,
            discover_versions=False, **kwargs)
        if endpoint_data is None:
            return

        if endpoint_data.api_version is None:
            # No version detected from the URL, trying full discovery.
            endpoint_data = self.get_endpoint_data(
                session, endpoint_override=endpoint_override,
                discover_versions=True, **kwargs)

        if endpoint_data and endpoint_data.api_version:
            return endpoint_data.api_version

        return None

    def get_endpoint(self, session, **kwargs):
        """Return an endpoint for the client.

        There are no required keyword arguments to ``get_endpoint`` as a plugin
        implementation should use best effort with the information available to
        determine the endpoint. However there are certain standard options that
        will be generated by the clients and should be used by plugins:

        - ``service_type``: what sort of service is required.
        - ``service_name``: the name of the service in the catalog.
        - ``interface``: what visibility the endpoint should have.
        - ``region_name``: the region the endpoint exists in.

        :param session: The session object that the auth_plugin belongs to.
        :type session: keystoneauth1.session.Session

        :returns: The base URL that will be used to talk to the required
                  service or None if not available.
        :rtype: string
        """
        endpoint_data = self.get_endpoint_data(
            session, discover_versions=False, **kwargs)
        if not endpoint_data:
            return None
        return endpoint_data.url

    def get_connection_params(self, session, **kwargs):
        """Return any additional connection parameters required for the plugin.

        :param session: The session object that the auth_plugin belongs to.
        :type session: keystoneauth1.session.Session

        :returns: Headers that are set to authenticate a message or None for
                  failure. Note that when checking this value that the empty
                  dict is a valid, non-failure response.
        :rtype: dict
        """
        return {}

    def invalidate(self):
        """Invalidate the current authentication data.

        This should result in fetching a new token on next call.

        A plugin may be invalidated if an Unauthorized HTTP response is
        returned to indicate that the token may have been revoked or is
        otherwise now invalid.

        :returns: True if there was something that the plugin did to
                  invalidate. This means that it makes sense to try again. If
                  nothing happens returns False to indicate give up.
        :rtype: bool
        """
        return False

    def get_user_id(self, session, **kwargs):
        """Return a unique user identifier of the plugin.

        Wherever possible the user id should be inferred from the token however
        there are certain URLs and other places that require access to the
        currently authenticated user id.

        :param session: A session object so the plugin can make HTTP calls.
        :type session: keystoneauth1.session.Session

        :returns: A user identifier or None if one is not available.
        :rtype: str
        """
        return None

    def get_project_id(self, session, **kwargs):
        """Return the project id that we are authenticated to.

        Wherever possible the project id should be inferred from the token
        however there are certain URLs and other places that require access to
        the currently authenticated project id.

        :param session: A session object so the plugin can make HTTP calls.
        :type session: keystoneauth1.session.Session

        :returns: A project identifier or None if one is not available.
        :rtype: str
        """
        return None

    def get_sp_auth_url(self, session, sp_id, **kwargs):
        """Return auth_url from the Service Provider object.

        This url is used for obtaining unscoped federated token from remote
        cloud.

        :param sp_id: ID of the Service Provider to be queried.
        :type sp_id: string

        :returns: A Service Provider auth_url or None if one is not available.
        :rtype: str

        """
        return None

    def get_sp_url(self, session, sp_id, **kwargs):
        """Return sp_url from the Service Provider object.

        This url is used for passing SAML2 assertion to the remote cloud.

        :param sp_id: ID of the Service Provider to be queried.
        :type sp_id: str

        :returns: A Service Provider sp_url or None if one is not available.
        :rtype: str

        """
        return None

    def get_cache_id(self):
        """Fetch an identifier that uniquely identifies the auth options.

        The returned identifier need not be decomposable or otherwise provide
        anyway to recreate the plugin. It should not contain sensitive data in
        plaintext.

        This string MUST change if any of the parameters that are used to
        uniquely identity this plugin change.

        If get_cache_id returns a str value suggesting that caching is
        supported then get_auth_cache and set_auth_cache must also be
        implemented.

        :returns: A unique string for the set of options
        :rtype: str or None if this is unsupported or unavailable.
        """
        return None

    def get_auth_state(self):
        """Retrieve the current authentication state for the plugin.

        Retrieve any internal state that represents the authenticated plugin.

        This should not fetch any new data if it is not present.

        :raises NotImplementedError: if the plugin does not support this
            feature.

        :returns: raw python data (which can be JSON serialized) that can be
                  moved into another plugin (of the same type) to have the
                  same authenticated state.
        :rtype: object or None if unauthenticated.
        """
        raise NotImplementedError()

    def set_auth_state(self, data):
        """Install existing authentication state for a plugin.

        Take the output of get_auth_state and install that authentication state
        into the current authentication plugin.

        :raises NotImplementedError: if the plugin does not support this
            feature.
        """
        raise NotImplementedError()


class FixedEndpointPlugin(BaseAuthPlugin):
    """A base class for plugins that have one fixed endpoint."""

    def __init__(self, endpoint=None):
        super(FixedEndpointPlugin, self).__init__()
        self.endpoint = endpoint

    def get_endpoint(self, session, **kwargs):
        """Return the supplied endpoint.

        Using this plugin the same endpoint is returned regardless of the
        parameters passed to the plugin. endpoint_override overrides the
        endpoint specified when constructing the plugin.
        """
        return kwargs.get('endpoint_override') or self.endpoint

    def get_endpoint_data(self, session,
                          endpoint_override=None,
                          discover_versions=True,
                          **kwargs):
        """Return a valid endpoint data for a the service.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param str endpoint_override: URL to use for version discovery.
        :param bool discover_versions: Whether to get version metadata from
                                       the version discovery document even
                                       if it major api version info can be
                                       inferred from the url.
                                       (optional, defaults to True)
        :param kwargs: Ignored.

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: Valid EndpointData or None if not available.
        :rtype: `keystoneauth1.discover.EndpointData` or None
        """
        return super(FixedEndpointPlugin, self).get_endpoint_data(
            session,
            endpoint_override=endpoint_override or self.endpoint,
            discover_versions=discover_versions,
            **kwargs)
