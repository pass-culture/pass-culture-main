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

# flake8: noqa: F405

from keystoneauth1.loading import adapter
from keystoneauth1.loading.base import *  # noqa
from keystoneauth1.loading import cli
from keystoneauth1.loading import conf
from keystoneauth1.loading.identity import *  # noqa
from keystoneauth1.loading.opts import *  # noqa
from keystoneauth1.loading import session


register_auth_argparse_arguments = cli.register_argparse_arguments
load_auth_from_argparse_arguments = cli.load_from_argparse_arguments

get_auth_common_conf_options = conf.get_common_conf_options
get_auth_plugin_conf_options = conf.get_plugin_conf_options
register_auth_conf_options = conf.register_conf_options
load_auth_from_conf_options = conf.load_from_conf_options

register_session_argparse_arguments = session.register_argparse_arguments
load_session_from_argparse_arguments = session.load_from_argparse_arguments
register_session_conf_options = session.register_conf_options
load_session_from_conf_options = session.load_from_conf_options
get_session_conf_options = session.get_conf_options

register_adapter_argparse_arguments = adapter.register_argparse_arguments
register_service_adapter_argparse_arguments = (
    adapter.register_service_argparse_arguments)
register_adapter_conf_options = adapter.register_conf_options
load_adapter_from_conf_options = adapter.load_from_conf_options
get_adapter_conf_options = adapter.get_conf_options


__all__ = (
    # loading.base
    'BaseLoader',
    'get_available_plugin_names',
    'get_available_plugin_loaders',
    'get_plugin_loader',
    'PLUGIN_NAMESPACE',

    # loading.identity
    'BaseIdentityLoader',
    'BaseV2Loader',
    'BaseV3Loader',
    'BaseFederationLoader',
    'BaseGenericLoader',

    # auth cli
    'register_auth_argparse_arguments',
    'load_auth_from_argparse_arguments',

    # auth conf
    'get_auth_common_conf_options',
    'get_auth_plugin_conf_options',
    'register_auth_conf_options',
    'load_auth_from_conf_options',

    # session
    'register_session_argparse_arguments',
    'load_session_from_argparse_arguments',
    'register_session_conf_options',
    'load_session_from_conf_options',
    'get_session_conf_options',

    # adapter
    'register_adapter_argparse_arguments',
    'register_service_adapter_argparse_arguments',
    'register_adapter_conf_options',
    'load_adapter_from_conf_options',
    'get_adapter_conf_options',

    # loading.opts
    'Opt',
)
