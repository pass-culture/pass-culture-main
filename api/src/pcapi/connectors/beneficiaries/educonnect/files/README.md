# Educonnect, SAML2 and metadata

Educonnect is an an Identity Provider using SAML2 protocol, allowing pass Culture (the Service Provider) to verify young users identity.

## Educonnect metadata

Educonnect metadata files are used by our SAML client to encrypt SAML data. There is one file for Educonnect _pr4_ environment (`educonnect.pr4.metadata.xml`) which is used by our testing and staging environments, one file for the _production_ environment (`educonnect.production.metadata.xml`), used by our production environment.

## pass Culture metadata

The files `PC-{env}-metadata.xml` are public and were transmitted to Educonnect. Each of them include:

- our `entityId`, one per environment (testing, staging and production)
- a certificate public key: ending on october 2121. The certificates were issued with the following command :
  `openssl req -nodes -new -x509 -keyout PC-testing.key -out PC-testing.cert -days 36500`

These files are commited for information but are not used by our code.

The `settings.EDUCONNECT_SP_CERTIFICATE` variable corresponds to the public key written in the `X509Certificate` tag of the XML.

It is associated to the private key stored in `settings.EDUCONNECT_SP_PRIVATE_KEY` variable.

These two variables are used to dynamically build `private.key` and `public.cert` files, used by our SAML client.
