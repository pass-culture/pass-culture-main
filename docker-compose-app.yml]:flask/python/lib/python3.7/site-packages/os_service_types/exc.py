# Copyright 2017 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import textwrap
import warnings

__all__ = ['warn', 'AliasUsageWarning']


def warn(warning, **kwargs):
    """Emit a warning that has builtin message text."""
    message = textwrap.fill(textwrap.dedent(warning.details.format(**kwargs)))
    warnings.warn(message, category=warning)


class AliasUsageWarning(Warning):
    """Use of historical service-type aliases is discouraged."""

    details = """
    Requested service_type {given} is an old alias. Please update your
    code to reference the official service_type {official}.
    """


class UnofficialUsageWarning(Warning):
    """Use of unofficial service-types is discouraged."""

    details = """
    Requested service_type {given} is not a known official OpenStack project.
    """
