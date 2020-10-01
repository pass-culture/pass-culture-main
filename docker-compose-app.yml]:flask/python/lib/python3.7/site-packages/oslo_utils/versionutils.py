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

"""
Helpers for comparing version strings.

.. versionadded:: 1.6
"""

import packaging.version
import six

from oslo_utils._i18n import _


def is_compatible(requested_version, current_version, same_major=True):
    """Determine whether `requested_version` is satisfied by
    `current_version`; in other words, `current_version` is >=
    `requested_version`.

    :param requested_version: version to check for compatibility
    :param current_version: version to check against
    :param same_major: if True, the major version must be identical between
        `requested_version` and `current_version`. This is used when a
        major-version difference indicates incompatibility between the two
        versions. Since this is the common-case in practice, the default is
        True.
    :returns: True if compatible, False if not
    """
    requested = packaging.version.Version(requested_version)
    current = packaging.version.Version(current_version)

    if same_major:
        if requested.major != current.major:
            return False

    return current >= requested


def convert_version_to_int(version):
    """Convert a version to an integer.

    *version* must be a string with dots or a tuple of integers.

    .. versionadded:: 2.0
    """
    try:
        if isinstance(version, six.string_types):
            version = convert_version_to_tuple(version)
        if isinstance(version, tuple):
            return six.moves.reduce(lambda x, y: (x * 1000) + y, version)
    except Exception as ex:
        msg = _("Version %s is invalid.") % version
        six.raise_from(ValueError(msg), ex)


def convert_version_to_str(version_int):
    """Convert a version integer to a string with dots.

    .. versionadded:: 2.0
    """
    version_numbers = []
    factor = 1000
    while version_int != 0:
        version_number = version_int - (version_int // factor * factor)
        version_numbers.insert(0, six.text_type(version_number))
        version_int = version_int // factor

    return '.'.join(map(str, version_numbers))


def convert_version_to_tuple(version_str):
    """Convert a version string with dots to a tuple.

    .. versionadded:: 2.0
    """
    return tuple(int(part) for part in version_str.split('.'))
