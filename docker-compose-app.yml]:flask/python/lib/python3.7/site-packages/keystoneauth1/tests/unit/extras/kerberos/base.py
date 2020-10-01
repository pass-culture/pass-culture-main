# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
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

from keystoneauth1.tests.unit.extras.kerberos import utils
from keystoneauth1.tests.unit import utils as test_utils


REQUEST = {'auth': {'identity': {'methods': ['kerberos'],
                                 'kerberos': {}}}}


class TestCase(test_utils.TestCase):
    """Test case base class for Kerberos unit tests."""

    TEST_V3_URL = test_utils.TestCase.TEST_ROOT_URL + 'v3'

    def setUp(self):
        super(TestCase, self).setUp()

        km = utils.KerberosMock(self.requests_mock)
        self.kerberos_mock = self.useFixture(km)

    def assertRequestBody(self, body=None):
        """Ensure the request body is the standard Kerberos auth request.

        :param dict body: the body to compare. If not provided the last request
                          body will be used.
        """
        if not body:
            body = self.requests_mock.last_request.json()

        self.assertEqual(REQUEST, body)
