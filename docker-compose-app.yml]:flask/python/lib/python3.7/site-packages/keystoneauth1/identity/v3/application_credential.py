# Copyright 2018 SUSE Linux GmbH
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

from keystoneauth1.identity.v3 import base


__all__ = ('ApplicationCredentialMethod', 'ApplicationCredential')


class ApplicationCredentialMethod(base.AuthMethod):
    """Construct a User/Passcode based authentication method.

    :param string application_credential_secret: Application credential secret.
    :param string application_credential_id: Application credential id.
    :param string application_credential_name: The name of the application
                                               credential, if an ID is not
                                               provided.
    :param string username: Username for authentication, if an application
                            credential ID is not provided.
    :param string user_id: User ID for authentication, if an application
                           credential ID is not provided.
    :param string user_domain_id: User's domain ID for authentication, if an
                                  application credential ID is not provided.
    :param string user_domain_name: User's domain name for authentication, if
                                    an application credential ID is not
                                    provided.
    """

    _method_parameters = ['application_credential_secret',
                          'application_credential_id',
                          'application_credential_name',
                          'user_id',
                          'username',
                          'user_domain_id',
                          'user_domain_name']

    def get_auth_data(self, session, auth, headers, **kwargs):
        auth_data = {'secret': self.application_credential_secret}

        if self.application_credential_id:
            auth_data['id'] = self.application_credential_id
        else:
            auth_data['name'] = self.application_credential_name
            auth_data['user'] = {}
            if self.user_id:
                auth_data['user']['id'] = self.user_id
            elif self.username:
                auth_data['user']['name'] = self.username

                if self.user_domain_id:
                    auth_data['user']['domain'] = {'id': self.user_domain_id}
                elif self.user_domain_name:
                    auth_data['user']['domain'] = {
                        'name': self.user_domain_name}

        return 'application_credential', auth_data

    def get_cache_id_elements(self):
        return dict(('application_credential_%s' % p, getattr(self, p))
                    for p in self._method_parameters)


class ApplicationCredential(base.AuthConstructor):
    """A plugin for authenticating with an application credential.

    :param string auth_url: Identity service endpoint for authentication.
    :param string application_credential_secret: Application credential secret.
    :param string application_credential_id: Application credential ID.
    :param string application_credential_name: Application credential name.
    :param string username: Username for authentication.
    :param string user_id: User ID for authentication.
    :param string user_domain_id: User's domain ID for authentication.
    :param string user_domain_name: User's domain name for authentication.
    :param bool reauthenticate: Allow fetching a new token if the current one
                                is going to expire. (optional) default True
    """

    _auth_method_class = ApplicationCredentialMethod
