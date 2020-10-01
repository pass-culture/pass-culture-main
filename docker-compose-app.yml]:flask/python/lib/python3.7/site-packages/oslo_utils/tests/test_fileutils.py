# Copyright 2011 OpenStack Foundation.
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

import errno
import hashlib
import json
import os
import shutil
import stat
import tempfile
import time
from unittest import mock
import uuid
import yaml

from oslotest import base as test_base
import six

from oslo_utils import fileutils

TEST_PERMISSIONS = stat.S_IRWXU


class EnsureTree(test_base.BaseTestCase):
    def test_ensure_tree(self):
        tmpdir = tempfile.mkdtemp()
        try:
            testdir = '%s/foo/bar/baz' % (tmpdir,)
            fileutils.ensure_tree(testdir, TEST_PERMISSIONS)
            self.assertTrue(os.path.isdir(testdir))
            self.assertEqual(os.stat(testdir).st_mode,
                             TEST_PERMISSIONS | stat.S_IFDIR)
        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)


class DeleteIfExists(test_base.BaseTestCase):
    def test_file_present(self):
        tmpfile = tempfile.mktemp()

        open(tmpfile, 'w')
        fileutils.delete_if_exists(tmpfile)
        self.assertFalse(os.path.exists(tmpfile))

    def test_file_absent(self):
        tmpfile = tempfile.mktemp()

        fileutils.delete_if_exists(tmpfile)
        self.assertFalse(os.path.exists(tmpfile))

    def test_dir_present(self):
        tmpdir = tempfile.mktemp()
        os.mkdir(tmpdir)

        fileutils.delete_if_exists(tmpdir, remove=os.rmdir)
        self.assertFalse(os.path.exists(tmpdir))

    def test_file_error(self):
        def errm(path):
            raise OSError(errno.EINVAL, '')

        tmpfile = tempfile.mktemp()

        open(tmpfile, 'w')
        self.assertRaises(OSError, fileutils.delete_if_exists, tmpfile, errm)
        os.unlink(tmpfile)


class RemovePathOnError(test_base.BaseTestCase):
    def test_error(self):
        tmpfile = tempfile.mktemp()
        open(tmpfile, 'w')

        try:
            with fileutils.remove_path_on_error(tmpfile):
                raise Exception
        except Exception:
            self.assertFalse(os.path.exists(tmpfile))

    def test_no_error(self):
        tmpfile = tempfile.mktemp()
        open(tmpfile, 'w')

        with fileutils.remove_path_on_error(tmpfile):
            pass
        self.assertTrue(os.path.exists(tmpfile))
        os.unlink(tmpfile)

    def test_remove(self):
        tmpfile = tempfile.mktemp()
        open(tmpfile, 'w')

        try:
            with fileutils.remove_path_on_error(tmpfile, remove=lambda x: x):
                raise Exception
        except Exception:
            self.assertTrue(os.path.exists(tmpfile))
        os.unlink(tmpfile)

    def test_remove_dir(self):
        tmpdir = tempfile.mktemp()
        os.mkdir(tmpdir)

        try:
            with fileutils.remove_path_on_error(
                    tmpdir,
                    lambda path: fileutils.delete_if_exists(path, os.rmdir)):
                raise Exception
        except Exception:
            self.assertFalse(os.path.exists(tmpdir))


class WriteToTempfileTestCase(test_base.BaseTestCase):
    def setUp(self):
        super(WriteToTempfileTestCase, self).setUp()
        self.content = 'testing123'.encode('ascii')

    def check_file_content(self, path):
        with open(path, 'r') as fd:
            ans = fd.read()
            self.assertEqual(self.content, six.b(ans))

    def test_file_without_path_and_suffix(self):
        res = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(res))

        (basepath, tmpfile) = os.path.split(res)
        self.assertTrue(basepath.startswith(tempfile.gettempdir()))
        self.assertTrue(tmpfile.startswith('tmp'))

        self.check_file_content(res)

    def test_file_with_not_existing_path(self):
        random_dir = uuid.uuid4().hex
        path = '/tmp/%s/test1' % random_dir
        res = fileutils.write_to_tempfile(self.content, path=path)
        self.assertTrue(os.path.exists(res))
        (basepath, tmpfile) = os.path.split(res)
        self.assertEqual(basepath, path)
        self.assertTrue(tmpfile.startswith('tmp'))

        self.check_file_content(res)
        shutil.rmtree('/tmp/' + random_dir)

    def test_file_with_not_default_suffix(self):
        suffix = '.conf'
        res = fileutils.write_to_tempfile(self.content, suffix=suffix)
        self.assertTrue(os.path.exists(res))

        (basepath, tmpfile) = os.path.split(res)
        self.assertTrue(basepath.startswith(tempfile.gettempdir()))
        self.assertTrue(tmpfile.startswith('tmp'))
        self.assertTrue(tmpfile.endswith('.conf'))

        self.check_file_content(res)

    def test_file_with_not_existing_path_and_not_default_suffix(self):
        suffix = '.txt'
        random_dir = uuid.uuid4().hex
        path = '/tmp/%s/test2' % random_dir
        res = fileutils.write_to_tempfile(self.content,
                                          path=path,
                                          suffix=suffix)
        self.assertTrue(os.path.exists(res))
        (basepath, tmpfile) = os.path.split(res)
        self.assertTrue(tmpfile.startswith('tmp'))
        self.assertEqual(basepath, path)
        self.assertTrue(tmpfile.endswith(suffix))

        self.check_file_content(res)
        shutil.rmtree('/tmp/' + random_dir)

    def test_file_with_not_default_prefix(self):
        prefix = 'test'
        res = fileutils.write_to_tempfile(self.content, prefix=prefix)
        self.assertTrue(os.path.exists(res))

        (basepath, tmpfile) = os.path.split(res)
        self.assertTrue(tmpfile.startswith(prefix))
        self.assertTrue(basepath.startswith(tempfile.gettempdir()))

        self.check_file_content(res)


