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


import fixtures


class HackingCode(fixtures.Fixture):
    """A fixture to house the various code examples.

    Examples contains various keystoneauth hacking style checks.
    """

    oslo_namespace_imports = {
        'code': """
            import oslo.utils
            import oslo_utils
            import oslo.utils.encodeutils
            import oslo_utils.encodeutils
            from oslo import utils
            from oslo.utils import encodeutils
            from oslo_utils import encodeutils

            import oslo.serialization
            import oslo_serialization
            import oslo.serialization.jsonutils
            import oslo_serialization.jsonutils
            from oslo import serialization
            from oslo.serialization import jsonutils
            from oslo_serialization import jsonutils

            import oslo.config
            import oslo_config
            import oslo.config.cfg
            import oslo_config.cfg
            from oslo import config
            from oslo.config import cfg
            from oslo_config import cfg

            import oslo.i18n
            import oslo_i18n
            import oslo.i18n.log
            import oslo_i18n.log
            from oslo import i18n
            from oslo.i18n import log
            from oslo_i18n import log
        """,
        'expected_errors': [
            (1, 0, 'K333'),
            (3, 0, 'K333'),
            (5, 0, 'K333'),
            (6, 0, 'K333'),
            (9, 0, 'K333'),
            (11, 0, 'K333'),
            (13, 0, 'K333'),
            (14, 0, 'K333'),
            (17, 0, 'K333'),
            (19, 0, 'K333'),
            (21, 0, 'K333'),
            (22, 0, 'K333'),
            (25, 0, 'K333'),
            (27, 0, 'K333'),
            (29, 0, 'K333'),
            (30, 0, 'K333'),
        ],
    }
