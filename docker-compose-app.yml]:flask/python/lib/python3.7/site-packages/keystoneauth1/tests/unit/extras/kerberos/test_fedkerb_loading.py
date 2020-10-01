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
from keystoneauth1 import loading
from keystoneauth1.tests.unit import utils as test_utils


class FedKerbLoadingTests(test_utils.TestCase):

    def test_options(self):
        opts = [o.name for o in
                loading.get_plugin_loader('v3fedkerb').get_options()]

        allowed_opts = ['system-scope',
                        'domain-id',
                        'domain-name',
                        'identity-provider',
                        'project-id',
                        'project-name',
                        'project-domain-id',
                        'project-domain-name',
                        'protocol',
                        'trust-id',
                        'auth-url',
                        'mutual-auth',
                        ]

        self.assertCountEqual(allowed_opts, opts)

    def create(self, **kwargs):
        loader = loading.get_plugin_loader('v3fedkerb')
        return loader.load_from_options(**kwargs)

    def test_load_none(self):
        self.assertRaises(exceptions.MissingRequiredOptions, self.create)

    def test_load(self):
        self.create(auth_url='auth_url',
                    identity_provider='idp',
                    protocol='protocol')
