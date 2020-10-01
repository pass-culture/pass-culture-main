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

from keystoneauth1 import exceptions
from keystoneauth1.loading import base
from keystoneauth1.loading import opts

__all__ = ('BaseIdentityLoader',
           'BaseV2Loader',
           'BaseV3Loader',
           'BaseFederationLoader',
           'BaseGenericLoader')


class BaseIdentityLoader(base.BaseLoader):
    """Base Option handling for identity plugins.

    This class defines options and handling that should be common across all
    plugins that are developed against the OpenStack identity service. It
    provides the options expected by the
    :py:class:`keystoneauth1.identity.BaseIdentityPlugin` class.
    """

    def get_options(self):
        options = super(BaseIdentityLoader, self).get_options()

        options.extend([
            opts.Opt('auth-url',
                     required=True,
                     help='Authentication URL'),
        ])

        return options


class BaseV2Loader(BaseIdentityLoader):
    """Base Option handling for identity plugins.

    This class defines options and handling that should be common to the V2
    identity API. It provides the options expected by the
    :py:class:`keystoneauth1.identity.v2.Auth` class.
    """

    def get_options(self):
        options = super(BaseV2Loader, self).get_options()

        options.extend([
            opts.Opt('tenant-id', help='Tenant ID'),
            opts.Opt('tenant-name', help='Tenant Name'),
            opts.Opt('trust-id', help='Trust ID'),
        ])

        return options


class BaseV3Loader(BaseIdentityLoader):
    """Base Option handling for identity plugins.

    This class defines options and handling that should be common to the V3
    identity API. It provides the options expected by the
    :py:class:`keystoneauth1.identity.v3.Auth` class.
    """

    def get_options(self):
        options = super(BaseV3Loader, self).get_options()

        options.extend([
            opts.Opt('system-scope', help='Scope for system operations'),
            opts.Opt('domain-id', help='Domain ID to scope to'),
            opts.Opt('domain-name', help='Domain name to scope to'),
            opts.Opt('project-id', help='Project ID to scope to'),
            opts.Opt('project-name', help='Project name to scope to'),
            opts.Opt('project-domain-id',
                     help='Domain ID containing project'),
            opts.Opt('project-domain-name',
                     help='Domain name containing project'),
            opts.Opt('trust-id', help='Trust ID'),
        ])

        return options

    def load_from_options(self, **kwargs):
        if (kwargs.get('project_name') and
                not (kwargs.get('project_domain_name') or
                     kwargs.get('project_domain_id'))):
            m = "You have provided a project_name. In the V3 identity API a " \
                "project_name is only unique within a domain so you must " \
                "also provide either a project_domain_id or " \
                "project_domain_name."
            raise exceptions.OptionError(m)

        return super(BaseV3Loader, self).load_from_options(**kwargs)


class BaseFederationLoader(BaseV3Loader):
    """Base Option handling for federation plugins.

    This class defines options and handling that should be common to the V3
    identity federation API. It provides the options expected by the
    :py:class:`keystoneauth1.identity.v3.FederationBaseAuth` class.
    """

    def get_options(self):
        options = super(BaseFederationLoader, self).get_options()

        options.extend([
            opts.Opt('identity-provider',
                     help="Identity Provider's name",
                     required=True),
            opts.Opt('protocol',
                     help='Protocol for federated plugin',
                     required=True),
        ])

        return options


class BaseGenericLoader(BaseIdentityLoader):
    """Base Option handling for generic plugins.

    This class defines options and handling that should be common to generic
    plugins. These plugins target the OpenStack identity service however are
    designed to be independent of API version. It provides the options expected
    by the :py:class:`keystoneauth1.identity.v3.BaseGenericPlugin` class.
    """

    def get_options(self):
        options = super(BaseGenericLoader, self).get_options()

        options.extend([
            opts.Opt('system-scope', help='Scope for system operations'),
            opts.Opt('domain-id', help='Domain ID to scope to'),
            opts.Opt('domain-name', help='Domain name to scope to'),
            opts.Opt('project-id', help='Project ID to scope to',
                     deprecated=[opts.Opt('tenant-id')]),
            opts.Opt('project-name', help='Project name to scope to',
                     deprecated=[opts.Opt('tenant-name')]),
            opts.Opt('project-domain-id',
                     help='Domain ID containing project'),
            opts.Opt('project-domain-name',
                     help='Domain name containing project'),
            opts.Opt('trust-id', help='Trust ID'),
            opts.Opt('default-domain-id',
                     help='Optional domain ID to use with v3 and v2 '
                          'parameters. It will be used for both the user '
                          'and project domain in v3 and ignored in '
                          'v2 authentication.'),
            opts.Opt('default-domain-name',
                     help='Optional domain name to use with v3 API and v2 '
                          'parameters. It will be used for both the user '
                          'and project domain in v3 and ignored in '
                          'v2 authentication.'),
        ])

        return options
