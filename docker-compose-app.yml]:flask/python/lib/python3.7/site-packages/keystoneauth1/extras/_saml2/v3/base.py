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

try:
    from lxml import etree
except ImportError:
    etree = None

from keystoneauth1 import exceptions
from keystoneauth1.identity import v3


class _Saml2TokenAuthMethod(v3.AuthMethod):
    _method_parameters = []

    def get_auth_data(self, session, auth, headers, **kwargs):
        raise exceptions.MethodNotImplemented('This method should never '
                                              'be called')


class BaseSAMLPlugin(v3.FederationBaseAuth):

    HTTP_MOVED_TEMPORARILY = 302
    HTTP_SEE_OTHER = 303

    _auth_method_class = _Saml2TokenAuthMethod

    def __init__(self, auth_url,
                 identity_provider, identity_provider_url,
                 username, password, protocol,
                 **kwargs):
        """Class constructor accepting following parameters.

        :param auth_url: URL of the Identity Service
        :type auth_url: string

        :param identity_provider: Name of the Identity Provider the client
                                  will authenticate against. This parameter
                                  will be used to build a dynamic URL used to
                                  obtain unscoped OpenStack token.
        :type identity_provider: string

        :param identity_provider_url: An Identity Provider URL, where the
                                      SAML2 auhentication request will be
                                      sent.
        :type identity_provider_url: string

        :param username: User's login
        :type username: string

        :param password: User's password
        :type password: string

        :param protocol: Protocol to be used for the authentication.
                         The name must be equal to one configured at the
                         keystone sp side. This value is used for building
                         dynamic authentication URL.
                         Typical value would be: saml2
        :type protocol: string

        """
        super(BaseSAMLPlugin, self).__init__(
            auth_url=auth_url, identity_provider=identity_provider,
            protocol=protocol,
            **kwargs)
        self.identity_provider_url = identity_provider_url
        self.username = username
        self.password = password

    @staticmethod
    def _first(_list):
        if len(_list) != 1:
            raise IndexError('Only single element list is acceptable')
        return _list[0]

    @staticmethod
    def str_to_xml(content, msg=None, include_exc=True):
        try:
            return etree.XML(content)
        except etree.XMLSyntaxError as e:
            if not msg:
                msg = str(e)
            else:
                msg = msg % e if include_exc else msg
            raise exceptions.AuthorizationFailure(msg)

    @staticmethod
    def xml_to_str(content, **kwargs):
        return etree.tostring(content, **kwargs)
