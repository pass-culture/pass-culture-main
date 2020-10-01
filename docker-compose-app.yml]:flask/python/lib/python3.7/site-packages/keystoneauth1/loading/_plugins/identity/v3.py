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

from keystoneauth1 import exceptions
from keystoneauth1 import identity
from keystoneauth1 import loading


def _add_common_identity_options(options):
    options.extend([
        loading.Opt('user-id', help='User ID'),
        loading.Opt('username',
                    help='Username',
                    deprecated=[loading.Opt('user-name')]),
        loading.Opt('user-domain-id', help="User's domain id"),
        loading.Opt('user-domain-name', help="User's domain name"),
    ])


def _assert_identity_options(options):
    if (options.get('username') and
            not (options.get('user_domain_name') or
                 options.get('user_domain_id'))):
        m = "You have provided a username. In the V3 identity API a " \
            "username is only unique within a domain so you must " \
            "also provide either a user_domain_id or user_domain_name."
        raise exceptions.OptionError(m)


class Password(loading.BaseV3Loader):

    @property
    def plugin_class(self):
        return identity.V3Password

    def get_options(self):
        options = super(Password, self).get_options()
        _add_common_identity_options(options)

        options.extend([
            loading.Opt('password',
                        secret=True,
                        prompt='Password: ',
                        help="User's password"),
        ])

        return options

    def load_from_options(self, **kwargs):
        _assert_identity_options(kwargs)

        return super(Password, self).load_from_options(**kwargs)


class Token(loading.BaseV3Loader):

    @property
    def plugin_class(self):
        return identity.V3Token

    def get_options(self):
        options = super(Token, self).get_options()

        options.extend([
            loading.Opt('token',
                        secret=True,
                        help='Token to authenticate with'),
        ])

        return options


class _OpenIDConnectBase(loading.BaseFederationLoader):

    def load_from_options(self, **kwargs):
        if not (kwargs.get('access_token_endpoint') or
                kwargs.get('discovery_endpoint')):
            m = ("You have to specify either an 'access-token-endpoint' or "
                 "a 'discovery-endpoint'.")
            raise exceptions.OptionError(m)

        return super(_OpenIDConnectBase, self).load_from_options(**kwargs)

    def get_options(self):
        options = super(_OpenIDConnectBase, self).get_options()

        options.extend([
            loading.Opt('client-id', help='OAuth 2.0 Client ID'),
            loading.Opt('client-secret', secret=True,
                        help='OAuth 2.0 Client Secret'),
            loading.Opt('openid-scope', default="openid profile",
                        dest="scope",
                        help='OpenID Connect scope that is requested from '
                             'authorization server. Note that the OpenID '
                             'Connect specification states that "openid" '
                             'must be always specified.'),
            loading.Opt('access-token-endpoint',
                        help='OpenID Connect Provider Token Endpoint. Note '
                        'that if a discovery document is being passed this '
                        'option will override the endpoint provided by the '
                        'server in the discovery document.'),
            loading.Opt('discovery-endpoint',
                        help='OpenID Connect Discovery Document URL. '
                        'The discovery document will be used to obtain the '
                        'values of the access token endpoint and the '
                        'authentication endpoint. This URL should look like '
                        'https://idp.example.org/.well-known/'
                        'openid-configuration'),
            loading.Opt('access-token-type',
                        help='OAuth 2.0 Authorization Server Introspection '
                             'token type, it is used to decide which type '
                             'of token will be used when processing token '
                             'introspection. Valid values are: '
                             '"access_token" or "id_token"'),
        ])

        return options


class OpenIDConnectClientCredentials(_OpenIDConnectBase):

    @property
    def plugin_class(self):
        return identity.V3OidcClientCredentials

    def get_options(self):
        options = super(OpenIDConnectClientCredentials, self).get_options()

        return options


class OpenIDConnectPassword(_OpenIDConnectBase):

    @property
    def plugin_class(self):
        return identity.V3OidcPassword

    def get_options(self):
        options = super(OpenIDConnectPassword, self).get_options()

        options.extend([
            loading.Opt('username', help='Username', required=True),
            loading.Opt('password', secret=True,
                        help='Password', required=True),
        ])

        return options


class OpenIDConnectAuthorizationCode(_OpenIDConnectBase):

    @property
    def plugin_class(self):
        return identity.V3OidcAuthorizationCode

    def get_options(self):
        options = super(OpenIDConnectAuthorizationCode, self).get_options()

        options.extend([
            loading.Opt('redirect-uri', help='OpenID Connect Redirect URL'),
            loading.Opt('code', secret=True, required=True,
                        deprecated=[loading.Opt('authorization-code')],
                        help='OAuth 2.0 Authorization Code'),
        ])

        return options


