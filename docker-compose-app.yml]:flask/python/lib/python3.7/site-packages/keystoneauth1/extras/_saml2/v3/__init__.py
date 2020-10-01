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

from keystoneauth1.extras._saml2.v3 import adfs
from keystoneauth1.extras._saml2.v3 import base
from keystoneauth1.extras._saml2.v3 import saml2

_SAML2_AVAILABLE = base.etree is not None and saml2.etree is not None
_ADFS_AVAILABLE = base.etree is not None and adfs.etree is not None

Saml2Password = saml2.Password
ADFSPassword = adfs.Password

__all__ = ('Saml2Password', 'ADFSPassword')
