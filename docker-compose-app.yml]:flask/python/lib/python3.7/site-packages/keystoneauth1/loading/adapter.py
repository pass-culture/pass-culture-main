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

from keystoneauth1 import adapter
from keystoneauth1.loading import _utils
from keystoneauth1.loading import base


__all__ = ('register_argparse_arguments',
           'register_service_argparse_arguments',
           'register_conf_options',
           'load_from_conf_options',
           'get_conf_options')


class Adapter(base.BaseLoader):

    @property
    def plugin_class(self):
        return adapter.Adapter

    def get_options(self):
        return []

    @staticmethod
    def get_conf_options(include_deprecated=True, deprecated_opts=None):
        """Get oslo_config options that are needed for a :py:class:`.Adapter`.

        These may be useful without being registered for config file generation
        or to manipulate the options before registering them yourself.

        The options that are set are:
            :service_type:      The default service_type for URL discovery.
            :service_name:      The default service_name for URL discovery.
            :interface:         The default interface for URL discovery.
                                (deprecated)
            :valid_interfaces:  List of acceptable interfaces for URL
                                discovery. Can be a list of any of
                                'public', 'internal' or 'admin'.
            :region_name:       The default region_name for URL discovery.
            :endpoint_override: Always use this endpoint URL for requests
                                for this client.
            :version:           The minimum version restricted to a given Major
                                API. Mutually exclusive with min_version and
                                max_version.
            :min_version:       The minimum major version of a given API,
                                intended to be used as the lower bound of a
                                range with max_version. Mutually exclusive with
                                version. If min_version is given with no
                                max_version it is as if max version is
                                'latest'.
            :max_version:       The maximum major version of a given API,
                                intended to be used as the upper bound of a
                                range with min_version. Mutually exclusive with
                                version.

        :param include_deprecated: If True (the default, for backward
                                   compatibility), deprecated options are
                                   included in the result.  If False, they are
                                   excluded.
        :param dict deprecated_opts: Deprecated options that should be included
             in the definition of new options. This should be a dict from the
             name of the new option to a list of oslo.DeprecatedOpts that
             correspond to the new option. (optional)

             For example, to support the ``api_endpoint`` option pointing to
             the new ``endpoint_override`` option name::

                 old_opt = oslo_cfg.DeprecatedOpt('api_endpoint', 'old_group')
                 deprecated_opts={'endpoint_override': [old_opt]}

        :returns: A list of oslo_config options.
        """
        cfg = _utils.get_oslo_config()

        if deprecated_opts is None:
            deprecated_opts = {}

        # This is goofy, but need to support hyphens *or* underscores
        deprecated_opts = {name.replace('_', '-'): opt
                           for name, opt in deprecated_opts.items()}

        opts = [cfg.StrOpt('service-type',
                           deprecated_opts=deprecated_opts.get('service-type'),
                           help='The default service_type for endpoint URL '
                                'discovery.'),
                cfg.StrOpt('service-name',
                           deprecated_opts=deprecated_opts.get('service-name'),
                           help='The default service_name for endpoint URL '
                                'discovery.'),
                cfg.ListOpt('valid-interfaces',
                            deprecated_opts=deprecated_opts.get(
                                'valid-interfaces'),
                            help='List of interfaces, in order of preference, '
                                 'for endpoint URL.'),
                cfg.StrOpt('region-name',
                           deprecated_opts=deprecated_opts.get('region-name'),
                           help='The default region_name for endpoint URL '
                                'discovery.'),
                cfg.StrOpt('endpoint-override',
                           deprecated_opts=deprecated_opts.get(
                               'endpoint-override'),
                           help='Always use this endpoint URL for requests '
                                'for this client. NOTE: The unversioned '
                                'endpoint should be specified here; to '
                                'request a particular API version, use the '
                                '`version`, `min-version`, and/or '
                                '`max-version` options.'),
                cfg.StrOpt('version',
                           deprecated_opts=deprecated_opts.get('version'),
                           help='Minimum Major API version within a given '
                                'Major API version for endpoint URL '
                                'discovery. Mutually exclusive with '
                                'min_version and max_version'),
                cfg.StrOpt('min-version',
                           deprecated_opts=deprecated_opts.get('min-version'),
                           help='The minimum major version of a given API, '
                                'intended to be used as the lower bound of a '
                                'range with max_version. Mutually exclusive '
                                'with version. If min_version is given with '
                                'no max_version it is as if max version is '
                                '"latest".'),
                cfg.StrOpt('max-version',
                           deprecated_opts=deprecated_opts.get('max-version'),
                           help='The maximum major version of a given API, '
                                'intended to be used as the upper bound of a '
                                'range with min_version. Mutually exclusive '
                                'with version.'),
                cfg.IntOpt('connect-retries',
                           deprecated_opts=deprecated_opts.get(
                               'connect-retries'),
                           help='The maximum number of retries that should be '
                                'attempted for connection errors.'),
                cfg.FloatOpt('connect-retry-delay',
                             deprecated_opts=deprecated_opts.get(
                                 'connect-retry-delay'),
                             help='Delay (in seconds) between two retries '
                                  'for connection errors. If not set, '
                                  'exponential retry starting with 0.5 '
                                  'seconds up to a maximum of 60 seconds '
                                  'is used.'),
                cfg.IntOpt('status-code-retries',
                           deprecated_opts=deprecated_opts.get(
                               'status-code-retries'),
                           help='The maximum number of retries that should be '
                                'attempted for retriable HTTP status codes.'),
                cfg.FloatOpt('status-code-retry-delay',
                             deprecated_opts=deprecated_opts.get(
                                 'status-code-retry-delay'),
                             help='Delay (in seconds) between two retries '
                                  'for retriable status codes. If not set, '
                                  'exponential retry starting with 0.5 '
                                  'seconds up to a maximum of 60 seconds '
                                  'is used.'),
                ]
        if include_deprecated:
            opts += [
                cfg.StrOpt('interface',
                           help='The default interface for endpoint URL '
                                'discovery.',
                           deprecated_for_removal=True,
                           deprecated_reason='Using valid-interfaces is'
                                             ' preferrable because it is'
                                             ' capable of accepting a list of'
                                             ' possible interfaces.'),
            ]
        return opts

    def register_conf_options(self, conf, group, include_deprecated=True,
                              deprecated_opts=None):
        """Register the oslo_config options that are needed for an Adapter.

        The options that are set are:
            :service_type:        The default service_type for URL discovery.
            :service_name:        The default service_name for URL discovery.
            :interface:           The default interface for URL discovery.
                                  (deprecated)
            :valid_interfaces:    List of acceptable interfaces for URL
                                  discovery. Can be a list of any of
                                  'public', 'internal' or 'admin'.
            :region_name:         The default region_name for URL discovery.
            :endpoint_override:   Always use this endpoint URL for requests
                                  for this client.
            :version:             The minimum version restricted to a given
                                  Major API. Mutually exclusive with
                                  min_version and max_version.
            :min_version:         The minimum major version of a given API,
                                  intended to be used as the lower bound of a
                                  range with max_version. Mutually exclusive
                                  with version. If min_version is given with no
                                  max_version it is as if max version is
                                  'latest'.
            :max_version:         The maximum major version of a given API,
                                  intended to be used as the upper bound of a
                                  range with min_version. Mutually exclusive
                                  with version.
            :connect_retries:     The maximum number of retries that should be
                                  attempted for connection errors.
            :status_code_retries: The maximum number of retries that should be
                                  attempted for retriable HTTP status codes.

        :param oslo_config.Cfg conf: config object to register with.
        :param string group: The ini group to register options in.
        :param include_deprecated: If True (the default, for backward
                                   compatibility), deprecated options are
                                   registered.  If False, they are excluded.
        :param dict deprecated_opts: Deprecated options that should be included
             in the definition of new options. This should be a dict from the
             name of the new option to a list of oslo.DeprecatedOpts that
             correspond to the new option. (optional)

             For example, to support the ``api_endpoint`` option pointing to
             the new ``endpoint_override`` option name::

                 old_opt = oslo_cfg.DeprecatedOpt('api_endpoint', 'old_group')
                 deprecated_opts={'endpoint_override': [old_opt]}

        :returns: The list of options that was registered.
        """
        opts = self.get_conf_options(include_deprecated=include_deprecated,
                                     deprecated_opts=deprecated_opts)
        conf.register_group(_utils.get_oslo_config().OptGroup(group))
        conf.register_opts(opts, group=group)
        return opts

    def load_from_conf_options(self, conf, group, **kwargs):
        """Create an Adapter object from an oslo_config object.

        The options must have been previously registered with
        register_conf_options.

        :param oslo_config.Cfg conf: config object to register with.
        :param string group: The ini group to register options in.
        :param dict kwargs: Additional parameters to pass to Adapter
                            construction.
        :returns: A new Adapter object.
        :rtype: :py:class:`.Adapter`
        """
        c = conf[group]
        process_conf_options(c, kwargs)
        return self.load_from_options(**kwargs)


