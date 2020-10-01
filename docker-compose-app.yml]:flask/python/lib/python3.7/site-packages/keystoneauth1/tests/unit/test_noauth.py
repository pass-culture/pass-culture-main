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

from keystoneauth1.loading._plugins import noauth as loader
from keystoneauth1 import noauth
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils


class NoAuthTest(utils.TestCase):

    NOAUTH_TOKEN = 'notused'
    TEST_URL = 'http://server/prefix'

    def test_basic_case(self):
        self.requests_mock.get(self.TEST_URL, text='body')

        a = noauth.NoAuth()
        s = session.Session(auth=a)

        data = s.get(self.TEST_URL, authenticated=True)

        self.assertEqual(data.text, 'body')
        self.assertRequestHeaderEqual('X-Auth-Token', self.NOAUTH_TOKEN)
        self.assertIsNone(a.get_endpoint(s))

    def test_noauth_options(self):
        opts = loader.NoAuth().get_options()
        self.assertEqual(['endpoint'], [o.name for o in opts])

    def test_get_endpoint(self):
        a = noauth.NoAuth(endpoint=self.TEST_URL)
        s = session.Session(auth=a)
        self.assertEqual(self.TEST_URL, a.get_endpoint(s))

    def test_get_endpoint_with_override(self):
        a = noauth.NoAuth(endpoint=self.TEST_URL)
        s = session.Session(auth=a)
        self.assertEqual('foo', a.get_endpoint(s, endpoint_override='foo'))
