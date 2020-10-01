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
import base64
import functools
import hashlib
import json
import threading

import six

from keystoneauth1 import _utils as utils
from keystoneauth1 import access
from keystoneauth1 import discover
from keystoneauth1 import exceptions
from keystoneauth1 import plugin

LOG = utils.get_logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseIdentityPlugin(plugin.BaseAuthPlugin):

    # we count a token as valid (not needing refreshing) if it is valid for at
    # least this many seconds before the token expiry time
    MIN_TOKEN_LIFE_SECONDS = 120

    def __init__(self, auth_url=None, reauthenticate=True):

        super(BaseIdentityPlugin, self).__init__()

        self.auth_url = auth_url
        self.auth_ref = None
        self.reauthenticate = reauthenticate

        self._lock = threading.Lock()

    @abc.abstractmethod
    def get_auth_ref(self, session, **kwargs):
        """Obtain a token from an OpenStack Identity Service.

        This method is overridden by the various token version plugins.

        This function should not be called independently and is expected to be
        invoked via the do_authenticate function.

        This function will be invoked if the AcessInfo object cached by the
        plugin is not valid. Thus plugins should always fetch a new AccessInfo
        when invoked. If you are looking to just retrieve the current auth
        data then you should use get_access.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session

        :raises keystoneauth1.exceptions.response.InvalidResponse:
            The response returned wasn't appropriate.
        :raises keystoneauth1.exceptions.http.HttpError:
            An error from an invalid HTTP response.

        :returns: Token access information.
        :rtype: :class:`keystoneauth1.access.AccessInfo`
        """

    def get_token(self, session, **kwargs):
        """Return a valid auth token.

        If a valid token is not present then a new one will be fetched.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: A valid token.
        :rtype: string
        """
        return self.get_access(session).auth_token

    def _needs_reauthenticate(self):
        """Return if the existing token needs to be re-authenticated.

        The token should be refreshed if it is about to expire.

        :returns: True if the plugin should fetch a new token. False otherwise.
        """
        if not self.auth_ref:
            # authentication was never fetched.
            return True

        if not self.reauthenticate:
            # don't re-authenticate if it has been disallowed.
            return False

        if self.auth_ref.will_expire_soon(self.MIN_TOKEN_LIFE_SECONDS):
            # if it's about to expire we should re-authenticate now.
            return True

        # otherwise it's fine and use the existing one.
        return False

    def get_access(self, session, **kwargs):
        """Fetch or return a current AccessInfo object.

        If a valid AccessInfo is present then it is returned otherwise a new
        one will be fetched.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :returns: Valid AccessInfo
        :rtype: :class:`keystoneauth1.access.AccessInfo`
        """
        # Hey Kids! Thread safety is important particularly in the case where
        # a service is creating an admin style plugin that will then proceed
        # to make calls from many threads. As a token expires all the threads
        # will try and fetch a new token at once, so we want to ensure that
        # only one thread tries to actually fetch from keystone at once.
        with self._lock:
            if self._needs_reauthenticate():
                self.auth_ref = self.get_auth_ref(session)

        return self.auth_ref

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
        if self.auth_ref:
            self.auth_ref = None
            return True

        return False

    def get_endpoint_data(self, session, service_type=None, interface=None,
                          region_name=None, service_name=None, allow=None,
                          allow_version_hack=True, discover_versions=True,
                          skip_discovery=False, min_version=None,
                          max_version=None, endpoint_override=None, **kwargs):
        """Return a valid endpoint data for a service.

        If a valid token is not present then a new one will be fetched using
        the session and kwargs.

        version, min_version and max_version can all be given either as a
        string or a tuple.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param string service_type: The type of service to lookup the endpoint
                                    for. This plugin will return None (failure)
                                    if service_type is not provided.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference. Can also be
                          `keystoneauth1.plugin.AUTH_INTERFACE` to indicate
                          that the auth_url should be used instead of the
                          value in the catalog. (optional, defaults to public)
        :param string region_name: The region the endpoint should exist in.
                                   (optional)
        :param string service_name: The name of the service in the catalog.
                                   (optional)
        :param dict allow: Extra filters to pass when discovering API
                           versions. (optional)
        :param bool allow_version_hack: Allow keystoneauth to hack up catalog
                                        URLS to support older schemes.
                                        (optional, default True)
        :param bool discover_versions: Whether to get version metadata from
                                       the version discovery document even
                                       if it's not neccessary to fulfill the
                                       major version request. (optional,
                                       defaults to True)
        :param bool skip_discovery: Whether to skip version discovery even
                                    if a version has been given. This is useful
                                    if endpoint_override or similar has been
                                    given and grabbing additional information
                                    about the endpoint is not useful.
        :param min_version: The minimum version that is acceptable. Mutually
                            exclusive with version. If min_version is given
                            with no max_version it is as if max version is
                            'latest'. (optional)
        :param max_version: The maximum version that is acceptable. Mutually
                            exclusive with version. If min_version is given
                            with no max_version it is as if max version is
                            'latest'. (optional)
        :param str endpoint_override: URL to use instead of looking in the
                                      catalog. Catalog lookup will be skipped,
                                      but version discovery will be run.
                                      Sets allow_version_hack to False
                                      (optional)
        :param kwargs: Ignored.

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: Valid EndpointData or None if not available.
        :rtype: `keystoneauth1.discover.EndpointData` or None
        """
        allow = allow or {}

        min_version, max_version = discover._normalize_version_args(
            None, min_version, max_version, service_type=service_type)

        # NOTE(jamielennox): if you specifically ask for requests to be sent to
        # the auth url then we can ignore many of the checks. Typically if you
        # are asking for the auth endpoint it means that there is no catalog to
        # query however we still need to support asking for a specific version
        # of the auth_url for generic plugins.
        if interface is plugin.AUTH_INTERFACE:
            endpoint_data = discover.EndpointData(
                service_url=self.auth_url,
                service_type=service_type or 'identity')
            project_id = None
        elif endpoint_override:
            # TODO(mordred) Make a code path that will look for a
            #               matching entry in the catalog if the catalog
            #               exists and fill in the interface, region_name, etc.
            #               For now, just use any information the use has
            #               provided.
            endpoint_data = discover.EndpointData(
                service_url=endpoint_override,
                catalog_url=endpoint_override,
                interface=interface,
                region_name=region_name,
                service_name=service_name)
            # Setting an endpoint_override then calling get_endpoint_data means
            # you absolutely want the discovery info for the URL in question.
            # There are no code flows where this will happen for any other
            # reasons.
            allow_version_hack = False
            project_id = self.get_project_id(session)
        else:
            if not service_type:
                LOG.warning('Plugin cannot return an endpoint without '
                            'knowing the service type that is required. Add '
                            'service_type to endpoint filtering data.')
                return None

            # It's possible for things higher in the stack, because of
            # defaults, to explicitly pass None.
            if not interface:
                interface = 'public'

            service_catalog = self.get_access(session).service_catalog
            project_id = self.get_project_id(session)
            # NOTE(mordred): service_catalog.url_data_for raises if it can't
            # find a match, so this will always be a valid object.
            endpoint_data = service_catalog.endpoint_data_for(
                service_type=service_type,
                interface=interface,
                region_name=region_name,
                service_name=service_name)
            if not endpoint_data:
                return None

        if skip_discovery:
            return endpoint_data

        try:
            return endpoint_data.get_versioned_data(
                session,
                project_id=project_id,
                min_version=min_version,
                max_version=max_version,
                cache=self._discovery_cache,
                discover_versions=discover_versions,
                allow_version_hack=allow_version_hack, allow=allow)
        except (exceptions.DiscoveryFailure,
                exceptions.HttpError,
                exceptions.ConnectionError):
            # If a version was requested, we didn't find it, return
            # None.
            if max_version or min_version:
                return None
            # If one wasn't, then the endpoint_data we already have
            # should be fine
            return endpoint_data

    def get_endpoint(self, session, service_type=None, interface=None,
                     region_name=None, service_name=None, version=None,
                     allow=None, allow_version_hack=True,
                     skip_discovery=False,
                     min_version=None, max_version=None,
                     **kwargs):
        """Return a valid endpoint for a service.

        If a valid token is not present then a new one will be fetched using
        the session and kwargs.

        version, min_version and max_version can all be given either as a
        string or a tuple.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param string service_type: The type of service to lookup the endpoint
                                    for. This plugin will return None (failure)
                                    if service_type is not provided.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference. Can also be
                          `keystoneauth1.plugin.AUTH_INTERFACE` to indicate
                          that the auth_url should be used instead of the
                          value in the catalog. (optional, defaults to public)
        :param string region_name: The region the endpoint should exist in.
                                   (optional)
        :param string service_name: The name of the service in the catalog.
                                   (optional)
        :param version: The minimum version number required for this
                        endpoint. (optional)
        :param dict allow: Extra filters to pass when discovering API
                           versions. (optional)
        :param bool allow_version_hack: Allow keystoneauth to hack up catalog
                                        URLS to support older schemes.
                                        (optional, default True)
        :param bool skip_discovery: Whether to skip version discovery even
                                    if a version has been given. This is useful
                                    if endpoint_override or similar has been
                                    given and grabbing additional information
                                    about the endpoint is not useful.
        :param min_version: The minimum version that is acceptable. Mutually
                            exclusive with version. If min_version is given
                            with no max_version it is as if max version is
                            'latest'. (optional)
        :param max_version: The maximum version that is acceptable. Mutually
                            exclusive with version. If min_version is given
                            with no max_version it is as if max version is
                            'latest'. (optional)

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: A valid endpoint URL or None if not available.
        :rtype: string or None
        """
        # Explode `version` into min_version and max_version - everything below
        # here uses the latter rather than the former.
        min_version, max_version = discover._normalize_version_args(
            version, min_version, max_version, service_type=service_type)
        # Set discover_versions to False since we're only going to return
        # a URL. Fetching the microversion data would be needlessly
        # expensive in the common case. However, discover_versions=False
        # will still run discovery if the version requested is not the
        # version in the catalog.
        endpoint_data = self.get_endpoint_data(
            session, service_type=service_type, interface=interface,
            region_name=region_name, service_name=service_name,
            allow=allow, min_version=min_version, max_version=max_version,
            discover_versions=False, skip_discovery=skip_discovery,
            allow_version_hack=allow_version_hack, **kwargs)
        return endpoint_data.url if endpoint_data else None

    def get_api_major_version(self, session, service_type=None, interface=None,
                              region_name=None, service_name=None,
                              version=None, allow=None,
                              allow_version_hack=True, skip_discovery=False,
                              discover_versions=False, min_version=None,
                              max_version=None, **kwargs):
        """Return the major API version for a service.

        If a valid token is not present then a new one will be fetched using
        the session and kwargs.

        version, min_version and max_version can all be given either as a
        string or a tuple.

        Valid interface types: `public` or `publicURL`,
                               `internal` or `internalURL`,
                               `admin` or 'adminURL`

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param string service_type: The type of service to lookup the endpoint
                                    for. This plugin will return None (failure)
                                    if service_type is not provided.
        :param interface: Type of endpoint. Can be a single value or a list
                          of values. If it's a list of values, they will be
                          looked for in order of preference. Can also be
                          `keystoneauth1.plugin.AUTH_INTERFACE` to indicate
                          that the auth_url should be used instead of the
                          value in the catalog. (optional, defaults to public)
        :param string region_name: The region the endpoint should exist in.
                                   (optional)
        :param string service_name: The name of the service in the catalog.
                                   (optional)
        :param version: The minimum version number required for this
                        endpoint. (optional)
        :param dict allow: Extra filters to pass when discovering API
                           versions. (optional)
        :param bool allow_version_hack: Allow keystoneauth to hack up catalog
                                        URLS to support older schemes.
                                        (optional, default True)
        :param bool skip_discovery: Whether to skip version discovery even
                                    if a version has been given. This is useful
                                    if endpoint_override or similar has been
                                    given and grabbing additional information
                                    about the endpoint is not useful.
        :param bool discover_versions: Whether to get version metadata from
                                       the version discovery document even
                                       if it's not neccessary to fulfill the
                                       major version request. Defaults to False
                                       because get_endpoint doesn't need
                                       metadata. (optional, defaults to False)
        :param min_version: The minimum version that is acceptable. Mutually
                            exclusive with version. If min_version is given
                            with no max_version it is as if max version is
                            'latest'. (optional)
        :param max_version: The maximum version that is acceptable. Mutually
                            exclusive with version. If min_version is given
                            with no max_version it is as if max version is
                            'latest'. (optional)

        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :return: The major version of the API of the service discovered.
        :rtype: tuple or None

        .. note:: Implementation notes follow. Users should not need to wrap
                  their head around these implementation notes.
                  `get_api_major_version` should do what is expected with the
                  least possible cost while still consistently returning a
                  value if possible.

        There are many cases when major version can be satisfied
        without actually calling the discovery endpoint (like when the version
        is in the url). If the user has a cloud with the versioned endpoint
        ``https://volume.example.com/v3`` in the catalog for the
        ``block-storage`` service and they do::

          client = adapter.Adapter(
              session, service_type='block-storage', min_version=2,
              max_version=3)
          volume_version = client.get_api_major_version()

        The version actually be returned with no api calls other than getting
        the token. For that reason, :meth:`.get_api_major_version` first
        calls :meth:`.get_endpoint_data` with ``discover_versions=False``.

        If their catalog has an unversioned endpoint
        ``https://volume.example.com`` for the ``block-storage`` service
        and they do this::

          client = adapter.Adapter(session, service_type='block-storage')

        client is now set up to "use whatever is in the catalog". Since the
        url doesn't have a version, :meth:`.get_endpoint_data` with
        ``discover_versions=False`` will result in ``api_version=None``.
        (No version was requested so it didn't need to do the round trip)

        In order to find out what version the endpoint actually is, we must
        make a round trip. Therefore, if ``api_version`` is ``None`` after
        the first call, :meth:`.get_api_major_version` will make a second
        call to :meth:`.get_endpoint_data` with ``discover_versions=True``.

        """
        allow = allow or {}
        # Explode `version` into min_version and max_version - everything below
        # here uses the latter rather than the former.
        min_version, max_version = discover._normalize_version_args(
            version, min_version, max_version, service_type=service_type)
        # Using functools.partial here just to reduce copy-pasta of params
        get_endpoint_data = functools.partial(
            self.get_endpoint_data,
            session, service_type=service_type, interface=interface,
            region_name=region_name, service_name=service_name,
            allow=allow, min_version=min_version, max_version=max_version,
            skip_discovery=skip_discovery,
            allow_version_hack=allow_version_hack, **kwargs)
        data = get_endpoint_data(discover_versions=discover_versions)
        if (not data or not data.api_version) and not discover_versions:
            # It's possible that no version was requested and the endpoint
            # in the catalog has no version in the URL. A version has been
            # requested, so now it's ok to run discovery.

            data = get_endpoint_data(discover_versions=True)
        if not data:
            return None
        return data.api_version

    def get_all_version_data(self, session, interface='public',
                             region_name=None, service_type=None,
                             **kwargs):
        """Get version data for all services in the catalog.

        :param session: A session object that can be used for communication.
        :type session: keystoneauth1.session.Session
        :param interface:
            Type of endpoint to get version data for. Can be a single value
            or a list of values. A value of None indicates that all interfaces
            should be queried. (optional, defaults to public)
        :param string region_name:
            Region of endpoints to get version data for. A valueof None
            indicates that all regions should be queried. (optional, defaults
            to None)
        :param string service_type:
            Limit the version data to a single service. (optional, defaults
            to None)
        :returns: A dictionary keyed by region_name with values containing
            dictionaries keyed by interface with values being a list of
            :class:`~keystoneauth1.discover.VersionData`.
        """
        service_types = discover._SERVICE_TYPES
        catalog = self.get_access(session).service_catalog
        version_data = {}
        endpoints_data = catalog.get_endpoints_data(
            interface=interface,
            region_name=region_name,
            service_type=service_type,
        )

        for endpoint_service_type, services in endpoints_data.items():
            if service_types.is_known(endpoint_service_type):
                endpoint_service_type = service_types.get_service_type(
                    endpoint_service_type)

            for service in services:
                versions = service.get_all_version_string_data(
                    session=session,
                    project_id=self.get_project_id(session),
                )

                if service.region_name not in version_data:
                    version_data[service.region_name] = {}
                regions = version_data[service.region_name]

                interface = service.interface.rstrip('URL')
                if interface not in regions:
                    regions[interface] = {}
                regions[interface][endpoint_service_type] = versions

        return version_data

    def get_user_id(self, session, **kwargs):
        return self.get_access(session).user_id

    def get_project_id(self, session, **kwargs):
        return self.get_access(session).project_id

    def get_sp_auth_url(self, session, sp_id, **kwargs):
        try:
            return self.get_access(
                session).service_providers.get_auth_url(sp_id)
        except exceptions.ServiceProviderNotFound:
            return None

    def get_sp_url(self, session, sp_id, **kwargs):
        try:
            return self.get_access(
                session).service_providers.get_sp_url(sp_id)
        except exceptions.ServiceProviderNotFound:
            return None

    def get_discovery(self, session, url, authenticated=None):
        """Return the discovery object for a URL.

        Check the session and the plugin cache to see if we have already
        performed discovery on the URL and if so return it, otherwise create
        a new discovery object, cache it and return it.

        This function is expected to be used by subclasses and should not
        be needed by users.

        :param session: A session object to discover with.
        :type session: keystoneauth1.session.Session
        :param str url: The url to lookup.
        :param bool authenticated: Include a token in the discovery call.
                                   (optional) Defaults to None (use a token
                                   if a plugin is installed).

        :raises keystoneauth1.exceptions.discovery.DiscoveryFailure:
            if for some reason the lookup fails.
        :raises keystoneauth1.exceptions.http.HttpError: An error from an
                                                         invalid HTTP response.

        :returns: A discovery object with the results of looking up that URL.
        """
        return discover.get_discovery(session=session, url=url,
                                      cache=self._discovery_cache,
                                      authenticated=authenticated)

    def get_cache_id_elements(self):
        """Get the elements for this auth plugin that make it unique.

        As part of the get_cache_id requirement we need to determine what
        aspects of this plugin and its values that make up the unique elements.

        This should be overridden by plugins that wish to allow caching.

        :returns: The unique attributes and values of this plugin.
        :rtype: A flat dict with a str key and str or None value. This is
                required as we feed these values into a hash. Pairs where the
                value is None are ignored in the hashed id.
        """
        raise NotImplementedError()

    def get_cache_id(self):
        """Fetch an identifier that uniquely identifies the auth options.

        The returned identifier need not be decomposable or otherwise provide
        any way to recreate the plugin.

        This string MUST change if any of the parameters that are used to
        uniquely identity this plugin change. It should not change upon a
        reauthentication of the plugin.

        :returns: A unique string for the set of options
        :rtype: str or None if this is unsupported or unavailable.
        """
        try:
            elements = self.get_cache_id_elements()
        except NotImplementedError:
            return None

        hasher = hashlib.sha256()

        for k, v in sorted(elements.items()):
            if v is not None:
                # NOTE(jamielennox): in python3 you need to pass bytes to hash
                if isinstance(k, six.string_types):
                    k = k.encode('utf-8')
                if isinstance(v, six.string_types):
                    v = v.encode('utf-8')

                hasher.update(k)
                hasher.update(v)

        return base64.b64encode(hasher.digest()).decode('utf-8')

    def get_auth_state(self):
        """Retrieve the current authentication state for the plugin.

        Retrieve any internal state that represents the authenticated plugin.

        This should not fetch any new data if it is not present.

        :returns: a string that can be stored or None if there is no auth state
                  present in the plugin. This string can be reloaded with
                  set_auth_state to set the same authentication.
        :rtype: str or None if no auth present.
        """
        if self.auth_ref:
            data = {'auth_token': self.auth_ref.auth_token,
                    'body': self.auth_ref._data}

            return json.dumps(data)

    def set_auth_state(self, data):
        """Install existing authentication state for a plugin.

        Take the output of get_auth_state and install that authentication state
        into the current authentication plugin.
        """
        if data:
            auth_data = json.loads(data)
            self.auth_ref = access.create(body=auth_data['body'],
                                          auth_token=auth_data['auth_token'])
        else:
            self.auth_ref = None
