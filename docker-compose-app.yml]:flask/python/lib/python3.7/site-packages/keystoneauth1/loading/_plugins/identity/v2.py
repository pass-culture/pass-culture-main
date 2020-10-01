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

from keystoneauth1 import identity
from keystoneauth1 import loading


class Token(loading.BaseV2Loader):

    @property
    def plugin_class(self):
        return identity.V2Token

    def get_options(self):
        options = super(Token, self).get_options()

        options.extend([
            loading.Opt('token', secret=True, help='Token'),
        ])

        return options


class Password(loading.BaseV2Loader):

    @property
    def plugin_class(self):
        return identity.V2Password

    def get_options(self):
        options = super(Password, self).get_options()

        options.extend([
            loading.Opt('username',
                       deprecated=[loading.Opt('user-name')],
                       help='Username to login with'),
            loading.Opt('user-id', help='User ID to login with'),
            loading.Opt('password',
                        secret=True,
                        prompt='Password: ',
                        help='Password to use'),
        ])

        return options
