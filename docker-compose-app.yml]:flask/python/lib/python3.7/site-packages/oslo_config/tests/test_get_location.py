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

import io
import tempfile
import textwrap

from oslotest import base

from oslo_config import cfg


class TestConfigOpts(cfg.ConfigOpts):
    def __call__(self, args=None, default_config_files=[],
                 default_config_dirs=[]):
        return cfg.ConfigOpts.__call__(
            self,
            args=args,
            prog='test',
            version='1.0',
            usage='%(prog)s FOO BAR',
            description='somedesc',
            epilog='tepilog',
            default_config_files=default_config_files,
            default_config_dirs=default_config_dirs,
            validate_default_values=True)


class LocationTestCase(base.BaseTestCase):

    def test_user_controlled(self):
        self.assertTrue(cfg.Locations.user.is_user_controlled)
        self.assertTrue(cfg.Locations.command_line.is_user_controlled)

    def test_not_user_controlled(self):
        self.assertFalse(cfg.Locations.opt_default.is_user_controlled)
        self.assertFalse(cfg.Locations.set_default.is_user_controlled)
        self.assertFalse(cfg.Locations.set_override.is_user_controlled)


class GetLocationTestCase(base.BaseTestCase):

    def setUp(self):
        super(GetLocationTestCase, self).setUp()

        def _clear():
            cfg._show_caller_details = False
        self.addCleanup(_clear)
        cfg._show_caller_details = True

        self.conf = TestConfigOpts()
        self.normal_opt = cfg.StrOpt(
            'normal_opt',
            default='normal_opt_default',
        )
        self.conf.register_opt(self.normal_opt)
        self.cli_opt = cfg.StrOpt(
            'cli_opt',
            default='cli_opt_default',
        )
        self.conf.register_cli_opt(self.cli_opt)
        self.group_opt = cfg.StrOpt(
            'group_opt',
            default='group_opt_default',
        )
        self.conf.register_opt(self.group_opt, group='group')

    def test_opt_default(self):
        self.conf([])
        loc = self.conf.get_location('normal_opt')
        self.assertEqual(
            cfg.Locations.opt_default,
            loc.location,
        )
        self.assertIn('test_get_location.py', loc.detail)

    def test_set_default_on_config_opt(self):
        self.conf.set_default('normal_opt', self.id())
        self.conf([])
        loc = self.conf.get_location('normal_opt')
        self.assertEqual(
            cfg.Locations.set_default,
            loc.location,
        )
        self.assertIn('test_get_location.py', loc.detail)

    def test_set_defaults_func(self):
        cfg.set_defaults([self.normal_opt], normal_opt=self.id())
        self.conf([])
        loc = self.conf.get_location('normal_opt')
        self.assertEqual(
            cfg.Locations.set_default,
            loc.location,
        )
        self.assertIn('test_get_location.py', loc.detail)

    def test_set_override(self):
        self.conf.set_override('normal_opt', self.id())
        self.conf([])
        loc = self.conf.get_location('normal_opt')
        self.assertEqual(
            cfg.Locations.set_override,
            loc.location,
        )
        self.assertIn('test_get_location.py', loc.detail)

    def test_user_cli(self):
        filename = self._write_opt_to_tmp_file(
            'DEFAULT', 'unknown_opt', self.id())
        self.conf(['--config-file', filename,
                   '--cli_opt', 'blah'])
        loc = self.conf.get_location('cli_opt')
        self.assertEqual(
            cfg.Locations.command_line,
            loc.location,
        )

    def test_default_cli(self):
        filename = self._write_opt_to_tmp_file(
            'DEFAULT', 'unknown_opt', self.id())
        self.conf(['--config-file', filename])
        loc = self.conf.get_location('cli_opt')
        self.assertEqual(
            cfg.Locations.opt_default,
            loc.location,
        )

    def _write_opt_to_tmp_file(self, group, option, value):
        filename = tempfile.mktemp()
        with io.open(filename, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent(u'''
            [{group}]
            {option} = {value}
            ''').format(
                group=group,
                option=option,
                value=value,
            ))
        return filename

    def test_user_cli_opt_in_file(self):
        filename = self._write_opt_to_tmp_file(
            'DEFAULT', 'cli_opt', self.id())
        self.conf(['--config-file', filename])
        loc = self.conf.get_location('cli_opt')
        self.assertEqual(
            cfg.Locations.user,
            loc.location,
        )
        self.assertEqual(
            filename,
            loc.detail,
        )

    def test_user_file(self):
        filename = self._write_opt_to_tmp_file(
            'DEFAULT', 'normal_opt', self.id())
        self.conf(['--config-file', filename])
        loc = self.conf.get_location('normal_opt')
        self.assertEqual(
            cfg.Locations.user,
            loc.location,
        )
        self.assertEqual(
            filename,
            loc.detail,
        )

    def test_duplicate_registration(self):
        # NOTE(dhellmann): The ZFS driver in Cinder uses multiple Opt
        # instances with the same settings but in different
        # modules. We don't want to break that case with the option
        # location stuff, so we need to test that it works. To
        # reproduce that test we have to simulate the option being
        # created in a different file, so we create a new Opt instance
        # and replace its _set_location data.
        dupe_opt = cfg.StrOpt(
            'normal_opt',
            default='normal_opt_default',
        )
        dupe_opt._set_location = cfg.LocationInfo(
            cfg.Locations.opt_default,
            'an alternative file',
        )
        # We expect register_opt() to return False to indicate that
        # the option was already registered.
        self.assertFalse(self.conf.register_opt(dupe_opt))

    def test_group_opt(self):
        self.conf([])
        loc = self.conf.get_location('group_opt', 'group')
        self.assertEqual(
            cfg.Locations.opt_default,
            loc.location,
        )
        self.assertIn('test_get_location.py', loc.detail)
