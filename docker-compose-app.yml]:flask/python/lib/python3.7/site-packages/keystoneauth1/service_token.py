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

from keystoneauth1 import plugin

SERVICE_AUTH_HEADER_NAME = 'X-Service-Token'

__all__ = ('ServiceTokenAuthWrapper',)


class ServiceTokenAuthWrapper(plugin.BaseAuthPlugin):

    def __init__(self, user_auth, service_auth):
        self.user_auth = user_auth
        self.service_auth = service_auth

    def get_headers(self, session, **kwargs):
        headers = self.user_auth.get_headers(session, **kwargs)

        token = self.service_auth.get_token(session, **kwargs)
        headers[SERVICE_AUTH_HEADER_NAME] = token

        return headers

    def invalidate(self):
        # NOTE(jamielennox): hmm, what to do here? Should we invalidate both
        # the service and user auth? Only one? There's no way to know what the
        # failure was to selectively invalidate.
        user = self.user_auth.invalidate()
        service = self.service_auth.invalidate()
        return user or service

    def get_connection_params(self, *args, **kwargs):
        # NOTE(jamielennox): This is also a bit of a guess but unlikely to be a
        # problem in practice. We don't know how merging connection parameters
        # between these plugins will conflict - but there aren't many plugins
        # that set this anyway.
        # Take the service auth params first so that user auth params will be
        # given priority.
        params = self.service_auth.get_connection_params(*args, **kwargs)
        params.update(self.user_auth.get_connection_params(*args, **kwargs))
        return params

    # TODO(jamielennox): Everything below here is a generic wrapper that could
    # be extracted into a base wrapper class. We can do this as soon as there
    # is a need for it, but we may never actually need it.

    def get_token(self, *args, **kwargs):
        return self.user_auth.get_token(*args, **kwargs)

    def get_endpoint(self, *args, **kwargs):
        return self.user_auth.get_endpoint(*args, **kwargs)

    def get_user_id(self, *args, **kwargs):
        return self.user_auth.get_user_id(*args, **kwargs)

    def get_project_id(self, *args, **kwargs):
        return self.user_auth.get_project_id(*args, **kwargs)

    def get_sp_auth_url(self, *args, **kwargs):
        return self.user_auth.get_sp_auth_url(*args, **kwargs)

    def get_sp_url(self, *args, **kwargs):
        return self.user_auth.get_sp_url(*args, **kwargs)
