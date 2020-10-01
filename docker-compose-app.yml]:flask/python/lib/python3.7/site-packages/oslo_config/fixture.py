#
# Copyright 2013 Mirantis, Inc.
# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
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

import fixtures

from oslo_config import cfg


class Config(fixtures.Fixture):
    """Allows overriding configuration settings for the test.

    `conf` will be reset on cleanup.

    """

    def __init__(self, conf=cfg.CONF):
        self.conf = conf

    def setUp(self):
        super(Config, self).setUp()
        # NOTE(morganfainberg): unregister must be added to cleanup before
        # reset is because cleanup works in reverse order of registered items,
        # and a reset must occur before unregistering options can occur.
        self.addCleanup(self._reset_default_config_files)
        self.addCleanup(self._reset_default_config_dirs)
        self.addCleanup(self._unregister_config_opts)
        self.addCleanup(self.conf.reset)
        self._registered_config_opts = {}

        # Grab an old copy of the default config files/dirs - if it exists -
        # for subsequent cleanup.
        if hasattr(self.conf, 'default_config_files'):
            self._default_config_files = self.conf.default_config_files
        else:
            self._default_config_files = None

        if hasattr(self.conf, 'default_config_dirs'):
            self._default_config_dirs = self.conf.default_config_dirs
        else:
            self._default_config_dirs = None

    def config(self, **kw):
        """Override configuration values.

        The keyword arguments are the names of configuration options to
        override and their values.

        If a `group` argument is supplied, the overrides are applied to
        the specified configuration option group, otherwise the overrides
        are applied to the ``default`` group.

        """

        group = kw.pop('group', None)
        for k, v in kw.items():
            self.conf.set_override(k, v, group)

    def _unregister_config_opts(self):
        for group in self._registered_config_opts:
            self.conf.unregister_opts(self._registered_config_opts[group],
                                      group=group)

    def _reset_default_config_files(self):
        if not hasattr(self.conf, 'default_config_files'):
            return

        if self._default_config_files:
            self.conf.default_config_files = self._default_config_files
        else:
            # Delete, because we could conceivably begin with the property
            # being unset.
            self.conf.default_config_files = None

    def _reset_default_config_dirs(self):
        if not hasattr(self.conf, 'default_config_dirs'):
            return

        if self._default_config_dirs:
            self.conf.default_config_dirs = self._default_config_dirs
        else:
            # Delete, because we could conceivably begin with the property
            # being unset.
            self.conf.default_config_dirs = None

    def register_opt(self, opt, group=None):
        """Register a single option for the test run.

        Options registered in this manner will automatically be unregistered
        during cleanup.

        If a `group` argument is supplied, it will register the new option
        to that group, otherwise the option is registered to the ``default``
        group.
        """
        self.conf.register_opt(opt, group=group)
        self._registered_config_opts.setdefault(group, set()).add(opt)

    def register_opts(self, opts, group=None):
        """Register multiple options for the test run.

        This works in the same manner as register_opt() but takes a list of
        options as the first argument. All arguments will be registered to the
        same group if the ``group`` argument is supplied, otherwise all options
        will be registered to the ``default`` group.
        """
        for opt in opts:
            self.register_opt(opt, group=group)

    def register_cli_opt(self, opt, group=None):
        """Register a single CLI option for the test run.

        Options registered in this manner will automatically be unregistered
        during cleanup.

        If a `group` argument is supplied, it will register the new option
        to that group, otherwise the option is registered to the ``default``
        group.

        CLI options must be registered before the command line and config files
        are parsed. This is to ensure that all CLI options are shown in --help
        and option validation works as expected.
        """
        self.conf.register_cli_opt(opt, group=group)
        self._registered_config_opts.setdefault(group, set()).add(opt)

    def register_cli_opts(self, opts, group=None):
        """Register multiple CLI options for the test run.

        This works in the same manner as register_opt() but takes a list of
        options as the first argument. All arguments will be registered to the
        same group if the ``group`` argument is supplied, otherwise all options
        will be registered to the ``default`` group.

        CLI options must be registered before the command line and config files
        are parsed. This is to ensure that all CLI options are shown in --help
        and option validation works as expected.
        """
        for opt in opts:
            self.register_cli_opt(opt, group=group)

    def load_raw_values(self, group=None, **kwargs):
        """Load raw values into the configuration without registering them.

        This method adds a series of parameters into the current config
        instance, as if they had been loaded by a ConfigParser. This method
        does not require that you register the configuration options first,
        however the values loaded will not be accessible until you do.
        """

        # Make sure the namespace exists for our tests.
        if not self.conf._namespace:
            self.conf.__call__(args=[])

        # Default out the group name
        group = 'DEFAULT' if not group else group

        raw_config = dict()
        raw_config[group] = dict()
        for key, value in kwargs.items():
            # Parsed values are an array of raw strings.
            raw_config[group][key] = [str(value)]

        self.conf._namespace._add_parsed_config_file(
            '<memory>', raw_config, raw_config)

    def set_config_files(self, config_files):
        """Specify a list of config files to read.

        This method allows you to predefine the list of configuration files
        that are loaded by oslo_config. It will ensure that your tests do not
        attempt to autodetect, and accidentally pick up config files from
        locally installed services.
        """
        if not isinstance(config_files, list):
            raise AttributeError("Please pass a list() to set_config_files()")

        # Make sure the namespace exists for our tests.
        if not self.conf._namespace:
            self.conf.__call__(args=[])

        self.conf.default_config_files = config_files
        self.conf.reload_config_files()

    def set_config_dirs(self, config_dirs):
        """Specify a list of config dirs to read.

        This method allows you to predefine the list of configuration dirs
        that are loaded by oslo_config. It will ensure that your tests do not
        attempt to autodetect, and accidentally pick up config files from
        locally installed services.
        """
        if not isinstance(config_dirs, list):
            raise AttributeError("Please pass a list() to set_config_dirs()")

        # Make sure the namespace exists for our tests.
        if not self.conf._namespace:
            self.conf([])

        self.conf.default_config_dirs = config_dirs
        self.conf.reload_config_files()

    def set_default(self, name, default, group=None):
        """Set a default value for an option.

        This method is not necessarily meant to be invoked
        directly. It is here to allow the set_defaults() functions in
        various Oslo libraries to work with a Config fixture instead
        of a ConfigOpts instance.

        Use it like::

            class MyTest(testtools.TestCase):

                def setUp(self):
                    super(MyTest, self).setUp()
                    self.conf = self.useFixture(fixture.Config())

                def test_something(self):
                    some_library.set_defaults(self.conf, name='value')
                    some_library.do_something_exciting()

        """
        self.conf.set_default(name, default, group)
        self.addCleanup(self.conf.clear_default, name, group)
