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

UNSCOPED_TOKEN_HEADER = 'UNSCOPED_TOKEN'

UNSCOPED_TOKEN = {
    "token": {
        "issued_at": "2014-06-09T09:48:59.643406Z",
        "extras": {},
        "methods": ["token"],
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


SAML_ENCODING = "<?xml version='1.0' encoding='UTF-8'?>"

TOKEN_SAML_RESPONSE = """
<ns2:Response Destination="http://beta.example.com/Shibboleth.sso/POST/ECP"
  ID="8c21de08d2f2435c9acf13e72c982846"
  IssueInstant="2015-03-25T14:43:21Z"
  Version="2.0">
  <saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">
    http://keystone.idp/v3/OS-FEDERATION/saml2/idp
  </saml:Issuer>
  <ns2:Status>
    <ns2:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </ns2:Status>
  <saml:Assertion ID="a5f02efb0bff4044b294b4583c7dfc5d"
    IssueInstant="2015-03-25T14:43:21Z" Version="2.0">
  <saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">
    http://keystone.idp/v3/OS-FEDERATION/saml2/idp</saml:Issuer>
  <xmldsig:Signature>
    <xmldsig:SignedInfo>
      <xmldsig:CanonicalizationMethod
        Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
      <xmldsig:SignatureMethod
        Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
      <xmldsig:Reference URI="#a5f02efb0bff4044b294b4583c7dfc5d">
        <xmldsig:Transforms>
          <xmldsig:Transform
             Algorithm="http://www.w3.org/2000/09/xmldsig#
             enveloped-signature"/>
          <xmldsig:Transform
             Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
        </xmldsig:Transforms>
        <xmldsig:DigestMethod
          Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
        <xmldsig:DigestValue>
          0KH2CxdkfzU+6eiRhTC+mbObUKI=
        </xmldsig:DigestValue>
      </xmldsig:Reference>
    </xmldsig:SignedInfo>
    <xmldsig:SignatureValue>
      m2jh5gDvX/1k+4uKtbb08CHp2b9UWsLw
    </xmldsig:SignatureValue>
    <xmldsig:KeyInfo>
      <xmldsig:X509Data>
        <xmldsig:X509Certificate>...</xmldsig:X509Certificate>
      </xmldsig:X509Data>
    </xmldsig:KeyInfo>
  </xmldsig:Signature>
  <saml:Subject>
    <saml:NameID>admin</saml:NameID>
    <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
      <saml:SubjectConfirmationData
        NotOnOrAfter="2015-03-25T15:43:21.172385Z"
        Recipient="http://beta.example.com/Shibboleth.sso/POST/ECP"/>
    </saml:SubjectConfirmation>
  </saml:Subject>
  <saml:AuthnStatement AuthnInstant="2015-03-25T14:43:21Z"
    SessionIndex="9790eb729858456f8a33b7a11f0a637e"
    SessionNotOnOrAfter="2015-03-25T15:43:21.172385Z">
    <saml:AuthnContext>
      <saml:AuthnContextClassRef>
        urn:oasis:names:tc:SAML:2.0:ac:classes:Password
      </saml:AuthnContextClassRef>
      <saml:AuthenticatingAuthority>
        http://keystone.idp/v3/OS-FEDERATION/saml2/idp
      </saml:AuthenticatingAuthority>
    </saml:AuthnContext>
  </saml:AuthnStatement>
  <saml:AttributeStatement>
    <saml:Attribute Name="openstack_user"
      NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
      <saml:AttributeValue xsi:type="xs:string">admin</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="openstack_roles"
      NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
      <saml:AttributeValue xsi:type="xs:string">admin</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="openstack_project"
      NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
      <saml:AttributeValue xsi:type="xs:string">admin</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
  </saml:Assertion>
</ns2:Response>
"""

TOKEN_BASED_SAML = ''.join([SAML_ENCODING, TOKEN_SAML_RESPONSE])

ECP_ENVELOPE = """
<ns0:Envelope
  xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:ns1="urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
  xmlns:ns2="urn:oasis:names:tc:SAML:2.0:protocol"
  xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
  xmlns:xmldsig="http://www.w3.org/2000/09/xmldsig#"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <ns0:Header>
    <ns1:RelayState
      ns0:actor="http://schemas.xmlsoap.org/soap/actor/next"
      ns0:mustUnderstand="1">
        ss:mem:1ddfe8b0f58341a5a840d2e8717b0737
      </ns1:RelayState>
  </ns0:Header>
  <ns0:Body>
  {0}
  </ns0:Body>
</ns0:Envelope>
""".format(TOKEN_SAML_RESPONSE)

TOKEN_BASED_ECP = ''.join([SAML_ENCODING, ECP_ENVELOPE])
