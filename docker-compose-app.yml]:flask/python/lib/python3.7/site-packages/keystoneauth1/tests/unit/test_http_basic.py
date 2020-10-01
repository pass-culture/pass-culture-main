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

from keystoneauth1 import http_basic
from keystoneauth1.loading._plugins import http_basic as loader
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils


class HTTPBasicAuthTest(utils.TestCase):

    TEST_URL = 'http://server/prefix'

    def test_basic_case(self):
        self.requests_mock.get(self.TEST_URL, text='body')

        a = http_basic.HTTPBasicAuth(username='myName', password='myPassword')
        s = session.Session(auth=a)

        data = s.get(self.TEST_URL, authenticated=True)

        self.assertEqual(data.text, 'body')
        self.assertRequestHeaderEqual(
            'Authorization', 'Basic bXlOYW1lOm15UGFzc3dvcmQ=')
        self.assertIsNone(a.get_endpoint(s))

    def test_basic_options(self):
        opts = loader.HTTPBasicAuth().get_options()
        self.assertEqual(['username', 'password', 'endpoint'],
                         [o.name for o in opts])

    def test_get_endpoint(self):
        a = http_basic.HTTPBasicAuth(endpoint=self.TEST_URL)
        s = session.Session(auth=a)
        self.assertEqual(self.TEST_URL, a.get_endpoint(s))

    def test_get_endpoint_with_override(self):
        a = http_basic.HTTPBasicAuth(endpoint=self.TEST_URL)
        s = session.Session(auth=a)
        self.assertEqual('foo', a.get_endpoint(s, endpoint_override='foo'))