class OpenIDConnectAccessToken(loading.BaseFederationLoader):

    @property
    def plugin_class(self):
        return identity.V3OidcAccessToken

    def get_options(self):
        options = super(OpenIDConnectAccessToken, self).get_options()

        options.extend([
            loading.Opt('access-token', secret=True, required=True,
                        help='OAuth 2.0 Access Token'),
        ])
        return options


class TOTP(loading.BaseV3Loader):

    @property
    def plugin_class(self):
        return identity.V3TOTP

    def get_options(self):
        options = super(TOTP, self).get_options()
        _add_common_identity_options(options)

        options.extend([
            loading.Opt(
                'passcode',
                secret=True,
                prompt='TOTP passcode: ',
                help="User's TOTP passcode"),
        ])

        return options

    def load_from_options(self, **kwargs):
        _assert_identity_options(kwargs)

        return super(TOTP, self).load_from_options(**kwargs)


class TokenlessAuth(loading.BaseLoader):

    @property
    def plugin_class(self):
        return identity.V3TokenlessAuth

    def get_options(self):
        options = super(TokenlessAuth, self).get_options()

        options.extend([
            loading.Opt('auth-url', required=True,
                        help='Authentication URL'),
            loading.Opt('domain-id', help='Domain ID to scope to'),
            loading.Opt('domain-name', help='Domain name to scope to'),
            loading.Opt('project-id', help='Project ID to scope to'),
            loading.Opt('project-name', help='Project name to scope to'),
            loading.Opt('project-domain-id',
                        help='Domain ID containing project'),
            loading.Opt('project-domain-name',
                        help='Domain name containing project'),
        ])

        return options

    def load_from_options(self, **kwargs):
        if (not kwargs.get('domain_id') and
                not kwargs.get('domain_name') and
                not kwargs.get('project_id') and
                not kwargs.get('project_name') or
                (kwargs.get('project_name') and
                    not (kwargs.get('project_domain_name') or
                         kwargs.get('project_domain_id')))):
            m = ('You need to provide either a domain_name, domain_id, '
                 'project_id or project_name. '
                 'If you have provided a project_name, in the V3 identity '
                 'API a project_name is only unique within a domain so '
                 'you must also provide either a project_domain_id or '
                 'project_domain_name.')
            raise exceptions.OptionError(m)

        return super(TokenlessAuth, self).load_from_options(**kwargs)


class ApplicationCredential(loading.BaseV3Loader):

    @property
    def plugin_class(self):
        return identity.V3ApplicationCredential

    def get_options(self):
        options = super(ApplicationCredential, self).get_options()
        _add_common_identity_options(options)

        options.extend([
            loading.Opt('application_credential_secret', secret=True,
                        required=True,
                        help="Application credential auth secret"),
        ]),
        options.extend([
            loading.Opt('application_credential_id',
                        help='Application credential ID'),
        ]),
        options.extend([
            loading.Opt('application_credential_name',
                        help='Application credential name'),
        ])

        return options

    def load_from_options(self, **kwargs):
        _assert_identity_options(kwargs)
        if (not kwargs.get('application_credential_id') and
                not kwargs.get('application_credential_name')):
            m = ('You must provide either an application credential ID or an '
                 'application credential name and user.')
            raise exceptions.OptionError(m)
        if not kwargs.get('application_credential_secret'):
            m = ('You must provide an auth secret.')
            raise exceptions.OptionError(m)

        return super(ApplicationCredential, self).load_from_options(**kwargs)


class MultiFactor(loading.BaseV3Loader):

    def __init__(self, *args, **kwargs):
        self._methods = None
        return super(MultiFactor, self).__init__(*args, **kwargs)

    @property
    def plugin_class(self):
        return identity.V3MultiFactor

    def get_options(self):
        options = super(MultiFactor, self).get_options()

        options.extend([
            loading.Opt(
                'auth_methods',
                required=True,
                help="Methods to authenticate with."),
        ])

        if self._methods:
            options_dict = {o.name: o for o in options}
            for method in self._methods:
                method_opts = loading.get_plugin_options(method)
                for opt in method_opts:
                    options_dict[opt.name] = opt
            options = list(options_dict.values())
        return options

    def load_from_options(self, **kwargs):
        _assert_identity_options(kwargs)

        if 'auth_methods' not in kwargs:
            raise exceptions.OptionError("methods is a required option.")

        self._methods = kwargs['auth_methods']

        return super(MultiFactor, self).load_from_options(**kwargs)
