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
__all__ = ['__version__', 'ServiceTypes']

import pbr.version

from os_service_types.service_types import ServiceTypes  # flake8: noqa

__version__ = pbr.version.VersionInfo('os-service-types').version_string()
_service_type_manager = None


def get_service_types(*args, **kwargs):
    """Return singleton instance of the ServiceTypes object.

    Parameters are all passed through to the
    :class:`~os_service_types.service_types.ServiceTypes` constructor.

    .. note::

      Only one singleton is kept, so if instances with different parameter
      values are desired, directly calling the constructor is necessary.

    :returns: Singleton instance of
        :class:`~os_service_types.service_types.ServiceTypes`
    """
    global _service_type_manager
    if not _service_type_manager:
        _service_type_manager = ServiceTypes(*args, **kwargs)
    return _service_type_manager
