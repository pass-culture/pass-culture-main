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
r"""
Environment
-----------

The **environment** backend driver provides a method of accessing
configuration data in environment variables. It is enabled by default
and requires no additional configuration to use. The environment is
checked after command line options, but before configuration files.


Environment variables are checked for any configuration data. The variable
names take the form:

* A prefix of ``OS_``
* The group name, uppercased
* Separated from the option name by a `__` (double underscore)
* Followed by the name

For an option that looks like this in the usual INI format::

    [placement_database]
    connection = sqlite:///

the corresponding environment variable would be
``OS_PLACEMENT_DATABASE__CONNECTION``.

The Driver Class
================

.. autoclass:: EnvironmentConfigurationSourceDriver

The Configuration Source Class
==============================

.. autoclass:: EnvironmentConfigurationSource

"""

import os

# Avoid circular import
import oslo_config.cfg
from oslo_config import sources


# In current practice this class is not used because the
# EnvironmentConfigurationSource is loaded by default, but we keep it
# here in case we choose to change that behavior in the future.
class EnvironmentConfigurationSourceDriver(sources.ConfigurationSourceDriver):
    """A backend driver for environment variables.

    This configuration source is available by default and does not need special
    configuration to use. The sample config is generated automatically but is
    not necessary.
    """

    def list_options_for_discovery(self):
        """There are no options for this driver."""
        return []

    def open_source_from_opt_group(self, conf, group_name):
        return EnvironmentConfigurationSource()


class EnvironmentConfigurationSource(sources.ConfigurationSource):
    """A configuration source for options in the environment."""

    @staticmethod
    def get_name(group_name, option_name):
        """Return the expected environment variable name for the given option.

        :param group_name: The group name or None. Defaults to 'DEFAULT' if
            None.
        :param option_name: The option name.
        :returns: Th expected environment variable name.
        """
        group_name = group_name or 'DEFAULT'
        return 'OS_{}__{}'.format(group_name.upper(), option_name.upper())

    def get(self, group_name, option_name, opt):
        env_name = self.get_name(group_name, option_name)
        try:
            value = os.environ[env_name]
            loc = oslo_config.cfg.LocationInfo(
                oslo_config.cfg.Locations.environment, env_name)
            return (value, loc)
        except KeyError:
            return (sources._NoValue, None)
