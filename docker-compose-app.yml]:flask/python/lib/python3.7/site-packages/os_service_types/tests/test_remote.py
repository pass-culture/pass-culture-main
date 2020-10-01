# -*- coding: utf-8 -*-

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

"""
test_remote
-----------

Tests for `ServiceTypes` class remote data.

oslotest sets up a TempHomeDir for us, so there should be no ~/.cache files
available in these tests.
"""
from requests_mock.contrib import fixture as rm_fixture
from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

import keystoneauth1.session

import os_service_types
import os_service_types.service_types
from os_service_types.tests import base


class TestRemote(base.TestCase, base.ServiceDataMixin):

    def setUp(self):
        super(TestRemote, self).setUp()
        # Set up a requests_mock fixture for all HTTP traffic
        adapter = self.useFixture(rm_fixture.Fixture())
        adapter.register_uri(
            'GET', os_service_types.service_types.SERVICE_TYPES_URL,
            json=self.remote_content,
            headers={'etag': self.getUniqueString('etag')})
        # use keystoneauth1 to get a Sessiom with no auth information
        self.session = keystoneauth1.session.Session()
        # Make an object that fetches from the network
        self.service_types = os_service_types.ServiceTypes(
            session=self.session)
        self.assertEqual(1, len(adapter.request_history))

    def test_remote_version(self):
        self.assertEqual(self.remote_version, self.service_types.version)
