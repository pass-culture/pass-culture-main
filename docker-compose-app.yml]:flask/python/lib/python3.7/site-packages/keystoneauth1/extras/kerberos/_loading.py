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
from keystoneauth1.extras import kerberos
from keystoneauth1 import loading


class Kerberos(loading.BaseV3Loader):

    @property
    def plugin_class(self):
        return kerberos.Kerberos

    @property
    def available(self):
        return kerberos.requests_kerberos is not None

    def get_options(self):
        options = super(Kerberos, self).get_options()

        options.extend([
            loading.Opt('mutual-auth',
                        required=False,
                        default='optional',
                        help='Configures Kerberos Mutual Authentication'),
        ])

        return options

    def load_from_options(self, **kwargs):
        if kwargs.get('mutual_auth'):
            value = kwargs.get('mutual_auth')
            if not (value.lower() in ['required', 'optional', 'disabled']):
                m = ('You need to provide a valid value for kerberos mutual '
                     'authentication. It can be one of the following: '
                     '(required, optional, disabled)')
                raise exceptions.OptionError(m)

        return super(Kerberos, self).load_from_options(**kwargs)


class MappedKerberos(loading.BaseFederationLoader):

    @property
    def plugin_class(self):
        return kerberos.MappedKerberos

    @property
    def available(self):
        return kerberos.requests_kerberos is not None

    def get_options(self):
        options = super(MappedKerberos, self).get_options()

        options.extend([
            loading.Opt('mutual-auth',
                        required=False,
                        default='optional',
                        help='Configures Kerberos Mutual Authentication'),
        ])

        return options

    def load_from_options(self, **kwargs):
        if kwargs.get('mutual_auth'):
            value = kwargs.get('mutual_auth')
            if not (value.lower() in ['required', 'optional', 'disabled']):
                m = ('You need to provide a valid value for kerberos mutual '
                     'authentication. It can be one of the following: '
                     '(required, optional, disabled)')
                raise exceptions.OptionError(m)

        return super(MappedKerberos, self).load_from_options(**kwargs)
