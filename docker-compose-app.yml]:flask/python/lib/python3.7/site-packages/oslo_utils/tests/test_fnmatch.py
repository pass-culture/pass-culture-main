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

import fnmatch as standard_fnmatch
import ntpath
import posixpath
import sys
from unittest import mock

from oslotest import base
import six


fnmatch = None


class TestFnmatch(base.BaseTestCase):

    def _test_fnmatch(self):
        self.assertFalse(fnmatch.fnmatch("tesX", "Test"))
        self.assertTrue(fnmatch.fnmatch("test", "test"))
        self.assertFalse(fnmatch.fnmatchcase("test", "Test"))
        self.assertTrue(fnmatch.fnmatchcase("test", "test"))
        self.assertTrue(fnmatch.fnmatch("testX", "test*"))
        self.assertEqual(["Test"], fnmatch.filter(["Test", "TestX"], "Test"))

    def _test_fnmatch_posix_nt(self):
        with mock.patch("os.path", new=posixpath):
            self.assertFalse(fnmatch.fnmatch("test", "Test"))
            self._test_fnmatch()
        with mock.patch("os.path", new=ntpath):
            self._test_fnmatch()
            self.assertTrue(fnmatch.fnmatch("test", "Test"))
            self.assertEqual(["Test"],
                             fnmatch.filter(["Test", "TestX"], "test"))

    def test_fnmatch(self):
        global fnmatch

        fnmatch = standard_fnmatch
        self._test_fnmatch_posix_nt()

        with mock.patch.object(sys, 'version_info', new=(2, 7, 11)):
            from oslo_utils import fnmatch as oslo_fnmatch
            fnmatch = oslo_fnmatch
            self._test_fnmatch_posix_nt()

        with mock.patch.object(sys, 'version_info', new=(2, 7, 0)):
            six.moves.reload_module(oslo_fnmatch)
            self._test_fnmatch_posix_nt()
