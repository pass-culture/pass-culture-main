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

from keystoneauth1.extras import _saml2
from keystoneauth1 import loading


class Saml2Password(loading.BaseFederationLoader):

    @property
    def plugin_class(self):
        return _saml2.V3Saml2Password

    @property
    def available(self):
        return _saml2._V3_SAML2_AVAILABLE

    def get_options(self):
        options = super(Saml2Password, self).get_options()

        options.extend([
            loading.Opt('identity-provider-url',
                        required=True,
                        help=('An Identity Provider URL, where the SAML2 '
                              'authentication request will be sent.')),
            loading.Opt('username', help='Username', required=True),
            loading.Opt('password',
                        secret=True,
                        help='Password',
                        required=True)
        ])

        return options


class ADFSPassword(loading.BaseFederationLoader):

    @property
    def plugin_class(self):
        return _saml2.V3ADFSPassword

    @property
    def available(self):
        return _saml2._V3_ADFS_AVAILABLE

    def get_options(self):
        options = super(ADFSPassword, self).get_options()

        options.extend([
            loading.Opt('identity-provider-url',
                        required=True,
                        help=('An Identity Provider URL, where the SAML '
                              'authentication request will be sent.')),
            loading.Opt('service-provider-endpoint',
                        required=True,
                        help="Service Provider's Endpoint"),
            loading.Opt('service-provider-entity-id',
                        required=True,
                        help="Service Provider's SAML Entity ID"),
            loading.Opt('username', help='Username', required=True),
            loading.Opt('password',
                        secret=True,
                        required=True,
                        help='Password')
        ])

        return options
