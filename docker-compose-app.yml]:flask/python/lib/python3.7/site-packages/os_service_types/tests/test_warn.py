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
test_warn
---------

Tests for warnings
"""
import warnings

import os_service_types
from os_service_types import exc
from os_service_types.tests import base


class TestWarnOn(base.TestCase):

    def setUp(self):
        super(TestWarnOn, self).setUp()
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        self.service_types = os_service_types.ServiceTypes(warn=True)

    def test_warning_emitted_on_alias(self):
        with warnings.catch_warnings(record=True) as w:
            self.service_types.get_service_type('volumev2')
            self.assertEqual(1, len(w))
            self.assertTrue(issubclass(w[-1].category, exc.AliasUsageWarning))

    def test_warning_not_emitted_on_official(self):
        with warnings.catch_warnings(record=True) as w:
            self.service_types.get_service_type('block-storage')
            self.assertEqual(0, len(w))


class TestWarnOff(base.TestCase):

    def setUp(self):
        super(TestWarnOff, self).setUp()
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        self.service_types = os_service_types.ServiceTypes()

    def test_warning_not_emitted_on_alias(self):
        with warnings.catch_warnings(record=True) as w:
            self.service_types.get_service_type('volumev2')
            self.assertEqual(0, len(w))

    def test_warning_not_emitted_on_official(self):
        with warnings.catch_warnings(record=True) as w:
            self.service_types.get_service_type('block-storage')
            self.assertEqual(0, len(w))