class TestComputeFileChecksum(test_base.BaseTestCase):

    def setUp(self):
        super(TestComputeFileChecksum, self).setUp()
        self.content = 'fake_content'.encode('ascii')

    def check_file_content(self, content, path):
        with open(path, 'r') as fd:
            ans = fd.read()
            self.assertEqual(content, six.b(ans))

    def test_compute_checksum_default_algorithm(self):
        path = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(path))
        self.check_file_content(self.content, path)

        expected_checksum = hashlib.sha256()
        expected_checksum.update(self.content)

        actual_checksum = fileutils.compute_file_checksum(path)

        self.assertEqual(expected_checksum.hexdigest(), actual_checksum)

    def test_compute_checksum_sleep_0_called(self):
        path = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(path))
        self.check_file_content(self.content, path)

        expected_checksum = hashlib.sha256()
        expected_checksum.update(self.content)

        with mock.patch.object(time, "sleep") as sleep_mock:
            actual_checksum = fileutils.compute_file_checksum(
                path, read_chunksize=4)

        sleep_mock.assert_has_calls([mock.call(0)] * 3)
        # Just to make sure that there were exactly 3 calls
        self.assertEqual(3, sleep_mock.call_count)
        self.assertEqual(expected_checksum.hexdigest(), actual_checksum)

    def test_compute_checksum_named_algorithm(self):
        path = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(path))
        self.check_file_content(self.content, path)

        expected_checksum = hashlib.sha512()
        expected_checksum.update(self.content)

        actual_checksum = fileutils.compute_file_checksum(path,
                                                          algorithm='sha512')

        self.assertEqual(expected_checksum.hexdigest(), actual_checksum)

    def test_compute_checksum_invalid_algorithm(self):
        path = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(path))
        self.check_file_content(self.content, path)

        self.assertRaises(ValueError, fileutils.compute_file_checksum,
                          path, algorithm='foo')

    def test_file_does_not_exist(self):
        random_file_name = uuid.uuid4().hex
        path = os.path.join('/tmp', random_file_name)
        self.assertRaises(IOError, fileutils.compute_file_checksum, path)

    def test_generic_io_error(self):
        tempdir = tempfile.mkdtemp()
        self.assertRaises(IOError, fileutils.compute_file_checksum, tempdir)


class LastBytesTestCase(test_base.BaseTestCase):
    """Test the last_bytes() utility method."""

    def setUp(self):
        super(LastBytesTestCase, self).setUp()
        self.content = b'1234567890'

    def test_truncated(self):
        res = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(res))
        out, unread_bytes = fileutils.last_bytes(res, 5)
        self.assertEqual(b'67890', out)
        self.assertGreater(unread_bytes, 0)

    def test_read_all(self):
        res = fileutils.write_to_tempfile(self.content)
        self.assertTrue(os.path.exists(res))
        out, unread_bytes = fileutils.last_bytes(res, 1000)
        self.assertEqual(b'1234567890', out)
        self.assertEqual(0, unread_bytes)

    def test_non_exist_file(self):
        self.assertRaises(IOError, fileutils.last_bytes,
                          'non_exist_file', 1000)


class FileTypeTestCase(test_base.BaseTestCase):
    """Test the is_yaml() and is_json() utility methods."""

    def setUp(self):
        super(FileTypeTestCase, self).setUp()
        data = {
            'name': 'test',
            'website': 'example.com'
        }
        temp_dir = tempfile.mkdtemp()
        self.json_file = tempfile.mktemp(dir=temp_dir)
        self.yaml_file = tempfile.mktemp(dir=temp_dir)

        with open(self.json_file, 'w') as fh:
            json.dump(data, fh)
        with open(self.yaml_file, 'w') as fh:
            yaml.dump(data, fh)

    def test_is_json(self):
        self.assertTrue(fileutils.is_json(self.json_file))
        self.assertFalse(fileutils.is_json(self.yaml_file))

    def test_is_yaml(self):
        self.assertTrue(fileutils.is_yaml(self.yaml_file))
        self.assertFalse(fileutils.is_yaml(self.json_file))
