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
Secret utilities.

.. versionadded:: 3.5
"""

import hmac


def _constant_time_compare(first, second):
    """Return True if both string or binary inputs are equal, otherwise False.

    This function should take a constant amount of time regardless of
    how many characters in the strings match. This function uses an
    approach designed to prevent timing analysis by avoiding
    content-based short circuiting behaviour, making it appropriate
    for cryptography.
    """
    first = str(first)
    second = str(second)
    if len(first) != len(second):
        return False
    result = 0
    for x, y in zip(first, second):
        result |= ord(x) ^ ord(y)
    return result == 0


try:
    constant_time_compare = hmac.compare_digest
except AttributeError:
    constant_time_compare = _constant_time_compare
