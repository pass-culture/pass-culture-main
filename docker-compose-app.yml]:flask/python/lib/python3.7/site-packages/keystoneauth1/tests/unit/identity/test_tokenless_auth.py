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

from keystoneauth1 import exceptions
from keystoneauth1.identity.v3 import tokenless_auth
from keystoneauth1 import session
from keystoneauth1.tests.unit import utils


class TokenlessAuthTest(utils.TestCase):

    TEST_URL = 'http://server/prefix'

    def create(self, auth_url,
               domain_id=None,
               domain_name=None,
               project_id=None,
               project_name=None,
               project_domain_id=None,
               project_domain_name=None):
        self.requests_mock.get(self.TEST_URL)
        auth = tokenless_auth.TokenlessAuth(
            auth_url=self.TEST_URL,
            domain_id=domain_id,
            domain_name=domain_name,
            project_id=project_id,
            project_name=project_name,
            project_domain_id=project_domain_id,
            project_domain_name=project_domain_name)
        return auth, session.Session(auth=auth)

    def test_domain_id_scope_header_pass(self):
        domain_id = uuid.uuid4().hex
        auth, session = self.create(auth_url=self.TEST_URL,
                                    domain_id=domain_id)
        session.get(self.TEST_URL, authenticated=True)
        self.assertRequestHeaderEqual('X-Domain-Id', domain_id)

    def test_domain_name_scope_header_pass(self):
        domain_name = uuid.uuid4().hex
        auth, session = self.create(auth_url=self.TEST_URL,
                                    domain_name=domain_name)
        session.get(self.TEST_URL, authenticated=True)
        self.assertRequestHeaderEqual('X-Domain-Name', domain_name)

    def test_project_id_scope_header_pass(self):
        project_id = uuid.uuid4().hex
        auth, session = self.create(auth_url=self.TEST_URL,
                                    project_id=project_id)
        session.get(self.TEST_URL, authenticated=True)
        self.assertRequestHeaderEqual('X-Project-Id', project_id)

    def test_project_of_domain_id_scope_header_pass(self):
        project_name = uuid.uuid4().hex
        project_domain_id = uuid.uuid4().hex
        auth, session = self.create(auth_url=self.TEST_URL,
                                    project_name=project_name,
                                    project_domain_id=project_domain_id)
        session.get(self.TEST_URL, authenticated=True)
        self.assertRequestHeaderEqual('X-Project-Name', project_name)
        self.assertRequestHeaderEqual('X-Project-Domain-Id', project_domain_id)

    def test_project_of_domain__name_scope_header_pass(self):
        project_name = uuid.uuid4().hex
        project_domain_name = uuid.uuid4().hex
        auth, session = self.create(auth_url=self.TEST_URL,
                                    project_name=project_name,
                                    project_domain_name=project_domain_name)
        session.get(self.TEST_URL, authenticated=True)
        self.assertRequestHeaderEqual('X-Project-Name', project_name)
        self.assertRequestHeaderEqual('X-Project-Domain-Name',
                                      project_domain_name)

    def test_no_scope_header_fail(self):
        auth, session = self.create(auth_url=self.TEST_URL)
        self.assertIsNone(auth.get_headers(session))
        msg = 'No valid authentication is available'
        self.assertRaisesRegex(exceptions.AuthorizationFailure,
                               msg,
                               session.get,
                               self.TEST_URL,
                               authenticated=True)

    def test_project_name_scope_only_header_fail(self):
        project_name = uuid.uuid4().hex
        auth, session = self.create(auth_url=self.TEST_URL,
                                    project_name=project_name)
        self.assertIsNone(auth.get_headers(session))
        msg = 'No valid authentication is available'
        self.assertRaisesRegex(exceptions.AuthorizationFailure,
                               msg,
                               session.get,
                               self.TEST_URL,
                               authenticated=True)
