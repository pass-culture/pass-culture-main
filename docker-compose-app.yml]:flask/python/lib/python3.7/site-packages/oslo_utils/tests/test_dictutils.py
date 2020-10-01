# -*- coding: utf-8 -*-

# Copyright (c) 2016 EasyStack Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from oslotest import base as test_base

from oslo_utils import dictutils as du


class DictUtilsTestCase(test_base.BaseTestCase):

    def test_flatten_dict_to_keypairs(self):
        data = {'a': 'A', 'b': 'B',
                'nested': {'a': 'A', 'b': 'B'}}
        pairs = list(du.flatten_dict_to_keypairs(data))
        self.assertEqual([('a', 'A'), ('b', 'B'),
                          ('nested:a', 'A'), ('nested:b', 'B')],
                         pairs)

    def test_flatten_dict_to_keypairs_with_separator(self):
        data = {'a': 'A', 'b': 'B',
                'nested': {'a': 'A', 'b': 'B'}}
        pairs = list(du.flatten_dict_to_keypairs(data, separator='.'))
        self.assertEqual([('a', 'A'), ('b', 'B'),
                          ('nested.a', 'A'), ('nested.b', 'B')],
                         pairs)
