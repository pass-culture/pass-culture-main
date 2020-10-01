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

from keystoneauth1.identity.v3 import base


__all__ = ('ReceiptMethod', )


class ReceiptMethod(base.AuthMethod):
    """Construct an Auth plugin to continue authentication with a receipt.

    :param string receipt: Receipt for authentication.
    """

    _method_parameters = ['receipt']

    def get_auth_data(self, session, auth, headers, **kwargs):
        """Add the auth receipt to the headers.

        We explicitly return None to avoid being added to the request
        methods, or body.
        """
        headers['Openstack-Auth-Receipt'] = self.receipt
        return (None, None)

    def get_cache_id_elements(self):
        return {'receipt_receipt': self.receipt}
