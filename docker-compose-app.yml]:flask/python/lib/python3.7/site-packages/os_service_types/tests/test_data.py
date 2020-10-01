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
test_data
------------

Tests for `os_service_types.data` module.

"""

import json

import six

from os_service_types import data
from os_service_types.tests import base


if six.PY2:
    # Python 2 has not FileNotFoundError exception
    FileNotFoundError = IOError


class TestData(base.TestCase, base.TemporaryFileMixin):

    def setUp(self):
        super(TestData, self).setUp()

    def test_load(self):
        json_data = {'some_key': 'some_value'}
        filename = self.create_json(json_data)
        actual_data = data.read_data(filename)
        self.assertEqual(json_data, actual_data)

    def test_load_service_types(self):
        json_data = data.read_data('service-types.json')
        for key in ["all_types_by_service_type", "forward",
                    "primary_service_by_project", "reverse"]:
            self.assertIn(key, json_data)

    def test_load_non_existing(self):
        self.assertRaises(FileNotFoundError, data.read_data,
                          '/non-existing-file')

    def create_json(self, json_data):
        fd, name = self.create_temp_file(suffix='.json')
        with fd:
            json.dump(json_data, fd)
        return name
