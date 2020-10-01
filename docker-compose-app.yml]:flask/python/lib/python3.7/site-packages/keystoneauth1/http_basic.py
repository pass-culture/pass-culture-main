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

import base64

from keystoneauth1 import plugin

AUTH_HEADER_NAME = 'Authorization'


class HTTPBasicAuth(plugin.FixedEndpointPlugin):
    """A provider that will always use HTTP Basic authentication.

    This is useful to unify session/adapter loading for services
    that might be deployed in standalone mode.
    """

    def __init__(self, endpoint=None, username=None, password=None):
        super(HTTPBasicAuth, self).__init__(endpoint)
        self.username = username
        self.password = password

    def get_token(self, session, **kwargs):
        if self.username is None or self.password is None:
            return None
        token = bytes('%s:%s' % (self.username, self.password),
                      encoding='utf-8')
        encoded = base64.b64encode(token)
        return str(encoded, encoding='utf-8')

    def get_headers(self, session, **kwargs):
        token = self.get_token(session)
        if not token:
            return None
        auth = 'Basic %s' % token
        return {AUTH_HEADER_NAME: auth}
