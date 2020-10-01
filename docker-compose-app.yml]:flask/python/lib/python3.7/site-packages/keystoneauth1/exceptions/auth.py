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

from keystoneauth1 import _utils as utils
from keystoneauth1.exceptions import base


class AuthorizationFailure(base.ClientException):
    message = "Cannot authorize API client."


class MissingAuthMethods(base.ClientException):
    message = "Not all required auth rules were satisfied"

    def __init__(self, response):
        self.response = response
        self.receipt = response.headers.get("Openstack-Auth-Receipt")
        body = response.json()
        self.methods = body['receipt']['methods']
        self.required_auth_methods = body['required_auth_methods']
        self.expires_at = utils.parse_isotime(body['receipt']['expires_at'])
        message = "%s: %s" % (self.message, self.required_auth_methods)
        super(MissingAuthMethods, self).__init__(message)
