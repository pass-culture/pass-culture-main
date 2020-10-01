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

import abc

import six
import stevedore

from keystoneauth1 import exceptions

PLUGIN_NAMESPACE = 'keystoneauth1.plugin'


__all__ = ('get_available_plugin_names',
           'get_available_plugin_loaders',
           'get_plugin_loader',
           'get_plugin_options',
           'BaseLoader',
           'PLUGIN_NAMESPACE')


def _auth_plugin_available(ext):
    """Read the value of available for whether to load this plugin."""
    return ext.obj.available


def get_available_plugin_names():
    """Get the names of all the plugins that are available on the system.

    This is particularly useful for help and error text to prompt a user for
    example what plugins they may specify.

    :returns: A list of names.
    :rtype: frozenset
    """
    mgr = stevedore.EnabledExtensionManager(namespace=PLUGIN_NAMESPACE,
                                            check_func=_auth_plugin_available,
                                            invoke_on_load=True,
                                            propagate_map_exceptions=True)
    return frozenset(mgr.names())


def get_available_plugin_loaders():
    """Retrieve all the plugin classes available on the system.

    :returns: A dict with plugin entrypoint name as the key and the plugin
              loader as the value.
    :rtype: dict
    """
    mgr = stevedore.EnabledExtensionManager(namespace=PLUGIN_NAMESPACE,
                                            check_func=_auth_plugin_available,
                                            invoke_on_load=True,
                                            propagate_map_exceptions=True)

    return dict(mgr.map(lambda ext: (ext.entry_point.name, ext.obj)))


def get_plugin_loader(name):
    """Retrieve a plugin class by its entrypoint name.

    :param str name: The name of the object to get.

    :returns: An auth plugin class.
    :rtype: :py:class:`keystoneauth1.loading.BaseLoader`

    :raises keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin:
        if a plugin cannot be created.
    """
    try:
        mgr = stevedore.DriverManager(namespace=PLUGIN_NAMESPACE,
                                      invoke_on_load=True,
                                      name=name)
    except RuntimeError:
        raise exceptions.NoMatchingPlugin(name)

    return mgr.driver


def get_plugin_options(name):
    """Get the options for a specific plugin.

    This will be the list of options that is registered and loaded by the
    specified plugin.

    :returns: A list of :py:class:`keystoneauth1.loading.Opt` options.

    :raises keystoneauth1.exceptions.auth_plugins.NoMatchingPlugin:
        if a plugin cannot be created.
    """
    return get_plugin_loader(name).get_options()


@six.add_metaclass(abc.ABCMeta)
class BaseLoader(object):

    @property
    def plugin_class(self):
        raise NotImplementedError()

    def create_plugin(self, **kwargs):
        """Create a plugin from the options available for the loader.

        Given the options that were specified by the loader create an
        appropriate plugin. You can override this function in your loader.

        This used to be specified by providing the plugin_class property and
        this is still supported, however specifying a property didn't let you
        choose a plugin type based upon the options that were presented.

        Override this function if you wish to return different plugins based on
        the options presented, otherwise you can simply provide the
        plugin_class property.

        Added 2.9
        """
        return self.plugin_class(**kwargs)

    @abc.abstractmethod
    def get_options(self):
        """Return the list of parameters associated with the auth plugin.

        This list may be used to generate CLI or config arguments.

        :returns: A list of Param objects describing available plugin
                  parameters.
        :rtype: list
        """
        return []

    @property
    def available(self):
        """Return if the plugin is available for loading.

        If a plugin is missing dependencies or for some other reason should not
        be available to the current system it should override this property and
        return False to exclude itself from the plugin list.

        :rtype: bool
        """
        return True

    def load_from_options(self, **kwargs):
        """Create a plugin from the arguments retrieved from get_options.

        A client can override this function to do argument validation or to
        handle differences between the registered options and what is required
        to create the plugin.
        """
        missing_required = [o for o in self.get_options()
                            if o.required and kwargs.get(o.dest) is None]

        if missing_required:
            raise exceptions.MissingRequiredOptions(missing_required)

        return self.create_plugin(**kwargs)

    def load_from_options_getter(self, getter, **kwargs):
        """Load a plugin from getter function that returns appropriate values.

        To handle cases other than the provided CONF and CLI loading you can
        specify a custom loader function that will be queried for the option
        value.
        The getter is a function that takes a
        :py:class:`keystoneauth1.loading.Opt` and returns a value to load with.

        :param getter: A function that returns a value for the given opt.
        :type getter: callable

        :returns: An authentication Plugin.
        :rtype: :py:class:`keystoneauth1.plugin.BaseAuthPlugin`
        """
        for opt in (o for o in self.get_options() if o.dest not in kwargs):
            val = getter(opt)
            if val is not None:
                val = opt.type(val)
            kwargs[opt.dest] = val

        return self.load_from_options(**kwargs)