def process_conf_options(confgrp, kwargs):
    """Set Adapter constructor kwargs based on conf options.

    :param oslo_config.cfg.GroupAttr confgrp: Config object group containing
            options to inspect.
    :param dict kwargs: Keyword arguments suitable for the constructor of
            keystoneauth1.adapter.Adapter. Will be modified by this method.
            Values already set remain unaffected.
    :raise TypeError: If invalid conf option values or combinations are found.
    """
    if confgrp.valid_interfaces and getattr(confgrp, 'interface', None):
        raise TypeError("interface and valid_interfaces are mutually"
                        " exclusive. Please use valid_interfaces.")
    if confgrp.valid_interfaces:
        for iface in confgrp.valid_interfaces:
            if iface not in ('public', 'internal', 'admin'):
                # TODO(efried): s/valies/values/ - are we allowed to fix this?
                raise TypeError("'{iface}' is not a valid value for"
                                " valid_interfaces. Valid valies are"
                                " public, internal or admin".format(
                                    iface=iface))
        kwargs.setdefault('interface', confgrp.valid_interfaces)
    elif hasattr(confgrp, 'interface'):
        kwargs.setdefault('interface', confgrp.interface)
    kwargs.setdefault('service_type', confgrp.service_type)
    kwargs.setdefault('service_name', confgrp.service_name)
    kwargs.setdefault('region_name', confgrp.region_name)
    kwargs.setdefault('endpoint_override', confgrp.endpoint_override)
    kwargs.setdefault('version', confgrp.version)
    kwargs.setdefault('min_version', confgrp.min_version)
    kwargs.setdefault('max_version', confgrp.max_version)
    if kwargs['version'] and (
            kwargs['max_version'] or kwargs['min_version']):
        raise TypeError(
            "version is mutually exclusive with min_version and"
            " max_version")
    kwargs.setdefault('connect_retries', confgrp.connect_retries)
    kwargs.setdefault('connect_retry_delay', confgrp.connect_retry_delay)
    kwargs.setdefault('status_code_retries', confgrp.status_code_retries)
    kwargs.setdefault('status_code_retry_delay',
                      confgrp.status_code_retry_delay)


def register_argparse_arguments(*args, **kwargs):
    return adapter.register_adapter_argparse_arguments(*args, **kwargs)


def register_service_argparse_arguments(*args, **kwargs):
    return adapter.register_service_adapter_argparse_arguments(*args, **kwargs)


def register_conf_options(*args, **kwargs):
    return Adapter().register_conf_options(*args, **kwargs)


def load_from_conf_options(*args, **kwargs):
    return Adapter().load_from_conf_options(*args, **kwargs)


def get_conf_options(*args, **kwargs):
    return Adapter.get_conf_options(*args, **kwargs)
