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

from keystoneauth1 import loading
from keystoneauth1.tests.unit import utils as test_utils


class OAuth1LoadingTests(test_utils.TestCase):

    def setUp(self):
        super(OAuth1LoadingTests, self).setUp()
        self.auth_url = uuid.uuid4().hex

    def create(self, **kwargs):
        kwargs.setdefault('auth_url', self.auth_url)
        loader = loading.get_plugin_loader('v3oauth1')
        return loader.load_from_options(**kwargs)

    def test_basic(self):
        access_key = uuid.uuid4().hex
        access_secret = uuid.uuid4().hex
        consumer_key = uuid.uuid4().hex
        consumer_secret = uuid.uuid4().hex

        p = self.create(access_key=access_key,
                        access_secret=access_secret,
                        consumer_key=consumer_key,
                        consumer_secret=consumer_secret)

        oauth_method = p.auth_methods[0]

        self.assertEqual(self.auth_url, p.auth_url)
        self.assertEqual(access_key, oauth_method.access_key)
        self.assertEqual(access_secret, oauth_method.access_secret)
        self.assertEqual(consumer_key, oauth_method.consumer_key)
        self.assertEqual(consumer_secret, oauth_method.consumer_secret)

    def test_options(self):
        options = loading.get_plugin_loader('v3oauth1').get_options()

        self.assertEqual(set([o.name for o in options]),
                         set(['auth-url',
                              'access-key',
                              'access-secret',
                              'consumer-key',
                              'consumer-secret']))
