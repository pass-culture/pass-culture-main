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

"""
File utilities.

.. versionadded:: 1.8
"""

import contextlib
import errno
import hashlib
import json
import os
import stat
import tempfile
import time
import yaml

from oslo_utils import excutils

_DEFAULT_MODE = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO


def ensure_tree(path, mode=_DEFAULT_MODE):
    """Create a directory (and any ancestor directories required)

    :param path: Directory to create
    :param mode: Directory creation permissions
    """
    try:
        os.makedirs(path, mode)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            if not os.path.isdir(path):
                raise
        else:
            raise


def delete_if_exists(path, remove=os.unlink):
    """Delete a file, but ignore file not found error.

    :param path: File to delete
    :param remove: Optional function to remove passed path
    """

    try:
        remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


@contextlib.contextmanager
def remove_path_on_error(path, remove=delete_if_exists):
    """Protect code that wants to operate on PATH atomically.
    Any exception will cause PATH to be removed.

    :param path: File to work with
    :param remove: Optional function to remove passed path
    """

    try:
        yield
    except Exception:
        with excutils.save_and_reraise_exception():
            remove(path)


def write_to_tempfile(content, path=None, suffix='', prefix='tmp'):
    """Create a temporary file containing data.

    Create a temporary file containing specified content, with a specified
    filename suffix and prefix. The tempfile will be created in a default
    location, or in the directory `path`, if it is not None. `path` and its
    parent directories will be created if they don't exist.

    :param content: bytestring to write to the file
    :param path: same as parameter 'dir' for mkstemp
    :param suffix: same as parameter 'suffix' for mkstemp
    :param prefix: same as parameter 'prefix' for mkstemp

    For example: it can be used in database tests for creating
    configuration files.

    .. versionadded:: 1.9
    """
    if path:
        ensure_tree(path)

    (fd, path) = tempfile.mkstemp(suffix=suffix, dir=path, prefix=prefix)
    try:
        os.write(fd, content)
    finally:
        os.close(fd)
    return path


def compute_file_checksum(path, read_chunksize=65536, algorithm='sha256'):
    """Compute checksum of a file's contents.

    :param path: Path to the file
    :param read_chunksize: Maximum number of bytes to be read from the file
     at once. Default is 65536 bytes or 64KB
    :param algorithm: The hash algorithm name to use. For example, 'md5',
     'sha256', 'sha512' and so on. Default is 'sha256'. Refer to
     hashlib.algorithms_available for available algorithms
    :return: Hex digest string of the checksum

    .. versionadded:: 3.31.0
    """
    checksum = hashlib.new(algorithm)  # Raises appropriate exceptions.
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(read_chunksize), b''):
            checksum.update(chunk)
            # Release greenthread, if greenthreads are not used it is a noop.
            time.sleep(0)
    return checksum.hexdigest()


def last_bytes(path, num):
    """Return num bytes from the end of the file and unread byte count.

    Returns a tuple containing some content from the file and the
    number of bytes that appear in the file before the point at which
    reading started. The content will be at most ``num`` bytes, taken
    from the end of the file. If the file is smaller than ``num``
    bytes the entire content of the file is returned.

    :param path: The file path to read
    :param num: The number of bytes to return

    :returns: (data, unread_bytes)

    """

    with open(path, 'rb') as fp:
        try:
            fp.seek(-num, os.SEEK_END)
        except IOError as e:
            # seek() fails with EINVAL when trying to go before the start of
            # the file. It means that num is larger than the file size, so
            # just go to the start.
            if e.errno == errno.EINVAL:
                fp.seek(0, os.SEEK_SET)
            else:
                raise
        unread_bytes = fp.tell()
        return (fp.read(), unread_bytes)


def is_json(file_path):
    """Check if file is of json type or not.

    This function try to load the input file using json.loads()
    and return False if ValueError otherwise True.

    :param file_path: The file path to check

    :returns: bool

    """
    with open(file_path, 'r') as fh:
        data = fh.read()
    try:
        json.loads(data)
        return True
    except ValueError:
        return False


def is_yaml(file_path):
    """Check if file is of yaml type or not.

    This function try to load the input file using yaml.safe_load()
    and return True if loadable. Because every json file can be loadable
    in yaml, so this function return False if file is loadable using
    json.loads() means it is json file.

    :param file_path: The file path to check

    :returns: bool

    """
    with open(file_path, 'r') as fh:
        data = fh.read()
        is_yaml = False
        try:
            json.loads(data)
        except ValueError:
            try:
                yaml.safe_load(data)
                is_yaml = True
            except yaml.scanner.ScannerError:
                pass
        return is_yaml
