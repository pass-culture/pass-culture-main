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

import uuid

from keystoneauth1.identity.generic import token
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1.identity.v3 import token as v3_token
from keystoneauth1.tests.unit.identity import utils


class TokenTests(utils.GenericPluginTestCase):

    PLUGIN_CLASS = token.Token
    V2_PLUGIN_CLASS = v2.Token
    V3_PLUGIN_CLASS = v3.Token

    def new_plugin(self, **kwargs):
        kwargs.setdefault('token', uuid.uuid4().hex)
        return super(TokenTests, self).new_plugin(**kwargs)

    def test_symbols(self):
        self.assertIs(v3.Token, v3_token.Token)
        self.assertIs(v3.TokenMethod, v3_token.TokenMethod)

    def test_token_cache_id(self):
        the_token = uuid.uuid4().hex
        project_name = uuid.uuid4().hex
        default_domain_id = uuid.uuid4().hex

        a = token.Token(self.TEST_URL,
                        token=the_token,
                        project_name=project_name,
                        default_domain_id=default_domain_id)

        b = token.Token(self.TEST_URL,
                        token=the_token,
                        project_name=project_name,
                        default_domain_id=default_domain_id)

        a_id = a.get_cache_id()
        b_id = b.get_cache_id()

        self.assertEqual(a_id, b_id)

        c = token.Token(self.TEST_URL,
                        token=the_token,
                        project_name=uuid.uuid4().hex,  # different
                        default_domain_id=default_domain_id)

        c_id = c.get_cache_id()

        self.assertNotEqual(a_id, c_id)
