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

from keystoneauth1.identity import base
from keystoneauth1.identity import generic
from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1.identity.v3 import oidc


BaseIdentityPlugin = base.BaseIdentityPlugin

V2Password = v2.Password
"""See :class:`keystoneauth1.identity.v2.Password`"""

V2Token = v2.Token
"""See :class:`keystoneauth1.identity.v2.Token`"""

V3Password = v3.Password
"""See :class:`keystoneauth1.identity.v3.Password`"""

V3Token = v3.Token
"""See :class:`keystoneauth1.identity.v3.Token`"""

Password = generic.Password
"""See :class:`keystoneauth1.identity.generic.Password`"""

Token = generic.Token
"""See :class:`keystoneauth1.identity.generic.Token`"""

V3OidcClientCredentials = oidc.OidcClientCredentials
"""See :class:`keystoneauth1.identity.v3.oidc.OidcClientCredentials`"""

V3OidcPassword = oidc.OidcPassword
"""See :class:`keystoneauth1.identity.v3.oidc.OidcPassword`"""

V3OidcAuthorizationCode = oidc.OidcAuthorizationCode
"""See :class:`keystoneauth1.identity.v3.oidc.OidcAuthorizationCode`"""

V3OidcAccessToken = oidc.OidcAccessToken
"""See :class:`keystoneauth1.identity.v3.oidc.OidcAccessToken`"""

V3TOTP = v3.TOTP
"""See :class:`keystoneauth1.identity.v3.TOTP`"""

V3TokenlessAuth = v3.TokenlessAuth
"""See :class:`keystoneauth1.identity.v3.TokenlessAuth`"""

V3ApplicationCredential = v3.ApplicationCredential
"""See :class:`keystoneauth1.identity.v3.ApplicationCredential`"""

V3MultiFactor = v3.MultiFactor
"""See :class:`keystoneauth1.identity.v3.MultiFactor`"""

__all__ = ('BaseIdentityPlugin',
           'Password',
           'Token',
           'V2Password',
           'V2Token',
           'V3Password',
           'V3Token',
           'V3OidcPassword',
           'V3OidcAuthorizationCode',
           'V3OidcAccessToken',
           'V3TOTP',
           'V3TokenlessAuth',
           'V3ApplicationCredential',
           'V3MultiFactor')
