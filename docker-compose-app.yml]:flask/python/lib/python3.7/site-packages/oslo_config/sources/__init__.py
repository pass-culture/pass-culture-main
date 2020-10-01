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
Oslo.config's primary source of configuration data are plaintext, INI-like
style, configuration files. With the addition of backend drivers support,
it is possible to store configuration data in different places and with
different formats, as long as there exists a proper driver to connect to those
external sources and provide a way to fetch configuration values from them.

A backend driver implementation is divided in two main classes, a driver
class of type :class:`ConfigurationSourceDriver` and a configuration source
class of type :class:`ConfigurationSource`.

**IMPORTANT:** At this point, all backend drivers are only able to provide
immutable values. This protects applications and services from having options
in external sources mutated when they reload configuration files.
"""

import abc


# We cannot use None as a sentinel indicating a missing value because it
# may be a valid value or default, so we use a custom singleton instead.
_NoValue = object()


class ConfigurationSourceDriver(object, metaclass=abc.ABCMeta):
    """A backend driver option for oslo.config.

    For each group name listed in **config_source** on the **DEFAULT** group,
    a :class:`ConfigurationSourceDriver` is responsible for creating one new
    instance of a :class:`ConfigurationSource`. The proper driver class to be
    used is selected based on the **driver** option inside each one of the
    groups listed in config_source and loaded through entry points managed by
    stevedore using the namespace oslo.config.driver::

        [DEFAULT]
        config_source = source1
        config_source = source2
        ...

        [source1]
        driver = remote_file
        ...

        [source2]
        driver = castellan
        ...

    Each specific driver knows all the available options to properly instatiate
    a ConfigurationSource using the values comming from the given group in the
    open_source_from_opt_group() method and is able to generate sample config
    through the list_options_for_discovery() method.

    """

    @abc.abstractmethod
    def open_source_from_opt_group(self, conf, group_name):
        """Return an open configuration source.

        Uses group_name to find the configuration settings for the new
        source and then open the configuration source and return it.

        If a source cannot be open, raises an appropriate exception.

        :param conf: The active configuration option handler from which
                     to seek configuration values.
        :type conf: ConfigOpts
        :param group_name: The configuration option group name where the
                           options for the source are stored.
        :type group_name: str
        :returns: an instance of a subclass of ConfigurationSource
        """

    @abc.abstractmethod
    def list_options_for_discovery(self):
        """Return the list of options available to configure a new source.

        Drivers should advertise all supported options in this method
        for the purpose of sample generation by oslo-config-generator.

        For an example on how to implement this method
        you can check the **remote_file** driver at
        oslo_config.sources._uri.URIConfigurationSourceDriver.

        :returns: a list of supported options of a ConfigurationSource.
        """


class ConfigurationSource(object, metaclass=abc.ABCMeta):
    """A configuration source option for oslo.config.

    A configuration source is able to fetch configuration values based on
    a (group, option) key from an external source that supports key-value
    mapping such as INI files, key-value stores, secret stores, and so on.

    """

    @abc.abstractmethod
    def get(self, group_name, option_name, opt):
        """Return the value of the option from the group.

        :param group_name: Name of the group.
        :type group_name: str
        :param option_name: Name of the option.
        :type option_name: str
        :param opt: The option definition.
        :type opt: Opt
        :returns: A tuple (value, location) where value is the option value
                  or oslo_config.sources._NoValue if the (group, option) is
                  not present in the source, and location is a LocationInfo.
        """
