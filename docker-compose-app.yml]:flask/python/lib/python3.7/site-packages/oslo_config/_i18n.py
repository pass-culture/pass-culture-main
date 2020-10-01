# Copyright 2016 OpenStack Foundation
#
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

"""oslo.i18n integration module.

See https://docs.openstack.org/oslo.i18n/latest/user/index.html.

"""

import oslo_i18n

DOMAIN = "oslo.config"

_translators = oslo_i18n.TranslatorFactory(domain=DOMAIN)

# The primary translation function using the well-known name "_"
_ = _translators.primary

# The contextual translation function using the name "_C"
# requires oslo.i18n >=2.1.0
_C = _translators.contextual_form

# The plural translation function using the name "_P"
# requires oslo.i18n >=2.1.0
_P = _translators.plural_form


def get_available_languages():
    return oslo_i18n.get_available_languages(DOMAIN)
