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


"""Kerberos authentication plugins.

.. warning::
    This module requires installation of an extra package (`requests_kerberos`)
    not installed by default. Without the extra package an import error will
    occur. The extra package can be installed using::

      $ pip install keystoneauth1[kerberos]
"""

try:
    import requests_kerberos
except ImportError:
    requests_kerberos = None

from keystoneauth1 import access
from keystoneauth1.identity import v3
from keystoneauth1.identity.v3 import federation


def _mutual_auth(value):
    if value is None:
        return requests_kerberos.OPTIONAL
    return {
        'required': requests_kerberos.REQUIRED,
        'optional': requests_kerberos.OPTIONAL,
        'disabled': requests_kerberos.DISABLED,
    }.get(value.lower(), requests_kerberos.OPTIONAL)


def _requests_auth(mutual_authentication):
    return requests_kerberos.HTTPKerberosAuth(
        mutual_authentication=_mutual_auth(mutual_authentication))


def _dependency_check():
    if requests_kerberos is None:
        raise ImportError("""
Using the kerberos authentication plugin requires installation of additional
packages. These can be installed with::

    $ pip install keystoneauth1[kerberos]
""")


class KerberosMethod(v3.AuthMethod):

    _method_parameters = ['mutual_auth']

    def __init__(self, *args, **kwargs):
        _dependency_check()
        super(KerberosMethod, self).__init__(*args, **kwargs)

    def get_auth_data(self, session, auth, headers, request_kwargs, **kwargs):
        # NOTE(jamielennox): request_kwargs is passed as a kwarg however it is
        # required and always present when called from keystoneclient.
        request_kwargs['requests_auth'] = _requests_auth(self.mutual_auth)
        return 'kerberos', {}


class Kerberos(v3.AuthConstructor):
    _auth_method_class = KerberosMethod


class MappedKerberos(federation.FederationBaseAuth):
    """Authenticate using Kerberos via the keystone federation mechanisms.

    This uses the OS-FEDERATION extension to gain an unscoped token and then
    use the standard keystone auth process to scope that to any given project.
    """

    def __init__(self, auth_url, identity_provider, protocol,
                 mutual_auth=None, **kwargs):
        _dependency_check()
        self.mutual_auth = mutual_auth
        super(MappedKerberos, self).__init__(auth_url, identity_provider,
                                             protocol, **kwargs)

    def get_unscoped_auth_ref(self, session, **kwargs):
        resp = session.get(self.federated_token_url,
                           requests_auth=_requests_auth(self.mutual_auth),
                           authenticated=False)

        return access.create(body=resp.json(), resp=resp)
