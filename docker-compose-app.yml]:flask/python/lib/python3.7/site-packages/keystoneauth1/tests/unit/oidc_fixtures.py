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

UNSCOPED_TOKEN = {
    "token": {
        "issued_at": "2014-06-09T09:48:59.643406Z",
        "extras": {},
        "methods": ["oidc"],
        "expires_at": "2014-06-09T10:48:59.643375Z",
        "user": {
            "OS-FEDERATION": {
                "identity_provider": {
                    "id": "bluepages"
                },
                "protocol": {
                    "id": "oidc"
                },
                "groups": [
                    {"id": "1764fa5cf69a49a4918131de5ce4af9a"}
                ]
            },
            "id": "oidc_user%40example.com",
            "name": "oidc_user@example.com"
        }
    }
}

ACCESS_TOKEN_VIA_PASSWORD_RESP = {
    "access_token": "z5H1ITZLlJVDHQXqJun",
    "token_type": "bearer",
    "expires_in": 3599,
    "scope": "openid profile",
    "refresh_token": "DCERsh83IAhu9bhavrp"
}

ACCESS_TOKEN_VIA_AUTH_GRANT_RESP = {
    "access_token": "ya29.jgGIjfVrBPWLStWSU3eh8ioE6hG06QQ",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "1/ySXNO9XISBMIgOrJDtdun6zK6XiATCKT",
    "id_token": "eyJhbGciOiJSUzI1Ni8hOYHuZT8dt_yynmJVhcU"
}

DISCOVERY_DOCUMENT = {
    "authorization_endpoint": "https://localhost:8020/oidc/authorize",
    "claims_supported": [
        "sub",
        "name",
        "preferred_username",
        "given_name",
        "family_name",
        "middle_name",
        "nickname",
        "profile",
        "picture",
        "website",
        "gender",
        "zoneinfo",
        "locale",
        "updated_at",
        "birthdate",
        "email",
        "email_verified",
        "phone_number",
        "phone_number_verified",
        "address"
    ],
    "grant_types_supported": [
        "authorization_code",
        "password",
    ],
    "introspection_endpoint": "https://localhost:8020/oidc/introspect",
    "issuer": "https://localhost:8020/oidc/",
    "jwks_uri": "https://localhost:8020/oidc/jwk",
    "op_policy_uri": "https://localhost:8020/oidc/about",
    "op_tos_uri": "https://localhost:8020/oidc/about",
    "registration_endpoint": "https://localhost:8020/oidc/register",
    "revocation_endpoint": "https://localhost:8020/oidc/revoke",
    "service_documentation": "https://localhost:8020/oidc/about",
    "token_endpoint": "https://localhost:8020/oidc/token",
    "userinfo_endpoint": "https://localhost:8020/oidc/userinfo",
    "token_endpoint_auth_methods_supported": [
        "client_secret_post",
        "client_secret_basic",
        "client_secret_jwt",
        "private_key_jwt",
        "none"
    ],
}
