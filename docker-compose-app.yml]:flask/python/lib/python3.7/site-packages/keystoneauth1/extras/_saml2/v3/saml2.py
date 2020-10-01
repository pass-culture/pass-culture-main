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

try:
    from lxml import etree
except ImportError:
    etree = None

import requests
import requests.auth

from keystoneauth1 import access
from keystoneauth1 import exceptions
from keystoneauth1.identity import v3

_PAOS_NAMESPACE = 'urn:liberty:paos:2003-08'
_ECP_NAMESPACE = 'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp'
_PAOS_HEADER = 'application/vnd.paos+xml'

_PAOS_VER = 'ver="%s";"%s"' % (_PAOS_NAMESPACE, _ECP_NAMESPACE)

_XML_NAMESPACES = {
    'ecp': _ECP_NAMESPACE,
    'S': 'http://schemas.xmlsoap.org/soap/envelope/',
    'paos': _PAOS_NAMESPACE,
}

_XBASE = '/S:Envelope/S:Header/'

_XPATH_SP_RELAY_STATE = '//ecp:RelayState'
_XPATH_SP_CONSUMER_URL = _XBASE + 'paos:Request/@responseConsumerURL'
_XPATH_IDP_CONSUMER_URL = _XBASE + 'ecp:Response/@AssertionConsumerServiceURL'

_SOAP_FAULT = """
    <S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
       <S:Body>
         <S:Fault>
            <faultcode>S:Server</faultcode>
            <faultstring>responseConsumerURL from SP and
            assertionConsumerServiceURL from IdP do not match
            </faultstring>
         </S:Fault>
       </S:Body>
    </S:Envelope>
"""


class SamlException(Exception):
    """Base SAML plugin exception."""


class InvalidResponse(SamlException):
    """Invalid Response from SAML authentication."""


class ConsumerMismatch(SamlException):
    """The SP and IDP consumers do not match."""


def _response_xml(response, name):
    try:
        return etree.XML(response.content)
    except etree.XMLSyntaxError as e:
        msg = 'SAML2: Error parsing XML returned from %s: %s' % (name, e)
        raise InvalidResponse(msg)


def _str_from_xml(xml, path):
    li = xml.xpath(path, namespaces=_XML_NAMESPACES)
    if len(li) != 1:
        raise IndexError('%s should provide a single element list' % path)
    return li[0]


class _SamlAuth(requests.auth.AuthBase):
    """A generic SAML ECP plugin for requests.

    This is a multi-step process including multiple HTTP requests.
    Authentication consists of:

    * HTTP GET request to the Service Provider.

        It's crucial to include HTTP headers indicating we are expecting SOAP
        message in return. Service Provider should respond with a SOAP
        message.

    * HTTP POST request to the external Identity Provider service with
        ECP extension enabled. The content sent is a header removed SOAP
        message returned from the Service Provider. It's also worth noting
        that ECP extension to the SAML2 doesn't define authentication method.
        The most popular is HttpBasicAuth with just user and password.
        Other possibilities could be X509 certificates or Kerberos.
        Upon successful authentication the user should receive a SAML2
        assertion.

    * HTTP POST request again to the Service Provider. The body of the
        request includes SAML2 assertion issued by a trusted Identity
        Provider. The request should be sent to the Service Provider
        consumer url specified in the SAML2 assertion.
        Providing the authentication was successful and both Service Provider
        and Identity Providers are trusted to each other, the Service
        Provider will issue an unscoped token with a list of groups the
        federated user is a member of.
    """

    def __init__(self, identity_provider_url, requests_auth):
        super(_SamlAuth, self).__init__()
        self.identity_provider_url = identity_provider_url
        self.requests_auth = requests_auth

    def __call__(self, request):
        try:
            accept = request.headers['Accept']
        except KeyError:
            request.headers['Accept'] = _PAOS_HEADER
        else:
            request.headers['Accept'] = ','.join([accept, _PAOS_HEADER])

        request.headers['PAOS'] = _PAOS_VER
        request.register_hook('response', self._handle_response)
        return request

    def _handle_response(self, response, **kwargs):
        if (response.status_code == 200 and
                response.headers.get('Content-Type') == _PAOS_HEADER):
            response = self._ecp_retry(response, **kwargs)

        return response

    def _ecp_retry(self, sp_response, **kwargs):
        history = [sp_response]

        def send(*send_args, **send_kwargs):
            req = requests.Request(*send_args, **send_kwargs)
            return sp_response.connection.send(req.prepare(), **kwargs)

        authn_request = _response_xml(sp_response, 'Service Provider')
        relay_state = _str_from_xml(authn_request, _XPATH_SP_RELAY_STATE)
        sp_consumer_url = _str_from_xml(authn_request, _XPATH_SP_CONSUMER_URL)

        authn_request.remove(authn_request[0])

        idp_response = send('POST',
                            self.identity_provider_url,
                            headers={'Content-type': 'text/xml'},
                            data=etree.tostring(authn_request),
                            auth=self.requests_auth)
        history.append(idp_response)

        authn_response = _response_xml(idp_response, 'Identity Provider')
        idp_consumer_url = _str_from_xml(authn_response,
                                         _XPATH_IDP_CONSUMER_URL)

        if sp_consumer_url != idp_consumer_url:
            # send fault message to the SP, discard the response
            send('POST',
                 sp_consumer_url,
                 data=_SOAP_FAULT,
                 headers={'Content-Type': _PAOS_HEADER})

            # prepare error message and raise an exception.
            msg = ('Consumer URLs from Service Provider %(service_provider)s '
                   '%(sp_consumer_url)s and Identity Provider '
                   '%(identity_provider)s %(idp_consumer_url)s are not equal')
            msg = msg % {
                'service_provider': sp_response.request.url,
                'sp_consumer_url': sp_consumer_url,
                'identity_provider': self.identity_provider_url,
                'idp_consumer_url': idp_consumer_url
            }

            raise ConsumerMismatch(msg)

        authn_response[0][0] = relay_state

        # idp_consumer_url is the URL on the SP that handles the ECP body
        # returned and creates an authenticated session.
        final_resp = send('POST',
                          idp_consumer_url,
                          headers={'Content-Type': _PAOS_HEADER},
                          cookies=idp_response.cookies,
                          data=etree.tostring(authn_response))

        history.append(final_resp)

        # the SP should then redirect us back to the original URL to retry the
        # original request.
        if final_resp.status_code in (requests.codes.found,
                                      requests.codes.other):

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            sp_response.content
            sp_response.raw.release_conn()

            req = sp_response.request.copy()
            req.url = final_resp.headers['location']
            req.prepare_cookies(final_resp.cookies)

            final_resp = sp_response.connection.send(req, **kwargs)
            history.append(final_resp)

        final_resp.history.extend(history)
        return final_resp


