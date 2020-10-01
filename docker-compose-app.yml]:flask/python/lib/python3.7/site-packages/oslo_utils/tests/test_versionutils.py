# Copyright (c) 2013 OpenStack Foundation
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

from oslo_utils import versionutils


class IsCompatibleTestCase(test_base.BaseTestCase):
    def test_same_version(self):
        self.assertTrue(versionutils.is_compatible('1', '1'))
        self.assertTrue(versionutils.is_compatible('1.0', '1.0'))
        self.assertTrue(versionutils.is_compatible('1.0.0', '1.0.0'))

    def test_requested_minor_greater(self):
        self.assertFalse(versionutils.is_compatible('1.1', '1.0'))

    def test_requested_minor_less_than(self):
        self.assertTrue(versionutils.is_compatible('1.0', '1.1'))

    def test_requested_patch_greater(self):
        self.assertFalse(versionutils.is_compatible('1.0.1', '1.0.0'))

    def test_requested_patch_less_than(self):
        self.assertTrue(versionutils.is_compatible('1.0.0', '1.0.1'))

    def test_requested_patch_not_present_same(self):
        self.assertTrue(versionutils.is_compatible('1.0', '1.0.0'))

    def test_requested_patch_not_present_less_than(self):
        self.assertTrue(versionutils.is_compatible('1.0', '1.0.1'))

    def test_current_patch_not_present_same(self):
        self.assertTrue(versionutils.is_compatible('1.0.0', '1.0'))

    def test_current_patch_not_present_less_than(self):
        self.assertFalse(versionutils.is_compatible('1.0.1', '1.0'))

    def test_same_major_true(self):
        """Even though the current version is 2.0, since `same_major` defaults
        to `True`, 1.0 is deemed incompatible.
        """
        self.assertFalse(versionutils.is_compatible('2.0', '1.0'))
        self.assertTrue(versionutils.is_compatible('1.0', '1.0'))
        self.assertFalse(versionutils.is_compatible('1.0', '2.0'))

    def test_same_major_false(self):
        """With `same_major` set to False, then major version compatibiity
        rule is not enforced, so a current version of 2.0 is deemed to satisfy
        a requirement of 1.0.
        """
        self.assertFalse(versionutils.is_compatible('2.0', '1.0',
                                                    same_major=False))
        self.assertTrue(versionutils.is_compatible('1.0', '1.0',
                                                   same_major=False))
        self.assertTrue(versionutils.is_compatible('1.0', '2.0',
                                                   same_major=False))

    def test_convert_version_to_int(self):
        self.assertEqual(6002000, versionutils.convert_version_to_int('6.2.0'))
        self.assertEqual(6004003,
                         versionutils.convert_version_to_int((6, 4, 3)))
        self.assertEqual(5, versionutils.convert_version_to_int((5, )))
        self.assertRaises(ValueError,
                          versionutils.convert_version_to_int, '5a.6b')

    def test_convert_version_to_string(self):
        self.assertEqual('6.7.0', versionutils.convert_version_to_str(6007000))
        self.assertEqual('4', versionutils.convert_version_to_str(4))

    def test_convert_version_to_tuple(self):
        self.assertEqual((6, 7, 0),
                         versionutils.convert_version_to_tuple('6.7.0'))
