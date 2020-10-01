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
from keystoneauth1 import loading


__all__ = ('MultiFactor', )


class MultiFactor(base.Auth):
    """A plugin for authenticating with multiple auth methods.

    :param string auth_url: Identity service endpoint for authentication.
    :param string auth_methods: names of the methods to authenticate with.
    :param string trust_id: Trust ID for trust scoping.
    :param string system_scope: System information to scope to.
    :param string domain_id: Domain ID for domain scoping.
    :param string domain_name: Domain name for domain scoping.
    :param string project_id: Project ID for project scoping.
    :param string project_name: Project name for project scoping.
    :param string project_domain_id: Project's domain ID for project.
    :param string project_domain_name: Project's domain name for project.
    :param bool reauthenticate: Allow fetching a new token if the current one
                                is going to expire. (optional) default True

    Also accepts various keyword args based on which methods are specified.
    """

    def __init__(self, auth_url, auth_methods, **kwargs):
        method_instances = []
        method_keys = set()
        for method in auth_methods:
            # Using the loaders we pull the related auth method class
            method_class = loading.get_plugin_loader(
                method).plugin_class._auth_method_class
            # We build some new kwargs for the method from required parameters
            method_kwargs = {}
            for key in method_class._method_parameters:
                # we add them to method_keys to pop later from global kwargs
                # rather than here as other methods may need them too
                method_keys.add(key)
                method_kwargs[key] = kwargs.get(key, None)
            # We initialize the method class using just required kwargs
            method_instances.append(method_class(**method_kwargs))
        # We now pop all the keys used for methods as otherwise they get passed
        # to the super class and throw errors
        for key in method_keys:
            kwargs.pop(key, None)
        super(MultiFactor, self).__init__(auth_url, method_instances, **kwargs)
