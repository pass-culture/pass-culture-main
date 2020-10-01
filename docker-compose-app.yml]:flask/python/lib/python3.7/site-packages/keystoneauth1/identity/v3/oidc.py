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
import warnings

import six

from keystoneauth1 import _utils as utils
from keystoneauth1 import access
from keystoneauth1 import exceptions
from keystoneauth1.identity.v3 import federation

_logger = utils.get_logger(__name__)

__all__ = ('OidcAuthorizationCode',
           'OidcClientCredentials',
           'OidcPassword',
           'OidcAccessToken')


@six.add_metaclass(abc.ABCMeta)
class _OidcBase(federation.FederationBaseAuth):
    """Base class for different OpenID Connect based flows.

    The OpenID Connect specification can be found at::
    ``http://openid.net/specs/openid-connect-core-1_0.html``
    """

    grant_type = None

    def __init__(self, auth_url, identity_provider, protocol,
                 client_id, client_secret,
                 access_token_type,
                 scope="openid profile",
                 access_token_endpoint=None,
                 discovery_endpoint=None,
                 grant_type=None,
                 **kwargs):
        """The OpenID Connect plugin expects the following.

        :param auth_url: URL of the Identity Service
        :type auth_url: string

        :param identity_provider: Name of the Identity Provider the client
                                  will authenticate against
        :type identity_provider: string

        :param protocol: Protocol name as configured in keystone
        :type protocol: string

        :param client_id: OAuth 2.0 Client ID
        :type client_id: string

        :param client_secret: OAuth 2.0 Client Secret
        :type client_secret: string

        :param access_token_type: OAuth 2.0 Authorization Server Introspection
                                  token type, it is used to decide which type
                                  of token will be used when processing token
                                  introspection. Valid values are:
                                  "access_token" or "id_token"
        :type access_token_type: string

        :param access_token_endpoint: OpenID Connect Provider Token Endpoint,
                                      for example:
                                      https://localhost:8020/oidc/OP/token
                                      Note that if a discovery document is
                                      provided this value will override
                                      the discovered one.
        :type access_token_endpoint: string

        :param discovery_endpoint: OpenID Connect Discovery Document URL,
                                   for example:
                  https://localhost:8020/oidc/.well-known/openid-configuration
        :type access_token_endpoint: string

        :param scope: OpenID Connect scope that is requested from OP,
                      for example: "openid profile email", defaults to
                      "openid profile". Note that OpenID Connect specification
                      states that "openid" must be always specified.
        :type scope: string
        """
        super(_OidcBase, self).__init__(auth_url, identity_provider, protocol,
                                        **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

        self.discovery_endpoint = discovery_endpoint
        self._discovery_document = {}
        self.access_token_endpoint = access_token_endpoint

        self.access_token_type = access_token_type
        self.scope = scope

        if grant_type is not None:
            if grant_type != self.grant_type:
                raise exceptions.OidcGrantTypeMissmatch()
            warnings.warn("Passing grant_type as an argument has been "
                          "deprecated as it is now defined in the plugin "
                          "itself. You should stop passing this argument "
                          "to the plugin, as it will be ignored, since you "
                          "cannot pass a free text string as a grant_type. "
                          "This argument will be dropped from the plugin in "
                          "July 2017 or with the next major release of "
                          "keystoneauth (3.0.0)",
                          DeprecationWarning)

    def _get_discovery_document(self, session):
        """Get the contents of the OpenID Connect Discovery Document.

        This method grabs the contents of the OpenID Connect Discovery Document
        if a discovery_endpoint was passed to the constructor and returns it as
        a dict, otherwise returns an empty dict. Note that it will fetch the
        discovery document only once, so subsequent calls to this method will
        return the cached result, if any.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a python dictionary containing the discovery document if any,
                  otherwise it will return an empty dict.
        :rtype: dict
        """
        if (self.discovery_endpoint is not None and
                not self._discovery_document):
            try:
                resp = session.get(self.discovery_endpoint,
                                   authenticated=False)
            except exceptions.HttpError:
                _logger.error("Cannot fetch discovery document %(discovery)s" %
                              {"discovery": self.discovery_endpoint})
                raise

            try:
                self._discovery_document = resp.json()
            except Exception:
                pass

            if not self._discovery_document:
                raise exceptions.InvalidOidcDiscoveryDocument()

        return self._discovery_document

    def _get_access_token_endpoint(self, session):
        """Get the "token_endpoint" for the OpenID Connect flow.

        This method will return the correct access token endpoint to be used.
        If the user has explicitly passed an access_token_endpoint to the
        constructor that will be returned. If there is no explicit endpoint and
        a discovery url is provided, it will try to get it from the discovery
        document. If nothing is found, an exception will be raised.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :return: the endpoint to use
        :rtype: string or None if no endpoint is found
        """
        if self.access_token_endpoint is not None:
            return self.access_token_endpoint

        discovery = self._get_discovery_document(session)
        endpoint = discovery.get("token_endpoint")
        if endpoint is None:
            raise exceptions.OidcAccessTokenEndpointNotFound()
        return endpoint

    def _get_access_token(self, session, payload):
        """Exchange a variety of user supplied values for an access token.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :param payload: a dict containing various OpenID Connect values, for
                        example::
                          {'grant_type': 'password', 'username': self.username,
                           'password': self.password, 'scope': self.scope}
        :type payload: dict
        """
        client_auth = (self.client_id, self.client_secret)
        access_token_endpoint = self._get_access_token_endpoint(session)

        op_response = session.post(access_token_endpoint,
                                   requests_auth=client_auth,
                                   data=payload,
                                   authenticated=False)
        access_token = op_response.json()[self.access_token_type]
        return access_token

    def _get_keystone_token(self, session, access_token):
        r"""Exchange an access token for a keystone token.

        By Sending the access token in an `Authorization: Bearer` header, to
        an OpenID Connect protected endpoint (Federated Token URL). The
        OpenID Connect server will use the access token to look up information
        about the authenticated user (this technique is called instrospection).
        The output of the instrospection will be an OpenID Connect Claim, that
        will be used against the mapping engine. Should the mapping engine
        succeed, a Keystone token will be presented to the user.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :param access_token: The OpenID Connect access token.
        :type access_token: str
        """
        # use access token against protected URL
        headers = {'Authorization': 'Bearer ' + access_token}
        auth_response = session.post(self.federated_token_url,
                                     headers=headers,
                                     authenticated=False)
        return auth_response

    def get_unscoped_auth_ref(self, session):
        """Authenticate with OpenID Connect and get back claims.

        This is a multi-step process:

        1.- An access token must be retrieved from the server. In order to do
            so, we need to exchange an authorization grant or refresh token
            with the token endpoint in order to obtain an access token. The
            authorization grant varies from plugin to plugin.

        2.- We then exchange the access token upon accessing the protected
            Keystone endpoint (federated auth URL). This will trigger the
            OpenID Connect Provider to perform a user introspection and
            retrieve information (specified in the scope) about the user in the
            form of an OpenID Connect Claim. These claims will be sent to
            Keystone in the form of environment variables.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a token data representation
        :rtype: :py:class:`keystoneauth1.access.AccessInfoV3`
        """
        # First of all, check if the grant type is supported
        discovery = self._get_discovery_document(session)
        grant_types = discovery.get("grant_types_supported")
        if (grant_types and
                self.grant_type is not None and
                self.grant_type not in grant_types):
            raise exceptions.OidcPluginNotSupported()

        # Get the payload
        payload = self.get_payload(session)
        payload.setdefault('grant_type', self.grant_type)

        # get an access token
        access_token = self._get_access_token(session, payload)

        response = self._get_keystone_token(session, access_token)

        # grab the unscoped token
        return access.create(resp=response)

    @abc.abstractmethod
    def get_payload(self, session):
        """Get the plugin specific payload for obtainin an access token.

        OpenID Connect supports different grant types. This method should
        prepare the payload that needs to be exchanged with the server in
        order to get an access token for the particular grant type that the
        plugin is implementing.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a python dictionary containing the payload to be exchanged
        :rtype: dict
        """
        raise NotImplementedError()


class OidcPassword(_OidcBase):
    """Implementation for OpenID Connect Resource Owner Password Credential."""

    grant_type = "password"

    def __init__(self, auth_url, identity_provider, protocol,  # nosec
                 client_id, client_secret,
                 access_token_endpoint=None,
                 discovery_endpoint=None,
                 access_token_type='access_token',
                 username=None, password=None,
                 **kwargs):
        """The OpenID Password plugin expects the following.

        :param username: Username used to authenticate
        :type username: string

        :param password: Password used to authenticate
        :type password: string
        """
        super(OidcPassword, self).__init__(
            auth_url=auth_url,
            identity_provider=identity_provider,
            protocol=protocol,
            client_id=client_id,
            client_secret=client_secret,
            access_token_endpoint=access_token_endpoint,
            discovery_endpoint=discovery_endpoint,
            access_token_type=access_token_type,
            **kwargs)
        self.username = username
        self.password = password

    def get_payload(self, session):
        """Get an authorization grant for the "password" grant type.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a python dictionary containing the payload to be exchanged
        :rtype: dict
        """
        payload = {'username': self.username,
                   'password': self.password,
                   'scope': self.scope}
        return payload


class OidcClientCredentials(_OidcBase):
    """Implementation for OpenID Connect Client Credentials."""

    grant_type = 'client_credentials'

    def __init__(self, auth_url, identity_provider, protocol,  # nosec
                 client_id, client_secret,
                 access_token_endpoint=None,
                 discovery_endpoint=None,
                 access_token_type='access_token',
                 **kwargs):
        """The OpenID Client Credentials expects the following.

        :param client_id: Client ID used to authenticate
        :type username: string

        :param client_secret: Client Secret used to authenticate
        :type password: string
        """
        super(OidcClientCredentials, self).__init__(
            auth_url=auth_url,
            identity_provider=identity_provider,
            protocol=protocol,
            client_id=client_id,
            client_secret=client_secret,
            access_token_endpoint=access_token_endpoint,
            discovery_endpoint=discovery_endpoint,
            access_token_type=access_token_type,
            **kwargs)

    def get_payload(self, session):
        """Get an authorization grant for the client credentials grant type.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a python dictionary containing the payload to be exchanged
        :rtype: dict
        """
        payload = {'scope': self.scope}
        return payload


class OidcAuthorizationCode(_OidcBase):
    """Implementation for OpenID Connect Authorization Code."""

    grant_type = 'authorization_code'

    def __init__(self, auth_url, identity_provider, protocol,  # nosec
                 client_id, client_secret,
                 access_token_endpoint=None,
                 discovery_endpoint=None,
                 access_token_type='access_token',
                 redirect_uri=None, code=None, **kwargs):
        """The OpenID Authorization Code plugin expects the following.

        :param redirect_uri: OpenID Connect Client Redirect URL
        :type redirect_uri: string

        :param code: OAuth 2.0 Authorization Code
        :type code: string

        """
        super(OidcAuthorizationCode, self).__init__(
            auth_url=auth_url,
            identity_provider=identity_provider,
            protocol=protocol,
            client_id=client_id,
            client_secret=client_secret,
            access_token_endpoint=access_token_endpoint,
            discovery_endpoint=discovery_endpoint,
            access_token_type=access_token_type,
            **kwargs)
        self.redirect_uri = redirect_uri
        self.code = code

    def get_payload(self, session):
        """Get an authorization grant for the "authorization_code" grant type.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a python dictionary containing the payload to be exchanged
        :rtype: dict
        """
        payload = {'redirect_uri': self.redirect_uri, 'code': self.code}

        return payload


class OidcAccessToken(_OidcBase):
    """Implementation for OpenID Connect access token reuse."""

    def __init__(self, auth_url, identity_provider, protocol,
                 access_token, **kwargs):
        """The OpenID Connect plugin based on the Access Token.

        It expects the following:

        :param auth_url: URL of the Identity Service
        :type auth_url: string

        :param identity_provider: Name of the Identity Provider the client
                                  will authenticate against
        :type identity_provider: string

        :param protocol: Protocol name as configured in keystone
        :type protocol: string

        :param access_token: OpenID Connect Access token
        :type access_token: string
        """
        super(OidcAccessToken, self).__init__(auth_url, identity_provider,
                                              protocol,
                                              client_id=None,
                                              client_secret=None,
                                              access_token_endpoint=None,
                                              access_token_type=None,
                                              **kwargs)
        self.access_token = access_token

    def get_payload(self, session):
        """OidcAccessToken does not require a payload."""
        return {}

    def get_unscoped_auth_ref(self, session):
        """Authenticate with OpenID Connect and get back claims.

        We exchange the access token upon accessing the protected Keystone
        endpoint (federated auth URL). This will trigger the OpenID Connect
        Provider to perform a user introspection and retrieve information
        (specified in the scope) about the user in the form of an OpenID
        Connect Claim. These claims will be sent to Keystone in the form of
        environment variables.

        :param session: a session object to send out HTTP requests.
        :type session: keystoneauth1.session.Session

        :returns: a token data representation
        :rtype: :py:class:`keystoneauth1.access.AccessInfoV3`
        """
        response = self._get_keystone_token(session, self.access_token)
        return access.create(resp=response)
