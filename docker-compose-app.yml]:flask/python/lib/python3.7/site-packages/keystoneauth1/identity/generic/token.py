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
from keystoneauth1.identity.generic import base
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3


class Token(base.BaseGenericPlugin):
    """Generic token auth plugin.

    :param string token: Token for authentication.
    """

    def __init__(self, auth_url, token=None, **kwargs):
        super(Token, self).__init__(auth_url, **kwargs)
        self._token = token

    def create_plugin(self, session, version, url, raw_status=None):
        if discover.version_match((2,), version):
            return v2.Token(url, self._token, **self._v2_params)

        elif discover.version_match((3,), version):
            return v3.Token(url, self._token, **self._v3_params)

    def get_cache_id_elements(self):
        elements = super(Token, self).get_cache_id_elements(_implemented=True)
        elements['token'] = self._token
        return elements
