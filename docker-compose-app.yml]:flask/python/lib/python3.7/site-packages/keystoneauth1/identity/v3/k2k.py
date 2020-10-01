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

import six

from keystoneauth1 import access
from keystoneauth1 import exceptions
from keystoneauth1.identity.v3 import federation
from keystoneauth1 import plugin

__all__ = ('Keystone2Keystone',)


class Keystone2Keystone(federation._Rescoped):
    """Plugin to execute the Keystone to Keyestone authentication flow.

    In this plugin, an ECP wrapped SAML assertion provided by a keystone
    Identity Provider (IdP) is used to request an OpenStack unscoped token
    from a keystone Service Provider (SP).

    :param base_plugin: Auth plugin already authenticated against the keystone
                        IdP.
    :type base_plugin: keystoneauth1.identity.v3.base.BaseAuth

    :param service_provider: The Service Provider ID as returned by
                             ServiceProviderManager.list()
    :type service_provider: str

    """

    REQUEST_ECP_URL = '/auth/OS-FEDERATION/saml2/ecp'
    """Path where the ECP wrapped SAML assertion should be presented to the
       Keystone Service Provider."""

    HTTP_MOVED_TEMPORARILY = 302
    HTTP_SEE_OTHER = 303

    def __init__(self, base_plugin, service_provider, **kwargs):
        super(Keystone2Keystone, self).__init__(auth_url=None, **kwargs)

        self._local_cloud_plugin = base_plugin
        self._sp_id = service_provider

    @classmethod
    def _remote_auth_url(cls, auth_url):
        """Return auth_url of the remote Keystone Service Provider.

        Remote cloud's auth_url is an endpoint for getting federated unscoped
        token, typically that would be
        ``https://remote.example.com:5000/v3/OS-FEDERATION/identity_providers/
        <idp>/protocols/<protocol_id>/auth``. However we need to generate a
        real auth_url, used for token scoping.  This function assumes there are
        static values today in the remote auth_url stored in the Service
        Provider attribute and those can be used as a delimiter. If the
        sp_auth_url doesn't comply with standard federation auth url the
        function will simply return whole string.

        :param auth_url: auth_url of the remote cloud
        :type auth_url: str

        :returns: auth_url of remote cloud where a token can be validated or
                  scoped.
        :rtype: str

        """
        PATTERN = '/OS-FEDERATION/'
        idx = auth_url.index(PATTERN) if PATTERN in auth_url else len(auth_url)
        return auth_url[:idx]

    def _get_ecp_assertion(self, session):
        body = {
            'auth': {
                'identity': {
                    'methods': ['token'],
                    'token': {
                        'id': self._local_cloud_plugin.get_token(session)
                    }
                },
                'scope': {
                    'service_provider': {
                        'id': self._sp_id
                    }
                }
            }
        }

        endpoint_filter = {'version': (3, 0),
                           'interface': plugin.AUTH_INTERFACE}

        headers = {'Accept': 'application/json'}

        resp = session.post(self.REQUEST_ECP_URL,
                            json=body,
                            auth=self._local_cloud_plugin,
                            endpoint_filter=endpoint_filter,
                            headers=headers,
                            authenticated=False,
                            raise_exc=False)

        # NOTE(marek-denis): I am not sure whether disabling exceptions in the
        # Session object and testing if resp.ok is sufficient. An alternative
        # would be catching locally all exceptions and reraising with custom
        # warning.
        if not resp.ok:
            msg = ("Error while requesting ECP wrapped assertion: response "
                   "exit code: %(status_code)d, reason: %(err)s")
            msg = msg % {'status_code': resp.status_code, 'err': resp.reason}
            raise exceptions.AuthorizationFailure(msg)

        if not resp.text:
            raise exceptions.InvalidResponse(resp)

        return six.text_type(resp.text)

    def _send_service_provider_ecp_authn_response(self, session, sp_url,
                                                  sp_auth_url):
        """Present ECP wrapped SAML assertion to the keystone SP.

        The assertion is issued by the keystone IdP and it is targeted to the
        keystone that will serve as Service Provider.

        :param session: a session object to send out HTTP requests.

        :param sp_url: URL where the ECP wrapped SAML assertion will be
                       presented to the keystone SP. Usually, something like:
                       https://sp.com/Shibboleth.sso/SAML2/ECP
        :type sp_url: str

        :param sp_auth_url: Federated authentication URL of the keystone SP.
                            It is specified by IdP, for example:
                            https://sp.com/v3/OS-FEDERATION/identity_providers/
                            idp_id/protocols/protocol_id/auth
        :type sp_auth_url: str

        """
        response = session.post(
            sp_url,
            headers={'Content-Type': 'application/vnd.paos+xml'},
            data=self._get_ecp_assertion(session),
            authenticated=False,
            redirect=False)

        # Don't follow HTTP specs - after the HTTP 302/303 response don't
        # repeat the call directed to the Location URL. In this case, this is
        # an indication that SAML2 session is now active and protected resource
        # can be accessed.
        if response.status_code in (self.HTTP_MOVED_TEMPORARILY,
                                    self.HTTP_SEE_OTHER):
            response = session.get(
                sp_auth_url,
                headers={'Content-Type': 'application/vnd.paos+xml'},
                authenticated=False)

        return response

    def get_unscoped_auth_ref(self, session, **kwargs):
        sp_auth_url = self._local_cloud_plugin.get_sp_auth_url(
            session, self._sp_id)
        sp_url = self._local_cloud_plugin.get_sp_url(session, self._sp_id)
        self.auth_url = self._remote_auth_url(sp_auth_url)

        response = self._send_service_provider_ecp_authn_response(
            session, sp_url, sp_auth_url)
        return access.create(resp=response)
