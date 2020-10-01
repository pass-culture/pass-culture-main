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


from keystoneauth1.exceptions import auth_plugins

__all__ = (
    'InvalidDiscoveryEndpoint', 'InvalidOidcDiscoveryDocument',
    'OidcAccessTokenEndpointNotFound', 'OidcAuthorizationEndpointNotFound',
    'OidcGrantTypeMissmatch', 'OidcPluginNotSupported',
)


class InvalidDiscoveryEndpoint(auth_plugins.AuthPluginException):
    message = "OpenID Connect Discovery Document endpoint not set."""


class InvalidOidcDiscoveryDocument(auth_plugins.AuthPluginException):
    message = "OpenID Connect Discovery Document is not valid JSON."""


class OidcAccessTokenEndpointNotFound(auth_plugins.AuthPluginException):
    message = "OpenID Connect access token endpoint not provided."


class OidcAuthorizationEndpointNotFound(auth_plugins.AuthPluginException):
    message = "OpenID Connect authorization endpoint not provided."


class OidcGrantTypeMissmatch(auth_plugins.AuthPluginException):
    message = "Missmatch between OpenID Connect plugin and grant_type argument"


class OidcPluginNotSupported(auth_plugins.AuthPluginException):
    message = "OpenID Connect grant type not supported by provider."
