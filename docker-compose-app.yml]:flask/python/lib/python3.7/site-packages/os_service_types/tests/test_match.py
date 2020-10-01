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
test_match
----------

Tests for is_match logic

oslotest sets up a TempHomeDir for us, so there should be no ~/.cache files
available in these tests.
"""
from testscenarios import load_tests_apply_scenarios as load_tests  # noqa

import os_service_types
from os_service_types.tests import base


class TestMatch(base.TestCase):

    scenarios = [
        ('match-official', dict(
            requested='compute', found='compute', is_match=True)),
        ('direct-match-unknown', dict(
            requested='unknown', found='unknown', is_match=True)),
        ('volumev2-finds-block', dict(
            requested='volumev2', found='block-storage', is_match=True)),
        ('volumev3-finds-block', dict(
            requested='volumev3', found='block-storage', is_match=True)),
        ('block-finds-volumev2', dict(
            requested='block-storage', found='volumev2', is_match=True)),
        ('block-finds-volumev3', dict(
            requested='block-storage', found='volumev3', is_match=True)),
        ('volumev2-not-volumev3', dict(
            requested='volumev2', found='volumev3', is_match=False)),
        ('non-match', dict(
            requested='unknown', found='compute', is_match=False)),
    ]

    def setUp(self):
        super(TestMatch, self).setUp()
        # Make an object with no network access
        self.service_types = os_service_types.ServiceTypes()

    def test_is_match(self):
        self.assertEqual(
            self.is_match,
            self.service_types.is_match(self.requested, self.found))
