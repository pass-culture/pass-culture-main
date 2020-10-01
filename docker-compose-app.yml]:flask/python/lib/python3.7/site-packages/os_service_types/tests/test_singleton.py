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
test_singleton
------------

Tests for `get_service_types` singleton factory function.
"""
import os_service_types
from os_service_types.tests import base


class TestSingleton(base.TestCase):

    def setUp(self):
        super(TestSingleton, self).setUp()
        # Make an object with no network access
        self.service_types = os_service_types.get_service_types()

    def test_singleton_same(self):
        service_types = os_service_types.get_service_types()
        self.assertTrue(service_types is self.service_types)

    def test_singleton_different(self):
        service_types = os_service_types.ServiceTypes()
        self.assertFalse(service_types is self.service_types)