class _FederatedSaml(v3.FederationBaseAuth):

    def __init__(self, auth_url, identity_provider, protocol,
                 identity_provider_url, **kwargs):
        super(_FederatedSaml, self).__init__(auth_url,
                                             identity_provider,
                                             protocol,
                                             **kwargs)
        self.identity_provider_url = identity_provider_url

    @abc.abstractmethod
    def get_requests_auth(self):
        raise NotImplementedError()

    def get_unscoped_auth_ref(self, session, **kwargs):
        method = self.get_requests_auth()
        auth = _SamlAuth(self.identity_provider_url, method)

        try:
            resp = session.get(self.federated_token_url,
                               requests_auth=auth,
                               authenticated=False)
        except SamlException as e:
            raise exceptions.AuthorizationFailure(str(e))

        return access.create(resp=resp)


class Password(_FederatedSaml):
    r"""Implement authentication plugin for SAML2 protocol.

    ECP stands for `Enhanced Client or Proxy` and is a SAML2 extension
    for federated authentication where a transportation layer consists of
    HTTP protocol and XML SOAP messages.

    `Read for more information
    <https://wiki.shibboleth.net/confluence/display/CONCEPT/ECP>`_ on ECP.

    Reference the `SAML2 ECP specification <https://www.oasis-open.org/\
    committees/download.php/49979/saml-ecp-v2.0-wd09.pdf>`_.

    Currently only HTTPBasicAuth mechanism is available for the IdP
    authenication.

    :param auth_url: URL of the Identity Service
    :type auth_url: string

    :param identity_provider: name of the Identity Provider the client will
                              authenticate against. This parameter will be used
                              to build a dynamic URL used to obtain unscoped
                              OpenStack token.
    :type identity_provider: string

    :param identity_provider_url: An Identity Provider URL, where the SAML2
                                  authn request will be sent.
    :type identity_provider_url: string

    :param username: User's login
    :type username: string

    :param password: User's password
    :type password: string

    :param protocol: Protocol to be used for the authentication.
                     The name must be equal to one configured at the
                     keystone sp side. This value is used for building
                     dynamic authentication URL.
                     Typical value  would be: saml2
    :type protocol: string

    """

    def __init__(self, auth_url, identity_provider, protocol,
                 identity_provider_url, username, password, **kwargs):
        super(Password, self).__init__(auth_url,
                                       identity_provider,
                                       protocol,
                                       identity_provider_url,
                                       **kwargs)
        self.username = username
        self.password = password

    def get_requests_auth(self):
        return requests.auth.HTTPBasicAuth(self.username, self.password)
