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

from keystoneauth1 import fixture
from keystoneauth1 import identity
from keystoneauth1 import service_token
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils


class ServiceTokenTests(utils.TestCase):

    TEST_URL = 'http://test.example.com/path/'
    USER_URL = 'http://user-keystone.example.com/v3'
    SERVICE_URL = 'http://service-keystone.example.com/v3'

    def setUp(self):
        super(ServiceTokenTests, self).setUp()

        self.user_token_id = uuid.uuid4().hex
        self.user_token = fixture.V3Token()
        self.user_token.set_project_scope()
        self.user_auth = identity.V3Password(auth_url=self.USER_URL,
                                             user_id=uuid.uuid4().hex,
                                             password=uuid.uuid4().hex,
                                             project_id=uuid.uuid4().hex)

        self.service_token_id = uuid.uuid4().hex
        self.service_token = fixture.V3Token()
        self.service_token.set_project_scope()
        self.service_auth = identity.V3Password(auth_url=self.SERVICE_URL,
                                                user_id=uuid.uuid4().hex,
                                                password=uuid.uuid4().hex,
                                                project_id=uuid.uuid4().hex)

        for t in (self.user_token, self.service_token):
            s = t.add_service('identity')
            s.add_standard_endpoints(public='http://keystone.example.com',
                                     admin='http://keystone.example.com',
                                     internal='http://keystone.example.com')

        self.test_data = {'data': uuid.uuid4().hex}

        self.user_mock = self.requests_mock.post(
            self.USER_URL + '/auth/tokens',
            json=self.user_token,
            headers={'X-Subject-Token': self.user_token_id})

        self.service_mock = self.requests_mock.post(
            self.SERVICE_URL + '/auth/tokens',
            json=self.service_token,
            headers={'X-Subject-Token': self.service_token_id})

        self.requests_mock.get(self.TEST_URL, json=self.test_data)

        self.combined_auth = service_token.ServiceTokenAuthWrapper(
            self.user_auth,
            self.service_auth)

        self.session = session.Session(auth=self.combined_auth)

    def test_setting_service_token(self):
        self.session.get(self.TEST_URL)

        headers = self.requests_mock.last_request.headers

        self.assertEqual(self.user_token_id, headers['X-Auth-Token'])
        self.assertEqual(self.service_token_id, headers['X-Service-Token'])

        self.assertTrue(self.user_mock.called_once)
        self.assertTrue(self.service_mock.called_once)

    def test_invalidation(self):
        text = uuid.uuid4().hex
        test_url = 'http://test.example.com/abc'

        response_list = [{'status_code': 401}, {'text': text}]
        mock = self.requests_mock.get(test_url, response_list=response_list)

        resp = self.session.get(test_url)
        self.assertEqual(text, resp.text)

        self.assertEqual(2, mock.call_count)
        self.assertEqual(2, self.user_mock.call_count)
        self.assertEqual(2, self.service_mock.call_count)

    def test_pass_throughs(self):
        self.assertEqual(self.user_auth.get_token(self.session),
                         self.combined_auth.get_token(self.session))

        self.assertEqual(
            self.user_auth.get_endpoint(self.session, 'identity'),
            self.combined_auth.get_endpoint(self.session, 'identity'))

        self.assertEqual(self.user_auth.get_user_id(self.session),
                         self.combined_auth.get_user_id(self.session))

        self.assertEqual(self.user_auth.get_project_id(self.session),
                         self.combined_auth.get_project_id(self.session))

        self.assertEqual(self.user_auth.get_sp_auth_url(self.session, 'a'),
                         self.combined_auth.get_sp_auth_url(self.session, 'a'))

        self.assertEqual(self.user_auth.get_sp_url(self.session, 'a'),
                         self.combined_auth.get_sp_url(self.session, 'a'))
