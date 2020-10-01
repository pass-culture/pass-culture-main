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
test_builtin
------------

Tests for `ServiceTypes` class builtin data.

oslotest sets up a TempHomeDir for us, so there should be no ~/.cache files
available in these tests.
"""
from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

import os_service_types
from os_service_types.tests import base


class TestBuiltin(base.TestCase, base.ServiceDataMixin):

    def setUp(self):
        super(TestBuiltin, self).setUp()
        # Make an object with no network access
        self.service_types = os_service_types.ServiceTypes()

    def test_builtin_version(self):
        self.assertEqual(self.builtin_version, self.service_types.version)
