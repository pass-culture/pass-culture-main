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

"""Thread safe fnmatch re-implementation.

Standard library fnmatch in Python versions <= 2.7.9 has thread safe
issue, this module is created for such case. see:
https://bugs.python.org/issue23191

.. versionadded:: 3.3
"""

import fnmatch as standard_fnmatch
import os
import posixpath
import re
import sys


if sys.version_info > (2, 7, 9):
    fnmatch = standard_fnmatch.fnmatch
    fnmatchcase = standard_fnmatch.fnmatchcase
    filter = standard_fnmatch.filter
    translate = standard_fnmatch.translate
else:
    _MATCH_CACHE = {}
    _MATCH_CACHE_MAX = 100

    translate = standard_fnmatch.translate

    def _get_cached_pattern(pattern):
        cached_pattern = _MATCH_CACHE.get(pattern)
        if cached_pattern is None:
            translated_pattern = translate(pattern)
            cached_pattern = re.compile(translated_pattern)
            if len(_MATCH_CACHE) >= _MATCH_CACHE_MAX:
                _MATCH_CACHE.clear()
            _MATCH_CACHE[pattern] = cached_pattern
        return cached_pattern

    def fnmatchcase(filename, pattern):
        cached_pattern = _get_cached_pattern(pattern)
        return cached_pattern.match(filename) is not None

    def fnmatch(filename, pattern):
        filename = os.path.normcase(filename)
        pattern = os.path.normcase(pattern)
        return fnmatchcase(filename, pattern)

    def filter(filenames, pattern):
        filtered_filenames = []

        pattern = os.path.normcase(pattern)
        cached_pattern = _get_cached_pattern(pattern)

        if os.path is posixpath:
            # normcase on posix is NOP. Optimize it away from the loop.
            for filename in filenames:
                if cached_pattern.match(filename):
                    filtered_filenames.append(filename)
        else:
            for filename in filenames:
                norm_name = os.path.normcase(filename)
                if cached_pattern.match(norm_name):
                    filtered_filenames.append(filename)

        return filtered_filenames
