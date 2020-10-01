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

import copy
import inspect

from oslo_config import cfg

import stevedore


def list_opts():
    default_config_files = [
        '~/.project/project.conf',
        '~/project.conf',
        '/etc/project/project.conf',
        '/etc/project.conf',
    ]
    default_config_dirs = [
        '~/.project/project.conf.d/',
        '~/project.conf.d/',
        '/etc/project/project.conf.d/',
        '/etc/project.conf.d/',
    ]
    options = [(None, cfg.ConfigOpts._list_options_for_discovery(
        default_config_files,
        default_config_dirs,
    ))]

    ext_mgr = stevedore.ExtensionManager(
        "oslo.config.driver",
        invoke_on_load=True)

    source_names = ext_mgr.names()
    for source_name in source_names:
        source = ext_mgr[source_name].obj
        source_options = copy.deepcopy(source.list_options_for_discovery())
        source_description = inspect.getdoc(source)
        source_options.insert(
            0,
            cfg.StrOpt(
                name='driver',
                sample_default=source_name,
                help=cfg._SOURCE_DRIVER_OPTION_HELP,
            )
        )
        group_name = 'sample_{}_source'.format(source_name)
        group_help = 'Example of using a {} source'.format(source_name)
        if source_description:
            group_help = '{}\n\n{}: {}'.format(
                group_help,
                source_name,
                source_description,
            )
        group = cfg.OptGroup(
            name=group_name,
            help=group_help,
            driver_option='driver',
            dynamic_group_owner='config_source',
        )
        options.append((group, source_options))

    return options
