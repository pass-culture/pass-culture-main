# Copyright 2012 Nebula, Inc.
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools

from keystoneauth1 import _utils as utils
from keystoneauth1.access import service_catalog
from keystoneauth1.access import service_providers


# gap, in seconds, to determine whether the given token is about to expire
STALE_TOKEN_DURATION = 30


__all__ = ('AccessInfo',
           'AccessInfoV2',
           'AccessInfoV3',
           'create')


def create(resp=None, body=None, auth_token=None):
    if resp and not body:
        body = resp.json()

    if 'token' in body:
        if resp and not auth_token:
            auth_token = resp.headers.get('X-Subject-Token')

        return AccessInfoV3(body, auth_token)
    elif 'access' in body:
        return AccessInfoV2(body, auth_token)

    raise ValueError('Unrecognized auth response')


def _missingproperty(f):

    @functools.wraps(f)
    def inner(self):
        try:
            return f(self)
        except KeyError:
            return None

    return property(inner)


class AccessInfo(object):
    """Encapsulates a raw authentication token from keystone.

    Provides helper methods for extracting useful values from that token.

    """

    _service_catalog_class = None

    def __init__(self, body, auth_token=None):
        self._data = body
        self._auth_token = auth_token
        self._service_catalog = None
        self._service_providers = None

    @property
    def service_catalog(self):
        if not self._service_catalog:
            self._service_catalog = self._service_catalog_class.from_token(
                self._data)

        return self._service_catalog

    def will_expire_soon(self, stale_duration=STALE_TOKEN_DURATION):
        """Determine if expiration is about to occur.

        :returns: true if expiration is within the given duration
        :rtype: boolean

        """
        norm_expires = utils.normalize_time(self.expires)
        # (gyee) should we move auth_token.will_expire_soon() to timeutils
        # instead of duplicating code here?
        soon = utils.from_utcnow(seconds=stale_duration)
        return norm_expires < soon

    def has_service_catalog(self):
        """Return true if the auth token has a service catalog.

        :returns: boolean
        """
        raise NotImplementedError()

    @property
    def auth_token(self):
        """Return the token_id associated with the auth request.

        To be used in headers for authenticating OpenStack API requests.

        :returns: str
        """
        return self._auth_token

    @property
    def expires(self):
        """Return the token expiration (as datetime object).

        :returns: datetime
        """
        raise NotImplementedError()

    @property
    def issued(self):
        """Return the token issue time (as datetime object).

        :returns: datetime
        """
        raise NotImplementedError()

    @property
    def username(self):
        """Return the username associated with the auth request.

        Follows the pattern defined in the V2 API of first looking for 'name',
        returning that if available, and falling back to 'username' if name
        is unavailable.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def user_id(self):
        """Return the user id associated with the auth request.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def user_domain_id(self):
        """Return the user's domain id associated with the auth request.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def user_domain_name(self):
        """Return the user's domain name associated with the auth request.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def role_ids(self):
        """Return a list of user's role ids associated with the auth request.

        :returns: a list of strings of role ids
        """
        raise NotImplementedError()

    @property
    def role_names(self):
        """Return a list of user's role names associated with the auth request.

        :returns: a list of strings of role names
        """
        raise NotImplementedError()

    @property
    def domain_name(self):
        """Return the domain name associated with the auth request.

        :returns: str or None (if no domain associated with the token)
        """
        raise NotImplementedError()

    @property
    def domain_id(self):
        """Return the domain id associated with the auth request.

        :returns: str or None (if no domain associated with the token)
        """
        raise NotImplementedError()

    @property
    def project_name(self):
        """Return the project name associated with the auth request.

        :returns: str or None (if no project associated with the token)
        """
        raise NotImplementedError()

    @property
    def tenant_name(self):
        """Synonym for project_name."""
        return self.project_name

    @property
    def scoped(self):
        """Return true if the auth token was scoped.

        Returns true if scoped to a tenant(project) or domain,
        and contains a populated service catalog.

        This is deprecated, use project_scoped instead.

        :returns: bool
        """
        return self.project_scoped or self.domain_scoped or self.system_scoped

    @property
    def project_scoped(self):
        """Return true if the auth token was scoped to a tenant (project).

        :returns: bool
        """
        return bool(self.project_id)

    @property
    def domain_scoped(self):
        """Return true if the auth token was scoped to a domain.

        :returns: bool
        """
        raise NotImplementedError()

    @property
    def system_scoped(self):
        """Return true if the auth token was scoped to the system.

        :returns: bool
        """
        raise NotImplementedError()

    @property
    def trust_id(self):
        """Return the trust id associated with the auth request.

        :returns: str or None (if no trust associated with the token)
        """
        raise NotImplementedError()

    @property
    def trust_scoped(self):
        """Return true if the auth token was scoped from a delegated trust.

        The trust delegation is via the OS-TRUST v3 extension.

        :returns: bool
        """
        raise NotImplementedError()

    @property
    def trustee_user_id(self):
        """Return the trustee user id associated with a trust.

        :returns: str or None (if no trust associated with the token)
        """
        raise NotImplementedError()

    @property
    def trustor_user_id(self):
        """Return the trustor user id associated with a trust.

        :returns: str or None (if no trust associated with the token)
        """
        raise NotImplementedError()

    @property
    def project_id(self):
        """Return the project ID associated with the auth request.

        This returns None if the auth token wasn't scoped to a project.

        :returns: str or None (if no project associated with the token)
        """
        raise NotImplementedError()

    @property
    def tenant_id(self):
        """Synonym for project_id."""
        return self.project_id

    @property
    def project_domain_id(self):
        """Return the project's domain id associated with the auth request.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def project_domain_name(self):
        """Return the project's domain name associated with the auth request.

        :returns: str
        """
        raise NotImplementedError()

    @property
    def oauth_access_token_id(self):
        """Return the access token ID if OAuth authentication used.

        :returns: str or None.
        """
        raise NotImplementedError()

    @property
    def oauth_consumer_id(self):
        """Return the consumer ID if OAuth authentication used.

        :returns: str or None.
        """
        raise NotImplementedError()

    @property
    def is_federated(self):
        """Return true if federation was used to get the token.

        :returns: boolean
        """
        raise NotImplementedError()

    @property
    def is_admin_project(self):
        """Return true if the current project scope is the admin project.

        For backwards compatibility purposes if there is nothing specified in
        the token we always assume we are in the admin project, so this will
        default to True.

        :returns boolean
        """
        raise NotImplementedError()

    @property
    def audit_id(self):
        """Return the audit ID if present.

        :returns: str or None.
        """
        raise NotImplementedError()

    @property
    def audit_chain_id(self):
        """Return the audit chain ID if present.

        In the event that a token was rescoped then this ID will be the
        :py:attr:`audit_id` of the initial token. Returns None if no value
        present.

        :returns: str or None.
        """
        raise NotImplementedError()

    @property
    def initial_audit_id(self):
        """The audit ID of the initially requested token.

        This is the :py:attr:`audit_chain_id` if present or the
        :py:attr:`audit_id`.
        """
        return self.audit_chain_id or self.audit_id

    @property
    def service_providers(self):
        """Return an object representing the list of trusted service providers.

        Used for Keystone2Keystone federating-out.

        :returns: :py:class:`keystoneauth1.service_providers.ServiceProviders`
                  or None
        """
        raise NotImplementedError()

    @property
    def bind(self):
        """Information about external mechanisms the token is bound to.

        If a token is bound to an external authentication mechanism it can only
        be used in conjunction with that mechanism. For example if bound to a
        kerberos principal it may only be accepted if there is also kerberos
        authentication performed on the request.

        :returns: A dictionary or None. The key will be the bind type the value
                  is a dictionary that is specific to the format of the bind
                  type. Returns None if there is no bind information in the
                  token.
        """
        raise NotImplementedError()

    @property
    def project_is_domain(self):
        """Return if a project act as a domain.

        :returns: bool
        """
        raise NotImplementedError()


class AccessInfoV2(AccessInfo):
    """An object for encapsulating raw v2 auth token from identity service."""

    version = 'v2.0'
    _service_catalog_class = service_catalog.ServiceCatalogV2

    def has_service_catalog(self):
        return 'serviceCatalog' in self._data.get('access', {})

    @_missingproperty
    def auth_token(self):
        set_token = super(AccessInfoV2, self).auth_token
        return set_token or self._data['access']['token']['id']

    @property
    def _token(self):
        return self._data['access']['token']

    @_missingproperty
    def expires(self):
        return utils.parse_isotime(self._token.get('expires'))

    @_missingproperty
    def issued(self):
        return utils.parse_isotime(self._token['issued_at'])

    @property
    def _user(self):
        return self._data['access']['user']

    @_missingproperty
    def username(self):
        return self._user.get('name') or self._user.get('username')

    @_missingproperty
    def user_id(self):
        return self._user['id']

    @property
    def user_domain_id(self):
        return None

    @property
    def user_domain_name(self):
        return None

    @_missingproperty
    def role_ids(self):
        metadata = self._data.get('access', {}).get('metadata', {})
        return metadata.get('roles', [])

    @_missingproperty
    def role_names(self):
        return [r['name'] for r in self._user.get('roles', [])]

    @property
    def domain_name(self):
        return None

    @property
    def domain_id(self):
        return None

    @property
    def project_name(self):
        try:
            tenant_dict = self._token['tenant']
        except KeyError:
            pass
        else:
            return tenant_dict.get('name')

        # pre grizzly
        try:
            return self._user['tenantName']
        except KeyError:
            pass

        # pre diablo, keystone only provided a tenantId
        try:
            return self._token['tenantId']
        except KeyError:
            pass

    @property
    def domain_scoped(self):
        return False

    @property
    def system_scoped(self):
        return False

    @property
    def _trust(self):
        return self._data['access']['trust']

    @_missingproperty
    def trust_id(self):
        return self._trust['id']

    @_missingproperty
    def trust_scoped(self):
        return bool(self._trust)

    @_missingproperty
    def trustee_user_id(self):
        return self._trust['trustee_user_id']

    @property
    def trustor_user_id(self):
        # this information is not available in the v2 token bug: #1331882
        return None

    @property
    def project_id(self):
        try:
            tenant_dict = self._token['tenant']
        except KeyError:
            pass
        else:
            return tenant_dict.get('id')

        # pre grizzly
        try:
            return self._user['tenantId']
        except KeyError:
            pass

        # pre diablo
        try:
            return self._token['tenantId']
        except KeyError:
            pass

    @property
    def project_is_domain(self):
        return False

    @property
    def project_domain_id(self):
        return None

    @property
    def project_domain_name(self):
        return None

    @property
    def oauth_access_token_id(self):
        return None

    @property
    def oauth_consumer_id(self):
        return None

    @property
    def is_federated(self):
        return False

    @property
    def is_admin_project(self):
        return True

    @property
    def audit_id(self):
        try:
            return self._token.get('audit_ids', [])[0]
        except IndexError:
            return None

    @property
    def audit_chain_id(self):
        try:
            return self._token.get('audit_ids', [])[1]
        except IndexError:
            return None

    @property
    def service_providers(self):
        return None

    @_missingproperty
    def bind(self):
        return self._token['bind']


class AccessInfoV3(AccessInfo):
    """An object encapsulating raw v3 auth token from identity service."""

    version = 'v3'
    _service_catalog_class = service_catalog.ServiceCatalogV3

    def has_service_catalog(self):
        return 'catalog' in self._data['token']

    @property
    def _user(self):
        return self._data['token']['user']

    @property
    def is_federated(self):
        return 'OS-FEDERATION' in self._user

    @property
    def is_admin_project(self):
        return self._data.get('token', {}).get('is_admin_project', True)

    @_missingproperty
    def expires(self):
        return utils.parse_isotime(self._data['token']['expires_at'])

    @_missingproperty
    def issued(self):
        return utils.parse_isotime(self._data['token']['issued_at'])

    @_missingproperty
    def user_id(self):
        return self._user['id']

    @property
    def user_domain_id(self):
        try:
            return self._user['domain']['id']
        except KeyError:
            if self.is_federated:
                return None
            raise

    @property
    def user_domain_name(self):
        try:
            return self._user['domain']['name']
        except KeyError:
            if self.is_federated:
                return None
            raise

    @_missingproperty
    def role_ids(self):
        return [r['id'] for r in self._data['token'].get('roles', [])]

    @_missingproperty
    def role_names(self):
        return [r['name'] for r in self._data['token'].get('roles', [])]

    @_missingproperty
    def username(self):
        return self._user['name']

    @_missingproperty
    def system(self):
        return self._data['token']['system']

    @property
    def _domain(self):
        return self._data['token']['domain']

    @_missingproperty
    def domain_name(self):
        return self._domain['name']

    @_missingproperty
    def domain_id(self):
        return self._domain['id']

    @property
    def _project(self):
        return self._data['token']['project']

    @_missingproperty
    def project_id(self):
        return self._project['id']

    @_missingproperty
    def project_is_domain(self):
        return self._data['token']['is_domain']

    @_missingproperty
    def project_domain_id(self):
        return self._project['domain']['id']

    @_missingproperty
    def project_domain_name(self):
        return self._project['domain']['name']

    @_missingproperty
    def project_name(self):
        return self._project['name']

    @property
    def domain_scoped(self):
        try:
            return bool(self._domain)
        except KeyError:
            return False

    @_missingproperty
    def system_scoped(self):
        return self._data['token']['system'].get('all', False)

    @property
    def _trust(self):
        return self._data['token']['OS-TRUST:trust']

    @_missingproperty
    def trust_id(self):
        return self._trust['id']

    @property
    def trust_scoped(self):
        try:
            return bool(self._trust)
        except KeyError:
            return False

    @_missingproperty
    def trustee_user_id(self):
        return self._trust['trustee_user']['id']

    @_missingproperty
    def trustor_user_id(self):
        return self._trust['trustor_user']['id']

    @property
    def application_credential(self):
        return self._data['token']['application_credential']

    @_missingproperty
    def application_credential_id(self):
        return self._data['token']['application_credential']['id']

    @_missingproperty
    def application_credential_access_rules(self):
        return self._data['token']['application_credential']['access_rules']

    @property
    def _oauth(self):
        return self._data['token']['OS-OAUTH1']

    @_missingproperty
    def oauth_access_token_id(self):
        return self._oauth['access_token_id']

    @_missingproperty
    def oauth_consumer_id(self):
        return self._oauth['consumer_id']

    @_missingproperty
    def audit_id(self):
        try:
            return self._data['token']['audit_ids'][0]
        except IndexError:
            return None

    @_missingproperty
    def audit_chain_id(self):
        try:
            return self._data['token']['audit_ids'][1]
        except IndexError:
            return None

    @property
    def service_providers(self):
        if not self._service_providers:
            self._service_providers = (
                service_providers.ServiceProviders.from_token(self._data))

        return self._service_providers

    @_missingproperty
    def bind(self):
        return self._data['token']['bind']
