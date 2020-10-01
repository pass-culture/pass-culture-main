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

import os
import string

DIR = os.path.dirname(os.path.abspath(__file__))


def template(f, **kwargs):
    with open(os.path.join(DIR, 'templates', f)) as f:
        return string.Template(f.read()).substitute(**kwargs)


def soap_response(**kwargs):
    kwargs.setdefault('provider', 'https://idp.testshib.org/idp/shibboleth')
    kwargs.setdefault('consumer',
                      'https://openstack4.local/Shibboleth.sso/SAML2/ECP')
    kwargs.setdefault('issuer', 'https://openstack4.local/shibboleth')
    return template('soap_response.xml', **kwargs).encode('utf-8')


def saml_assertion(**kwargs):
    kwargs.setdefault('issuer', 'https://idp.testshib.org/idp/shibboleth')
    kwargs.setdefault('destination',
                      'https://openstack4.local/Shibboleth.sso/SAML2/ECP')
    return template('saml_assertion.xml', **kwargs).encode('utf-8')


def authn_request(**kwargs):
    kwargs.setdefault('issuer',
                      'https://openstack4.local/Shibboleth.sso/SAML2/ECP')
    return template('authn_request.xml', **kwargs).encode('utf-8')


SP_SOAP_RESPONSE = soap_response()
SAML2_ASSERTION = saml_assertion()
AUTHN_REQUEST = authn_request()

UNSCOPED_TOKEN_HEADER = 'UNSCOPED_TOKEN'

UNSCOPED_TOKEN = {
    "token": {
        "issued_at": "2014-06-09T09:48:59.643406Z",
        "extras": {},
        "methods": ["saml2"],
        "expires_at": "2014-06-09T10:48:59.643375Z",
        "user": {
            "OS-FEDERATION": {
                "identity_provider": {
                    "id": "testshib"
                },
                "protocol": {
                    "id": "saml2"
                },
                "groups": [
                    {"id": "1764fa5cf69a49a4918131de5ce4af9a"}
                ]
            },
            "id": "testhib%20user",
            "name": "testhib user"
        }
    }
}

PROJECTS = {
    "projects": [
        {
            "domain_id": "37ef61",
            "enabled": 'true',
            "id": "12d706",
            "links": {
                "self": "http://identity:35357/v3/projects/12d706"
            },
            "name": "a project name"
        },
        {
            "domain_id": "37ef61",
            "enabled": 'true',
            "id": "9ca0eb",
            "links": {
                "self": "http://identity:35357/v3/projects/9ca0eb"
            },
            "name": "another project"
        }
    ],
    "links": {
        "self": "http://identity:35357/v3/OS-FEDERATION/projects",
        "previous": 'null',
        "next": 'null'
    }
}

DOMAINS = {
    "domains": [
        {
            "description": "desc of domain",
            "enabled": 'true',
            "id": "37ef61",
            "links": {
                "self": "http://identity:35357/v3/domains/37ef61"
            },
            "name": "my domain"
        }
    ],
    "links": {
        "self": "http://identity:35357/v3/OS-FEDERATION/domains",
        "previous": 'null',
        "next": 'null'
    }
}
