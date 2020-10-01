# Copyright 2014 Red Hat, Inc.
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

import argparse
import errno
import functools
import io
import logging
import os
import shutil
import sys
import tempfile
from unittest import mock

import fixtures
from oslotest import base
import testscenarios

from oslo_config import cfg
from oslo_config import types

load_tests = testscenarios.load_tests_apply_scenarios


class ExceptionsTestCase(base.BaseTestCase):

    def test_error(self):
        msg = str(cfg.Error('foobar'))
        self.assertEqual('foobar', msg)

    def test_args_already_parsed_error(self):
        msg = str(cfg.ArgsAlreadyParsedError('foobar'))
        self.assertEqual('arguments already parsed: foobar', msg)

    def test_no_such_opt_error(self):
        msg = str(cfg.NoSuchOptError('foo'))
        self.assertEqual('no such option foo in group [DEFAULT]', msg)

    def test_no_such_opt_error_with_group(self):
        msg = str(cfg.NoSuchOptError('foo', cfg.OptGroup('bar')))
        self.assertEqual('no such option foo in group [bar]', msg)

    def test_no_such_group_error(self):
        msg = str(cfg.NoSuchGroupError('bar'))
        self.assertEqual('no such group [bar]', msg)

    def test_duplicate_opt_error(self):
        msg = str(cfg.DuplicateOptError('foo'))
        self.assertEqual('duplicate option: foo', msg)

    def test_required_opt_error(self):
        msg = str(cfg.RequiredOptError('foo'))
        self.assertEqual('value required for option foo in group [DEFAULT]',
                         msg)

    def test_required_opt_error_with_group(self):
        msg = str(cfg.RequiredOptError('foo', cfg.OptGroup('bar')))
        self.assertEqual('value required for option foo in group [bar]', msg)

    def test_template_substitution_error(self):
        msg = str(cfg.TemplateSubstitutionError('foobar'))
        self.assertEqual('template substitution error: foobar', msg)

    def test_config_files_not_found_error(self):
        msg = str(cfg.ConfigFilesNotFoundError(['foo', 'bar']))
        self.assertEqual('Failed to find some config files: foo,bar', msg)

    def test_config_files_permission_denied_error(self):
        msg = str(cfg.ConfigFilesPermissionDeniedError(['foo', 'bar']))
        self.assertEqual('Failed to open some config files: foo,bar', msg)

    def test_config_dir_not_found_error(self):
        msg = str(cfg.ConfigDirNotFoundError('foobar'))
        self.assertEqual('Failed to read config file directory: foobar', msg)

    def test_config_file_parse_error(self):
        msg = str(cfg.ConfigFileParseError('foo', 'foobar'))
        self.assertEqual('Failed to parse foo: foobar', msg)


class BaseTestCase(base.BaseTestCase):

    class TestConfigOpts(cfg.ConfigOpts):
        def __call__(self, args=None, default_config_files=[],
                     default_config_dirs=[], usage=None):
            return cfg.ConfigOpts.__call__(
                self,
                args=args,
                prog='test',
                version='1.0',
                usage=usage,
                description='somedesc',
                epilog='tepilog',
                default_config_files=default_config_files,
                default_config_dirs=default_config_dirs,
                validate_default_values=True)

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.useFixture(fixtures.NestedTempfile())
        self.conf = self.TestConfigOpts()

        self.tempdirs = []

    def create_tempfiles(self, files, ext='.conf'):
        tempfiles = []
        for (basename, contents) in files:
            if not os.path.isabs(basename):
                # create all the tempfiles in a tempdir
                tmpdir = tempfile.mkdtemp()
                path = os.path.join(tmpdir, basename + ext)
                # the path can start with a subdirectory so create
                # it if it doesn't exist yet
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
            else:
                path = basename + ext
            fd = os.open(path, os.O_CREAT | os.O_WRONLY)
            tempfiles.append(path)
            try:
                os.write(fd, contents.encode('utf-8'))
            finally:
                os.close(fd)
        return tempfiles


class UsageTestCase(BaseTestCase):

    def test_print_usage(self):
        f = io.StringIO()
        self.conf([])
        self.conf.print_usage(file=f)
        self.assertIn(
            'usage: test [-h] [--config-dir DIR] [--config-file PATH] '
            '[--version]',
            f.getvalue())
        self.assertNotIn('somedesc', f.getvalue())
        self.assertNotIn('tepilog', f.getvalue())
        self.assertNotIn('optional:', f.getvalue())

    def test_print_custom_usage(self):
        conf = self.TestConfigOpts()

        self.tempdirs = []
        f = io.StringIO()
        conf([], usage='%(prog)s FOO BAR')
        conf.print_usage(file=f)
        self.assertIn('usage: test FOO BAR', f.getvalue())
        self.assertNotIn('somedesc', f.getvalue())
        self.assertNotIn('tepilog', f.getvalue())
        self.assertNotIn('optional:', f.getvalue())

    def test_print_help(self):
        f = io.StringIO()
        self.conf([])
        self.conf.print_help(file=f)
        self.assertIn(
            'usage: test [-h] [--config-dir DIR] [--config-file PATH] '
            '[--version]',
            f.getvalue())
        self.assertIn('somedesc', f.getvalue())
        self.assertIn('tepilog', f.getvalue())
        self.assertNotIn('optional:', f.getvalue())


class HelpTestCase(BaseTestCase):

    def test_print_help(self):
        f = io.StringIO()
        self.conf([])
        self.conf.print_help(file=f)
        self.assertIn(
            'usage: test [-h] [--config-dir DIR] [--config-file PATH] '
            '[--version]',
            f.getvalue())
        self.assertIn('optional', f.getvalue())
        self.assertIn('-h, --help', f.getvalue())

    def test_print_strOpt_with_choices_help(self):
        f = io.StringIO()
        cli_opts = [
            cfg.StrOpt('aa', short='a', default='xx',
                       choices=['xx', 'yy', 'zz'],
                       help='StrOpt with choices.'),
            cfg.StrOpt('bb', short='b', default='yy',
                       choices=[None, 'yy', 'zz'],
                       help='StrOpt with choices.'),
            cfg.StrOpt('cc', short='c', default='zz',
                       choices=['', 'yy', 'zz'],
                       help='StrOpt with choices.'),
        ]
        self.conf.register_cli_opts(cli_opts)
        self.conf([])
        self.conf.print_help(file=f)
        self.assertIn(
            'usage: test [-h] [--aa AA] [--bb BB] [--cc CC] [--config-dir DIR]'
            '\n            [--config-file PATH] [--version]',
            f.getvalue())
        self.assertIn('optional', f.getvalue())
        self.assertIn('-h, --help', f.getvalue())
        self.assertIn('StrOpt with choices. Allowed values: xx, yy, zz',
                      f.getvalue())
        self.assertIn('StrOpt with choices. Allowed values: <None>, yy, zz',
                      f.getvalue())
        self.assertIn("StrOpt with choices. Allowed values: '', yy, zz",
                      f.getvalue())

    def test_print_sorted_help(self):
        f = io.StringIO()
        self.conf.register_cli_opt(cfg.StrOpt('abc'))
        self.conf.register_cli_opt(cfg.StrOpt('zba'))
        self.conf.register_cli_opt(cfg.StrOpt('ghi'))
        self.conf.register_cli_opt(cfg.StrOpt('deb'))
        self.conf([])
        self.conf.print_help(file=f)
        zba = f.getvalue().find('--zba')
        abc = f.getvalue().find('--abc')
        ghi = f.getvalue().find('--ghi')
        deb = f.getvalue().find('--deb')
        list = [abc, deb, ghi, zba]
        self.assertEqual(sorted(list), list)

    def test_print_sorted_help_with_positionals(self):
        f = io.StringIO()
        self.conf.register_cli_opt(
            cfg.StrOpt('pst', positional=True, required=False))
        self.conf.register_cli_opt(cfg.StrOpt('abc'))
        self.conf.register_cli_opt(cfg.StrOpt('zba'))
        self.conf.register_cli_opt(cfg.StrOpt('ghi'))
        self.conf([])
        self.conf.print_help(file=f)
        zba = f.getvalue().find('--zba')
        abc = f.getvalue().find('--abc')
        ghi = f.getvalue().find('--ghi')
        list = [abc, ghi, zba]
        self.assertEqual(sorted(list), list)

    def test_print_help_with_deprecated(self):
        f = io.StringIO()
        abc = cfg.StrOpt('a-bc',
                         deprecated_opts=[cfg.DeprecatedOpt('d-ef')])
        uvw = cfg.StrOpt('u-vw',
                         deprecated_name='x-yz')

        self.conf.register_cli_opt(abc)
        self.conf.register_cli_opt(uvw)
        self.conf([])
        self.conf.print_help(file=f)
        self.assertIn('--a-bc A_BC, --d-ef A_BC, --d_ef A_BC', f.getvalue())
        self.assertIn('--u-vw U_VW, --x-yz U_VW, --x_yz U_VW', f.getvalue())


class FindConfigFilesTestCase(BaseTestCase):

    def test_find_config_files(self):
        config_files = [os.path.expanduser('~/.blaa/blaa.conf'),
                        '/etc/foo.conf']

        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.useFixture(fixtures.MonkeyPatch('os.path.exists',
                        lambda p: p in config_files))

        self.assertEqual(cfg.find_config_files(project='blaa'), config_files)

    def test_find_config_files_snap(self):
        config_files = ['/snap/nova/current/etc/blaa/blaa.conf',
                        '/var/snap/nova/common/etc/blaa/blaa.conf']
        fake_env = {'SNAP': '/snap/nova/current/',
                    'SNAP_COMMON': '/var/snap/nova/common/'}

        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.useFixture(fixtures.MonkeyPatch('os.path.exists',
                        lambda p: p in config_files))
        self.useFixture(fixtures.MonkeyPatch('os.environ', fake_env))

        self.assertEqual(cfg.find_config_files(project='blaa'),
                         ['/var/snap/nova/common/etc/blaa/blaa.conf'])

    def test_find_config_files_with_extension(self):
        config_files = ['/etc/foo.json']

        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.useFixture(fixtures.MonkeyPatch('os.path.exists',
                        lambda p: p in config_files))

        self.assertEqual(cfg.find_config_files(project='blaa'), [])
        self.assertEqual(cfg.find_config_files(project='blaa',
                                               extension='.json'),
                         config_files)


class FindConfigDirsTestCase(BaseTestCase):

    def test_find_config_dirs(self):
        config_dirs = [os.path.expanduser('~/.blaa/blaa.conf.d'),
                       '/etc/foo.conf.d']

        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.useFixture(fixtures.MonkeyPatch('os.path.exists',
                                             lambda p: p in config_dirs))

        self.assertEqual(cfg.find_config_dirs(project='blaa'), config_dirs)

    def test_find_config_dirs_snap(self):
        config_dirs = ['/var/snap/nova/common/etc/blaa/blaa.conf.d']
        fake_env = {'SNAP': '/snap/nova/current/',
                    'SNAP_COMMON': '/var/snap/nova/common/'}

        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.useFixture(fixtures.MonkeyPatch('os.path.exists',
                                             lambda p: p in config_dirs))
        self.useFixture(fixtures.MonkeyPatch('os.environ', fake_env))

        self.assertEqual(cfg.find_config_dirs(project='blaa'), config_dirs)

    def test_find_config_dirs_non_exists(self):
        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.assertEqual(cfg.find_config_dirs(project='blaa'), [])

    def test_find_config_dirs_with_extension(self):
        config_dirs = ['/etc/foo.json.d']

        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo']))
        self.useFixture(fixtures.MonkeyPatch('os.path.exists',
                                             lambda p: p in config_dirs))

        self.assertEqual(cfg.find_config_dirs(project='blaa'), [])
        self.assertEqual(cfg.find_config_dirs(project='blaa',
                                              extension='.json.d'),
                         config_dirs)


class DefaultConfigFilesTestCase(BaseTestCase):

    def test_use_default(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        paths = self.create_tempfiles([('foo-', '[DEFAULT]\n''foo = bar\n')])

        self.conf.register_cli_opt(cfg.StrOpt('config-file-foo'))
        self.conf(args=['--config-file-foo', 'foo.conf'],
                  default_config_files=[paths[0]])

        self.assertEqual([paths[0]], self.conf.config_file)
        self.assertEqual('bar', self.conf.foo)

    def test_do_not_use_default_multi_arg(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        paths = self.create_tempfiles([('foo-', '[DEFAULT]\n''foo = bar\n')])

        self.conf(args=['--config-file', paths[0]],
                  default_config_files=['bar.conf'])

        self.assertEqual([paths[0]], self.conf.config_file)
        self.assertEqual('bar', self.conf.foo)

    def test_do_not_use_default_single_arg(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        paths = self.create_tempfiles([('foo-', '[DEFAULT]\n''foo = bar\n')])

        self.conf(args=['--config-file=' + paths[0]],
                  default_config_files=['bar.conf'])

        self.assertEqual([paths[0]], self.conf.config_file)
        self.assertEqual('bar', self.conf.foo)

    def test_no_default_config_file(self):
        self.conf(args=[])
        self.assertEqual([], self.conf.config_file)

    def test_find_default_config_file(self):
        paths = self.create_tempfiles([('def', '[DEFAULT]')])

        self.useFixture(fixtures.MonkeyPatch(
                        'oslo_config.cfg.find_config_files',
                        lambda project, prog: paths))

        self.conf(args=[], default_config_files=None)
        self.assertEqual(paths, self.conf.config_file)

    def test_default_config_file(self):
        paths = self.create_tempfiles([('def', '[DEFAULT]')])

        self.conf(args=[], default_config_files=paths)

        self.assertEqual(paths, self.conf.config_file)

    def test_default_config_file_with_value(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('def', '[DEFAULT]\n''foo = bar\n')])

        self.conf(args=[], default_config_files=paths)

        self.assertEqual(paths, self.conf.config_file)
        self.assertEqual('bar', self.conf.foo)

    def test_default_config_file_priority(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('def', '[DEFAULT]\n''foo = bar\n')])

        self.conf(args=['--foo=blaa'], default_config_files=paths)

        self.assertEqual(paths, self.conf.config_file)
        self.assertEqual('blaa', self.conf.foo)


class DefaultConfigDirsTestCase(BaseTestCase):

    def test_use_default(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        paths = self.create_tempfiles([('foo.conf.d/foo',
                                        '[DEFAULT]\n''foo = bar\n')])
        p = os.path.dirname(paths[0])
        self.conf.register_cli_opt(cfg.StrOpt('config-dir-foo'))
        self.conf(args=['--config-dir-foo', 'foo.conf.d'],
                  default_config_dirs=[p])

        self.assertEqual([p], self.conf.config_dir)
        self.assertEqual('bar', self.conf.foo)

    def test_do_not_use_default_multi_arg(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        paths = self.create_tempfiles([('foo.conf.d/foo',
                                        '[DEFAULT]\n''foo = bar\n')])
        p = os.path.dirname(paths[0])
        self.conf(args=['--config-dir', p],
                  default_config_dirs=['bar.conf.d'])

        self.assertEqual([p], self.conf.config_dirs)
        self.assertEqual('bar', self.conf.foo)

    def test_do_not_use_default_single_arg(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        paths = self.create_tempfiles([('foo.conf.d/foo',
                                        '[DEFAULT]\n''foo = bar\n')])
        p = os.path.dirname(paths[0])
        self.conf(args=['--config-dir=' + p],
                  default_config_dirs=['bar.conf.d'])

        self.assertEqual([p], self.conf.config_dir)
        self.assertEqual('bar', self.conf.foo)

    def test_no_default_config_dir(self):
        self.conf(args=[])
        self.assertEqual([], self.conf.config_dir)

    def test_find_default_config_dir(self):
        paths = self.create_tempfiles([('def.conf.d/def',
                                        '[DEFAULT]')])
        p = os.path.dirname(paths[0])
        self.useFixture(fixtures.MonkeyPatch(
                        'oslo_config.cfg.find_config_dirs',
                        lambda project, prog: p))

        self.conf(args=[], default_config_dirs=None)
        self.assertEqual([p], self.conf.config_dir)

    def test_default_config_dir(self):
        paths = self.create_tempfiles([('def.conf.d/def',
                                        '[DEFAULT]')])
        p = os.path.dirname(paths[0])
        self.conf(args=[], default_config_dirs=[p])

        self.assertEqual([p], self.conf.config_dir)

    def test_default_config_dir_with_value(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('def.conf.d/def',
                                        '[DEFAULT]\n''foo = bar\n')])
        p = os.path.dirname(paths[0])
        self.conf(args=[], default_config_dirs=[p])

        self.assertEqual([p], self.conf.config_dir)
        self.assertEqual('bar', self.conf.foo)

    def test_default_config_dir_priority(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('def.conf.d/def',
                                        '[DEFAULT]\n''foo = bar\n')])
        p = os.path.dirname(paths[0])
        self.conf(args=['--foo=blaa'], default_config_dirs=[p])

        self.assertEqual([p], self.conf.config_dir)
        self.assertEqual('blaa', self.conf.foo)


class CliOptsTestCase(BaseTestCase):
    """Test CLI Options.

    Each test scenario takes a name for the scenarios, as well as a dict:
    opt_class - class of the type of option that should be tested
    default - a default value for the option
    cli_args - a list containing a representation of an input command line
    value - the result value that is expected to be found
    deps - a tuple of deprecated name/group
    """

    IPv4Opt = functools.partial(cfg.IPOpt, version=4)
    IPv6Opt = functools.partial(cfg.IPOpt, version=6)

    multi_int = functools.partial(cfg.MultiOpt, item_type=types.Integer())
    multi_float = functools.partial(cfg.MultiOpt, item_type=types.Float())
    multi_string = functools.partial(cfg.MultiOpt, item_type=types.String())

    scenarios = [
        ('str_default',
         dict(opt_class=cfg.StrOpt, default=None, cli_args=[], value=None,
              deps=(None, None))),
        ('str_arg',
         dict(opt_class=cfg.StrOpt, default=None, cli_args=['--foo', 'bar'],
              value='bar', deps=(None, None))),
        ('str_arg_deprecated_name',
         dict(opt_class=cfg.StrOpt, default=None,
              cli_args=['--oldfoo', 'bar'], value='bar',
              deps=('oldfoo', None))),
        ('str_arg_deprecated_group',
         dict(opt_class=cfg.StrOpt, default=None,
              cli_args=['--old-foo', 'bar'], value='bar',
              deps=(None, 'old'))),
        ('str_arg_deprecated_group_default',
         dict(opt_class=cfg.StrOpt, default=None, cli_args=['--foo', 'bar'],
              value='bar', deps=(None, 'DEFAULT'))),
        ('str_arg_deprecated_group_and_name',
         dict(opt_class=cfg.StrOpt, default=None,
              cli_args=['--old-oof', 'bar'], value='bar',
              deps=('oof', 'old'))),
        ('bool_default',
         dict(opt_class=cfg.BoolOpt, default=False,
              cli_args=[], value=False, deps=(None, None))),
        ('bool_arg',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--foo'], value=True, deps=(None, None))),
        ('bool_arg_deprecated_name',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--oldfoo'], value=True,
              deps=('oldfoo', None))),
        ('bool_arg_deprecated_group',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--old-foo'], value=True,
              deps=(None, 'old'))),
        ('bool_arg_deprecated_group_default',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--foo'], value=True,
              deps=(None, 'DEFAULT'))),
        ('bool_arg_deprecated_group_and_name',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--old-oof'], value=True,
              deps=('oof', 'old'))),
        ('bool_arg_inverse',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--foo', '--nofoo'], value=False, deps=(None, None))),
        ('bool_arg_inverse_deprecated_name',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--oldfoo', '--nooldfoo'], value=False,
              deps=('oldfoo', None))),
        ('bool_arg_inverse_deprecated_group',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--old-foo', '--old-nofoo'], value=False,
              deps=(None, 'old'))),
        ('bool_arg_inverse_deprecated_group_default',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--foo', '--nofoo'], value=False,
              deps=(None, 'DEFAULT'))),
        ('bool_arg_inverse_deprecated_group_and_name',
         dict(opt_class=cfg.BoolOpt, default=None,
              cli_args=['--old-oof', '--old-nooof'], value=False,
              deps=('oof', 'old'))),
        ('int_default',
         dict(opt_class=cfg.IntOpt, default=10,
              cli_args=[], value=10, deps=(None, None))),
        ('int_arg',
         dict(opt_class=cfg.IntOpt, default=None,
              cli_args=['--foo=20'], value=20, deps=(None, None))),
        ('int_arg_deprecated_name',
         dict(opt_class=cfg.IntOpt, default=None,
              cli_args=['--oldfoo=20'], value=20, deps=('oldfoo', None))),
        ('int_arg_deprecated_group',
         dict(opt_class=cfg.IntOpt, default=None,
              cli_args=['--old-foo=20'], value=20, deps=(None, 'old'))),
        ('int_arg_deprecated_group_default',
         dict(opt_class=cfg.IntOpt, default=None,
              cli_args=['--foo=20'], value=20, deps=(None, 'DEFAULT'))),
        ('int_arg_deprecated_group_and_name',
         dict(opt_class=cfg.IntOpt, default=None,
              cli_args=['--old-oof=20'], value=20, deps=('oof', 'old'))),
        ('float_default',
         dict(opt_class=cfg.FloatOpt, default=1.0,
              cli_args=[], value=1.0, deps=(None, None))),
        ('float_arg',
         dict(opt_class=cfg.FloatOpt, default=None,
              cli_args=['--foo', '2.0'], value=2.0, deps=(None, None))),
        ('float_arg_deprecated_name',
         dict(opt_class=cfg.FloatOpt, default=None,
              cli_args=['--oldfoo', '2.0'], value=2.0, deps=('oldfoo', None))),
        ('float_arg_deprecated_group',
         dict(opt_class=cfg.FloatOpt, default=None,
              cli_args=['--old-foo', '2.0'], value=2.0, deps=(None, 'old'))),
        ('float_arg_deprecated_group_default',
         dict(opt_class=cfg.FloatOpt, default=None,
              cli_args=['--foo', '2.0'], value=2.0, deps=(None, 'DEFAULT'))),
        ('float_arg_deprecated_group_and_name',
         dict(opt_class=cfg.FloatOpt, default=None,
              cli_args=['--old-oof', '2.0'], value=2.0, deps=('oof', 'old'))),
        ('float_default_as_integer',
         dict(opt_class=cfg.FloatOpt, default=2,
              cli_args=['--old-oof', '2.0'], value=2.0, deps=('oof', 'old'))),
        ('ipv4addr_arg',
         dict(opt_class=IPv4Opt, default=None,
              cli_args=['--foo', '192.168.0.1'], value='192.168.0.1',
              deps=(None, None))),
        ('ipaddr_arg_implicitv4',
         dict(opt_class=cfg.IPOpt, default=None,
              cli_args=['--foo', '192.168.0.1'], value='192.168.0.1',
              deps=(None, None))),
        ('ipaddr_arg_implicitv6',
         dict(opt_class=cfg.IPOpt, default=None,
              cli_args=['--foo', 'abcd:ef::1'], value='abcd:ef::1',
              deps=(None, None))),
        ('ipv6addr_arg',
         dict(opt_class=IPv6Opt, default=None,
              cli_args=['--foo', 'abcd:ef::1'], value='abcd:ef::1',
              deps=(None, None))),
        ('list_default',
         dict(opt_class=cfg.ListOpt, default=['bar'],
              cli_args=[], value=['bar'], deps=(None, None))),
        ('list_arg',
         dict(opt_class=cfg.ListOpt, default=None,
              cli_args=['--foo', 'blaa,bar'], value=['blaa', 'bar'],
              deps=(None, None))),
        ('list_arg_with_spaces',
         dict(opt_class=cfg.ListOpt, default=None,
              cli_args=['--foo', 'blaa ,bar'], value=['blaa', 'bar'],
              deps=(None, None))),
        ('list_arg_deprecated_name',
         dict(opt_class=cfg.ListOpt, default=None,
              cli_args=['--oldfoo', 'blaa,bar'], value=['blaa', 'bar'],
              deps=('oldfoo', None))),
        ('list_arg_deprecated_group',
         dict(opt_class=cfg.ListOpt, default=None,
              cli_args=['--old-foo', 'blaa,bar'], value=['blaa', 'bar'],
              deps=(None, 'old'))),
        ('list_arg_deprecated_group_default',
         dict(opt_class=cfg.ListOpt, default=None,
              cli_args=['--foo', 'blaa,bar'], value=['blaa', 'bar'],
              deps=(None, 'DEFAULT'))),
        ('list_arg_deprecated_group_and_name',
         dict(opt_class=cfg.ListOpt, default=None,
              cli_args=['--old-oof', 'blaa,bar'], value=['blaa', 'bar'],
              deps=('oof', 'old'))),
        ('dict_default',
         dict(opt_class=cfg.DictOpt, default={'foo': 'bar'},
              cli_args=[], value={'foo': 'bar'}, deps=(None, None))),
        ('dict_arg',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--foo', 'key1:blaa,key2:bar'],
              value={'key1': 'blaa', 'key2': 'bar'}, deps=(None, None))),
        ('dict_arg_multiple_keys_last_wins',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--foo', 'key1:blaa', '--foo', 'key2:bar'],
              value={'key2': 'bar'}, deps=(None, None))),
        ('dict_arg_with_spaces',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--foo', 'key1:blaa   ,key2:bar'],
              value={'key1': 'blaa', 'key2': 'bar'}, deps=(None, None))),
        ('dict_arg_deprecated_name',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--oldfoo', 'key1:blaa', '--oldfoo', 'key2:bar'],
              value={'key2': 'bar'}, deps=('oldfoo', None))),
        ('dict_arg_deprecated_group',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--old-foo', 'key1:blaa,key2:bar'],
              value={'key1': 'blaa', 'key2': 'bar'}, deps=(None, 'old'))),
        ('dict_arg_deprecated_group2',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--old-foo', 'key1:blaa', '--old-foo', 'key2:bar'],
              value={'key2': 'bar'}, deps=(None, 'old'))),
        ('dict_arg_deprecated_group_default',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--foo', 'key1:blaa', '--foo', 'key2:bar'],
              value={'key2': 'bar'}, deps=(None, 'DEFAULT'))),
        ('dict_arg_deprecated_group_and_name',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--old-oof', 'key1:blaa,key2:bar'],
              value={'key1': 'blaa', 'key2': 'bar'}, deps=('oof', 'old'))),
        ('dict_arg_deprecated_group_and_name2',
         dict(opt_class=cfg.DictOpt, default=None,
              cli_args=['--old-oof', 'key1:blaa', '--old-oof', 'key2:bar'],
              value={'key2': 'bar'}, deps=('oof', 'old'))),
        ('port_default',
         dict(opt_class=cfg.PortOpt, default=80,
              cli_args=[], value=80, deps=(None, None))),
        ('port_arg',
         dict(opt_class=cfg.PortOpt, default=None,
              cli_args=['--foo=80'], value=80, deps=(None, None))),
        ('port_arg_deprecated_name',
         dict(opt_class=cfg.PortOpt, default=None,
              cli_args=['--oldfoo=80'], value=80, deps=('oldfoo', None))),
        ('port_arg_deprecated_group',
         dict(opt_class=cfg.PortOpt, default=None,
              cli_args=['--old-foo=80'], value=80, deps=(None, 'old'))),
        ('port_arg_deprecated_group_default',
         dict(opt_class=cfg.PortOpt, default=None,
              cli_args=['--foo=80'], value=80, deps=(None, 'DEFAULT'))),
        ('port_arg_deprecated_group_and_name',
         dict(opt_class=cfg.PortOpt, default=None,
              cli_args=['--old-oof=80'], value=80, deps=('oof', 'old'))),
        ('uri_default',
         dict(opt_class=cfg.URIOpt, default='http://example.com',
              cli_args=[], value='http://example.com', deps=(None, None))),
        ('uri_arg',
         dict(opt_class=cfg.URIOpt, default=None,
              cli_args=['--foo', 'http://example.com'],
              value='http://example.com', deps=(None, None))),
        ('multistr_default',
         dict(opt_class=cfg.MultiStrOpt, default=['bar'], cli_args=[],
              value=['bar'], deps=(None, None))),
        ('multistr_arg',
         dict(opt_class=cfg.MultiStrOpt, default=None,
              cli_args=['--foo', 'blaa', '--foo', 'bar'],
              value=['blaa', 'bar'], deps=(None, None))),
        ('multistr_arg_deprecated_name',
         dict(opt_class=cfg.MultiStrOpt, default=None,
              cli_args=['--oldfoo', 'blaa', '--oldfoo', 'bar'],
              value=['blaa', 'bar'], deps=('oldfoo', None))),
        ('multistr_arg_deprecated_group',
         dict(opt_class=cfg.MultiStrOpt, default=None,
              cli_args=['--old-foo', 'blaa', '--old-foo', 'bar'],
              value=['blaa', 'bar'], deps=(None, 'old'))),
        ('multistr_arg_deprecated_group_default',
         dict(opt_class=cfg.MultiStrOpt, default=None,
              cli_args=['--foo', 'blaa', '--foo', 'bar'],
              value=['blaa', 'bar'], deps=(None, 'DEFAULT'))),
        ('multistr_arg_deprecated_group_and_name',
         dict(opt_class=cfg.MultiStrOpt, default=None,
              cli_args=['--old-oof', 'blaa', '--old-oof', 'bar'],
              value=['blaa', 'bar'], deps=('oof', 'old'))),
        ('multiopt_arg_int',
         dict(opt_class=multi_int, default=None,
              cli_args=['--foo', '1', '--foo', '2'],
              value=[1, 2], deps=(None, None))),
        ('multiopt_float_int',
         dict(opt_class=multi_float, default=None,
              cli_args=['--foo', '1.2', '--foo', '2.3'],
              value=[1.2, 2.3], deps=(None, None))),
        ('multiopt_string',
         dict(opt_class=multi_string, default=None,
              cli_args=['--foo', 'bar', '--foo', 'baz'],
              value=["bar", "baz"], deps=(None, None))),
    ]

    def test_cli(self):

        self.conf.register_cli_opt(
            self.opt_class('foo', default=self.default,
                           deprecated_name=self.deps[0],
                           deprecated_group=self.deps[1]))

        self.conf(self.cli_args)

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(self.value, self.conf.foo)


class CliSpecialOptsTestCase(BaseTestCase):

    def test_help(self):
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn('usage: test', sys.stdout.getvalue())
        self.assertIn('[--version]', sys.stdout.getvalue())
        self.assertIn('[-h]', sys.stdout.getvalue())
        self.assertIn('--help', sys.stdout.getvalue())
        self.assertIn('[--config-dir DIR]', sys.stdout.getvalue())
        self.assertIn('[--config-file PATH]', sys.stdout.getvalue())

    def test_version(self):
        # In Python 3.4+, argparse prints the version on stdout; before 3.4, it
        # printed it on stderr.
        if sys.version_info >= (3, 4):
            stream_name = 'stdout'
        else:
            stream_name = 'stderr'
        self.useFixture(fixtures.MonkeyPatch("sys.%s" % stream_name,
                                             io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--version'])
        self.assertIn('1.0', getattr(sys, stream_name).getvalue())

    def test_config_file(self):
        paths = self.create_tempfiles([('1', '[DEFAULT]'),
                                       ('2', '[DEFAULT]')])

        self.conf(['--config-file', paths[0], '--config-file', paths[1]])

        self.assertEqual(paths, self.conf.config_file)


class PositionalTestCase(BaseTestCase):

    def _do_pos_test(self, opt_class, default, cli_args, value):
        self.conf.register_cli_opt(opt_class('foo',
                                             default=default,
                                             positional=True,
                                             required=False))

        self.conf(cli_args)

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(value, self.conf.foo)

    def test_positional_str_none_default(self):
        self._do_pos_test(cfg.StrOpt, None, [], None)

    def test_positional_str_default(self):
        self._do_pos_test(cfg.StrOpt, 'bar', [], 'bar')

    def test_positional_str_arg(self):
        self._do_pos_test(cfg.StrOpt, None, ['bar'], 'bar')

    def test_positional_int_none_default(self):
        self._do_pos_test(cfg.IntOpt, None, [], None)

    def test_positional_int_default(self):
        self._do_pos_test(cfg.IntOpt, 10, [], 10)

    def test_positional_int_arg(self):
        self._do_pos_test(cfg.IntOpt, None, ['20'], 20)

    def test_positional_float_none_default(self):
        self._do_pos_test(cfg.FloatOpt, None, [], None)

    def test_positional_float_default(self):
        self._do_pos_test(cfg.FloatOpt, 1.0, [], 1.0)

    def test_positional_float_arg(self):
        self._do_pos_test(cfg.FloatOpt, None, ['2.0'], 2.0)

    def test_positional_list_none_default(self):
        self._do_pos_test(cfg.ListOpt, None, [], None)

    def test_positional_list_empty_default(self):
        self._do_pos_test(cfg.ListOpt, [], [], [])

    def test_positional_list_default(self):
        self._do_pos_test(cfg.ListOpt, ['bar'], [], ['bar'])

    def test_positional_list_arg(self):
        self._do_pos_test(cfg.ListOpt, None,
                          ['blaa,bar'], ['blaa', 'bar'])

    def test_positional_dict_none_default(self):
        self._do_pos_test(cfg.DictOpt, None, [], None)

    def test_positional_dict_empty_default(self):
        self._do_pos_test(cfg.DictOpt, {}, [], {})

    def test_positional_dict_default(self):
        self._do_pos_test(cfg.DictOpt, {'key1': 'bar'}, [], {'key1': 'bar'})

    def test_positional_dict_arg(self):
        self._do_pos_test(cfg.DictOpt, None,
                          ['key1:blaa,key2:bar'],
                          {'key1': 'blaa', 'key2': 'bar'})

    def test_positional_ip_none_default(self):
        self._do_pos_test(cfg.IPOpt, None, [], None)

    def test_positional_ip_default(self):
        self._do_pos_test(cfg.IPOpt, '127.0.0.1', [], '127.0.0.1')

    def test_positional_ip_arg(self):
        self._do_pos_test(cfg.IPOpt, None, ['127.0.0.1'], '127.0.0.1')

    def test_positional_port_none_default(self):
        self._do_pos_test(cfg.PortOpt, None, [], None)

    def test_positional_port_default(self):
        self._do_pos_test(cfg.PortOpt, 80, [], 80)

    def test_positional_port_arg(self):
        self._do_pos_test(cfg.PortOpt, None, ['443'], 443)

    def test_positional_uri_default(self):
        self._do_pos_test(cfg.URIOpt, 'http://example.com', [],
                          'http://example.com')

    def test_positional_uri_none_default(self):
        self._do_pos_test(cfg.URIOpt, None, [], None)

    def test_positional_uri_arg(self):
        self._do_pos_test(cfg.URIOpt, None, ['http://example.com'],
                          'http://example.com')

    def test_positional_multistr_none_default(self):
        self._do_pos_test(cfg.MultiStrOpt, None, [], None)

    def test_positional_multistr_empty_default(self):
        self._do_pos_test(cfg.MultiStrOpt, [], [], [])

    def test_positional_multistr_default(self):
        self._do_pos_test(cfg.MultiStrOpt, ['bar'], [], ['bar'])

    def test_positional_multistr_arg(self):
        self._do_pos_test(cfg.MultiStrOpt, None,
                          ['blaa', 'bar'], ['blaa', 'bar'])

    def test_positional_bool(self):
        self.assertRaises(ValueError, cfg.BoolOpt, 'foo', positional=True)

    def test_required_positional_opt_defined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=True, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' foo\n', sys.stdout.getvalue())

        self.conf(['bar'])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_required_positional_opt_undefined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=True, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' foo\n', sys.stdout.getvalue())

        self.assertRaises(SystemExit, self.conf, [])

    def test_optional_positional_opt_defined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=False, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' [foo]\n', sys.stdout.getvalue())

        self.conf(['bar'])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_optional_positional_opt_undefined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=False, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' [foo]\n', sys.stdout.getvalue())

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertIsNone(self.conf.foo)

    def test_optional_positional_hyphenated_opt_defined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo-bar', required=False, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' [foo_bar]\n', sys.stdout.getvalue())

        self.conf(['baz'])
        self.assertTrue(hasattr(self.conf, 'foo_bar'))
        self.assertEqual('baz', self.conf.foo_bar)

    def test_optional_positional_hyphenated_opt_undefined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo-bar', required=False, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' [foo_bar]\n', sys.stdout.getvalue())

        self.conf([])
        self.assertTrue(hasattr(self.conf, 'foo_bar'))
        self.assertIsNone(self.conf.foo_bar)

    def test_required_positional_hyphenated_opt_defined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo-bar', required=True, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' foo_bar\n', sys.stdout.getvalue())

        self.conf(['baz'])
        self.assertTrue(hasattr(self.conf, 'foo_bar'))
        self.assertEqual('baz', self.conf.foo_bar)

    def test_required_positional_hyphenated_opt_undefined(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo-bar', required=True, positional=True))

        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn(' foo_bar\n', sys.stdout.getvalue())

        self.assertRaises(SystemExit, self.conf, [])

    def test_missing_required_cli_opt(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=True, positional=True))
        self.assertRaises(SystemExit, self.conf, [])

    def test_positional_opts_order(self):
        self.conf.register_cli_opts((
            cfg.StrOpt('command', positional=True),
            cfg.StrOpt('arg1', positional=True),
            cfg.StrOpt('arg2', positional=True))
        )

        self.conf(['command', 'arg1', 'arg2'])

        self.assertEqual('command', self.conf.command)
        self.assertEqual('arg1', self.conf.arg1)
        self.assertEqual('arg2', self.conf.arg2)

    def test_positional_opt_order(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('command', positional=True))
        self.conf.register_cli_opt(
            cfg.StrOpt('arg1', positional=True))
        self.conf.register_cli_opt(
            cfg.StrOpt('arg2', positional=True))

        self.conf(['command', 'arg1', 'arg2'])

        self.assertEqual('command', self.conf.command)
        self.assertEqual('arg1', self.conf.arg1)
        self.assertEqual('arg2', self.conf.arg2)

    def test_positional_opt_unregister(self):
        command = cfg.StrOpt('command', positional=True)
        arg1 = cfg.StrOpt('arg1', positional=True)
        arg2 = cfg.StrOpt('arg2', positional=True)
        self.conf.register_cli_opt(command)
        self.conf.register_cli_opt(arg1)
        self.conf.register_cli_opt(arg2)

        self.conf(['command', 'arg1', 'arg2'])

        self.assertEqual('command', self.conf.command)
        self.assertEqual('arg1', self.conf.arg1)
        self.assertEqual('arg2', self.conf.arg2)

        self.conf.reset()

        self.conf.unregister_opt(arg1)
        self.conf.unregister_opt(arg2)

        arg0 = cfg.StrOpt('arg0', positional=True)
        self.conf.register_cli_opt(arg0)
        self.conf.register_cli_opt(arg1)

        self.conf(['command', 'arg0', 'arg1'])

        self.assertEqual('command', self.conf.command)
        self.assertEqual('arg0', self.conf.arg0)
        self.assertEqual('arg1', self.conf.arg1)


# The real report_deprecated_feature has caching that causes races in our
# unit tests.  This replicates the relevant functionality.
def _fake_deprecated_feature(logger, msg, *args, **kwargs):
    stdmsg = 'Deprecated: %s' % msg
    logger.warning(stdmsg, *args, **kwargs)


@mock.patch('oslo_log.versionutils.report_deprecated_feature',
            _fake_deprecated_feature)
class ConfigFileOptsTestCase(BaseTestCase):

    def setUp(self):
        super(ConfigFileOptsTestCase, self).setUp()
        self.logger = self.useFixture(
            fixtures.FakeLogger(
                format='%(message)s',
                level=logging.WARNING,
                nuke_handlers=True,
            )
        )

    def _do_deprecated_test(self, opt_class, value, result, key,
                            section='DEFAULT',
                            dname=None, dgroup=None):
        self.conf.register_opt(opt_class('newfoo',
                                         deprecated_name=dname,
                                         deprecated_group=dgroup))

        paths = self.create_tempfiles([('test',
                                        '[' + section + ']\n' +
                                        key + ' = ' + value + '\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertEqual(result, self.conf.newfoo)

    def _do_dname_test_use(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'oldfoo',
                                 dname='oldfoo')

    def _do_dgroup_test_use(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'newfoo',
                                 section='old', dgroup='old')

    def _do_default_dgroup_test_use(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'newfoo',
                                 section='DEFAULT', dgroup='DEFAULT')

    def _do_dgroup_and_dname_test_use(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'oof',
                                 section='old', dgroup='old', dname='oof')

    def _do_dname_test_ignore(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'newfoo',
                                 dname='oldfoo')

    def _do_dgroup_test_ignore(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'newfoo',
                                 section='DEFAULT', dgroup='old')

    def _do_dgroup_and_dname_test_ignore(self, opt_class, value, result):
        self._do_deprecated_test(opt_class, value, result, 'oof',
                                 section='old', dgroup='old', dname='oof')

    def test_conf_file_str_default(self):
        self.conf.register_opt(cfg.StrOpt('foo', default='bar'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_conf_file_str_value(self):
        self.conf.register_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_conf_file_str_value_override(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = baar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = baaar\n')])

        self.conf(['--foo', 'bar',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('baaar', self.conf.foo)

    def test_conf_file_str_value_override_use_deprecated(self):
        """last option should always win, even if last uses deprecated."""
        self.conf.register_cli_opt(
            cfg.StrOpt('newfoo', deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('0',
                                        '[DEFAULT]\n'
                                        'newfoo = middle\n'),
                                       ('1',
                                        '[DEFAULT]\n'
                                        'oldfoo = last\n')])

        self.conf(['--newfoo', 'first',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertTrue(hasattr(self.conf, 'oldfoo'))
        self.assertEqual('last', self.conf.newfoo)
        log_out = self.logger.output
        self.assertIn('is deprecated', log_out)
        self.assertIn('Use option "newfoo"', log_out)

    def test_use_deprecated_for_removal_without_reason(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('oldfoo',
                       deprecated_for_removal=True))

        paths = self.create_tempfiles([('0',
                                        '[DEFAULT]\n'
                                        'oldfoo = middle\n')])

        self.conf(['--oldfoo', 'first',
                   '--config-file', paths[0]])

        log_out = self.logger.output
        self.assertIn('deprecated for removal.', log_out)

    def test_use_deprecated_for_removal_with_reason(self):
        self.conf.register_cli_opt(
            cfg.StrOpt('oldfoo',
                       deprecated_for_removal=True,
                       deprecated_reason='a very good reason'))

        paths = self.create_tempfiles([('0',
                                        '[DEFAULT]\n'
                                        'oldfoo = middle\n')])

        self.conf(['--oldfoo', 'first',
                   '--config-file', paths[0]])

        log_out = self.logger.output
        self.assertIn('deprecated for removal (a very good reason).', log_out)

    def test_conf_file_str_use_dname(self):
        self._do_dname_test_use(cfg.StrOpt, 'value1', 'value1')

    def test_conf_file_str_use_dgroup(self):
        self._do_dgroup_test_use(cfg.StrOpt, 'value1', 'value1')

    def test_conf_file_str_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.StrOpt, 'value1', 'value1')

    def test_conf_file_str_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.StrOpt, 'value1', 'value1')

    def test_conf_file_str_ignore_dname(self):
        self._do_dname_test_ignore(cfg.StrOpt, 'value2', 'value2')

    def test_conf_file_str_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.StrOpt, 'value2', 'value2')

    def test_conf_file_str_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.StrOpt, 'value2', 'value2')

    def test_conf_file_str_value_with_good_choice_value(self):
        self.conf.register_opt(cfg.StrOpt('foo', choices=['bar', 'baz']))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_conf_file_bool_default_none(self):
        self.conf.register_opt(cfg.BoolOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertIsNone(self.conf.foo)

    def test_conf_file_bool_default_false(self):
        self.conf.register_opt(cfg.BoolOpt('foo', default=False))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertFalse(self.conf.foo)

    def test_conf_file_bool_value(self):
        self.conf.register_opt(cfg.BoolOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = true\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertTrue(self.conf.foo)

    def test_conf_file_bool_cli_value_override(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 0\n')])

        self.conf(['--foo',
                   '--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertFalse(self.conf.foo)

    def test_conf_file_bool_cli_inverse_override(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = true\n')])

        self.conf(['--nofoo',
                   '--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertTrue(self.conf.foo)

    def test_conf_file_bool_cli_order_override(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = false\n')])

        self.conf(['--config-file', paths[0],
                   '--foo'])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertTrue(self.conf.foo)

    def test_conf_file_bool_file_value_override(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 0\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = yes\n')])

        self.conf(['--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertTrue(self.conf.foo)

    def test_conf_file_bool_use_dname(self):
        self._do_dname_test_use(cfg.BoolOpt, 'yes', True)

    def test_conf_file_bool_use_dgroup(self):
        self._do_dgroup_test_use(cfg.BoolOpt, 'yes', True)

    def test_conf_file_bool_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.BoolOpt, 'yes', True)

    def test_conf_file_bool_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.BoolOpt, 'yes', True)

    def test_conf_file_bool_ignore_dname(self):
        self._do_dname_test_ignore(cfg.BoolOpt, 'no', False)

    def test_conf_file_bool_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.BoolOpt, 'no', False)

    def test_conf_file_bool_ignore_group_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.BoolOpt, 'no', False)

    def test_conf_file_int_default(self):
        self.conf.register_opt(cfg.IntOpt('foo', default=666))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(666, self.conf.foo)

    def test_conf_file_int_string_default_type(self):
        self.conf.register_opt(cfg.IntOpt('foo', default='666'))
        self.conf([])
        self.assertEqual(666, self.conf.foo)

    def test_conf_file_int_value(self):
        self.conf.register_opt(cfg.IntOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 666\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(666, self.conf.foo)

    def test_conf_file_int_value_override(self):
        self.conf.register_cli_opt(cfg.IntOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 66\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = 666\n')])

        self.conf(['--foo', '6',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(666, self.conf.foo)

    def test_conf_file_int_min_max(self):
        self.conf.register_opt(cfg.IntOpt('foo', min=1, max=5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 10\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_int_min_greater_max(self):
        self.assertRaises(ValueError, cfg.IntOpt, 'foo', min=5, max=1)

    def test_conf_file_int_use_dname(self):
        self._do_dname_test_use(cfg.IntOpt, '66', 66)

    def test_conf_file_int_use_dgroup(self):
        self._do_dgroup_test_use(cfg.IntOpt, '66', 66)

    def test_conf_file_int_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.IntOpt, '66', 66)

    def test_conf_file_int_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.IntOpt, '66', 66)

    def test_conf_file_int_ignore_dname(self):
        self._do_dname_test_ignore(cfg.IntOpt, '64', 64)

    def test_conf_file_int_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.IntOpt, '64', 64)

    def test_conf_file_int_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.IntOpt, '64', 64)

    def test_conf_file_float_default(self):
        self.conf.register_opt(cfg.FloatOpt('foo', default=6.66))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(6.66, self.conf.foo)

    def test_conf_file_float_default_wrong_type(self):
        self.assertRaises(cfg.DefaultValueError, cfg.FloatOpt, 'foo',
                          default='foobar6.66')

    def test_conf_file_float_value(self):
        self.conf.register_opt(cfg.FloatOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 6.66\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(6.66, self.conf.foo)

    def test_conf_file_float_value_override(self):
        self.conf.register_cli_opt(cfg.FloatOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 6.6\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = 6.66\n')])

        self.conf(['--foo', '6',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(6.66, self.conf.foo)

    def test_conf_file_float_use_dname(self):
        self._do_dname_test_use(cfg.FloatOpt, '66.54', 66.54)

    def test_conf_file_float_use_dgroup(self):
        self._do_dgroup_test_use(cfg.FloatOpt, '66.54', 66.54)

    def test_conf_file_float_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.FloatOpt, '66.54', 66.54)

    def test_conf_file_float_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.FloatOpt, '66.54', 66.54)

    def test_conf_file_float_ignore_dname(self):
        self._do_dname_test_ignore(cfg.FloatOpt, '64.54', 64.54)

    def test_conf_file_float_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.FloatOpt, '64.54', 64.54)

    def test_conf_file_float_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.FloatOpt, '64.54', 64.54)

    def test_conf_file_float_min_max_above_max(self):
        self.conf.register_opt(cfg.FloatOpt('foo', min=1.1, max=5.5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 10.5\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_float_only_max_above_max(self):
        self.conf.register_opt(cfg.FloatOpt('foo', max=5.5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 10.5\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_float_min_max_below_min(self):
        self.conf.register_opt(cfg.FloatOpt('foo', min=1.1, max=5.5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 0.5\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_float_only_min_below_min(self):
        self.conf.register_opt(cfg.FloatOpt('foo', min=1.1))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 0.5\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_float_min_max_in_range(self):
        self.conf.register_opt(cfg.FloatOpt('foo', min=1.1, max=5.5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 4.5\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(4.5, self.conf.foo)

    def test_conf_file_float_only_max_in_range(self):
        self.conf.register_opt(cfg.FloatOpt('foo', max=5.5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 4.5\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(4.5, self.conf.foo)

    def test_conf_file_float_only_min_in_range(self):
        self.conf.register_opt(cfg.FloatOpt('foo', min=3.5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 4.5\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(4.5, self.conf.foo)

    def test_conf_file_float_min_greater_max(self):
        self.assertRaises(ValueError, cfg.FloatOpt, 'foo', min=5.5, max=1.5)

    def test_conf_file_list_default(self):
        self.conf.register_opt(cfg.ListOpt('foo', default=['bar']))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(['bar'], self.conf.foo)

    def test_conf_file_list_default_wrong_type(self):
        self.assertRaises(cfg.DefaultValueError, cfg.ListOpt, 'foo',
                          default=25)

    def test_conf_file_list_value(self):
        self.conf.register_opt(cfg.ListOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(['bar'], self.conf.foo)

    def test_conf_file_list_value_override(self):
        self.conf.register_cli_opt(cfg.ListOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = bar,bar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = b,a,r\n')])

        self.conf(['--foo', 'bar',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(['b', 'a', 'r'], self.conf.foo)

    def test_conf_file_list_item_type(self):
        self.conf.register_cli_opt(cfg.ListOpt('foo',
                                               item_type=types.Integer()))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = 1,2\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual([1, 2], self.conf.foo)

    def test_conf_file_list_item_wrong_type(self):
        self.assertRaises(cfg.DefaultValueError, cfg.ListOpt, 'foo',
                          default="bar", item_type=types.Integer())

    def test_conf_file_list_bounds(self):
        self.conf.register_cli_opt(cfg.ListOpt('foo',
                                               item_type=types.Integer(),
                                               default="[1,2]",
                                               bounds=True))
        self.conf([])
        self.assertEqual([1, 2], self.conf.foo)

    def test_conf_file_list_use_dname(self):
        self._do_dname_test_use(cfg.ListOpt, 'a,b,c', ['a', 'b', 'c'])

    def test_conf_file_list_use_dgroup(self):
        self._do_dgroup_test_use(cfg.ListOpt, 'a,b,c', ['a', 'b', 'c'])

    def test_conf_file_list_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.ListOpt, 'a,b,c', ['a', 'b', 'c'])

    def test_conf_file_list_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.ListOpt, 'a,b,c',
                                           ['a', 'b', 'c'])

    def test_conf_file_list_ignore_dname(self):
        self._do_dname_test_ignore(cfg.ListOpt, 'd,e,f', ['d', 'e', 'f'])

    def test_conf_file_list_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.ListOpt, 'd,e,f', ['d', 'e', 'f'])

    def test_conf_file_list_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(
            cfg.ListOpt, 'd,e,f', ['d', 'e', 'f'])

    def test_conf_file_list_spaces_use_dname(self):
        self._do_dname_test_use(cfg.ListOpt, 'a, b, c', ['a', 'b', 'c'])

    def test_conf_file_list_spaces_use_dgroup(self):
        self._do_dgroup_test_use(cfg.ListOpt, 'a, b, c', ['a', 'b', 'c'])

    def test_conf_file_list_spaces_use_default_dgroup(self):
        self._do_default_dgroup_test_use(
            cfg.ListOpt, 'a, b, c', ['a', 'b', 'c'])

    def test_conf_file_list_spaces_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(
            cfg.ListOpt, 'a, b, c', ['a', 'b', 'c'])

    def test_conf_file_list_spaces_ignore_dname(self):
        self._do_dname_test_ignore(cfg.ListOpt, 'd, e, f', ['d', 'e', 'f'])

    def test_conf_file_list_spaces_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.ListOpt, 'd, e, f', ['d', 'e', 'f'])

    def test_conf_file_list_spaces_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.ListOpt, 'd, e, f',
                                              ['d', 'e', 'f'])

    def test_conf_file_dict_default(self):
        self.conf.register_opt(cfg.DictOpt('foo', default={'key': 'bar'}))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual({'key': 'bar'}, self.conf.foo)

    def test_conf_file_dict_value(self):
        self.conf.register_opt(cfg.DictOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = key:bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual({'key': 'bar'}, self.conf.foo)

    def test_conf_file_dict_colon_in_value(self):
        self.conf.register_opt(cfg.DictOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = key:bar:baz\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual({'key': 'bar:baz'}, self.conf.foo)

    def test_conf_file_dict_value_no_colon(self):
        self.conf.register_opt(cfg.DictOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = key:bar,baz\n')])

        self.conf(['--config-file', paths[0]])

        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')
        self.assertRaises(ValueError, getattr, self.conf, 'foo')

    def test_conf_file_dict_value_duplicate_key(self):
        self.conf.register_opt(cfg.DictOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = key:bar,key:baz\n')])

        self.conf(['--config-file', paths[0]])

        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')
        self.assertRaises(ValueError, getattr, self.conf, 'foo')

    def test_conf_file_dict_values_override_deprecated(self):
        self.conf.register_cli_opt(cfg.DictOpt('foo',
                                   deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = key1:bar1\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'oldfoo = key2:bar2\n'
                                        'oldfoo = key3:bar3\n')])

        self.conf(['--foo', 'key0:bar0',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))

        self.assertEqual({'key3': 'bar3'}, self.conf.foo)

    def test_conf_file_dict_deprecated(self):
        self.conf.register_opt(cfg.DictOpt('newfoo', deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'oldfoo= key1:bar1\n'
                                        'oldfoo = key2:bar2\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertEqual({'key2': 'bar2'}, self.conf.newfoo)

    def test_conf_file_dict_value_override(self):
        self.conf.register_cli_opt(cfg.DictOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = key:bar,key2:bar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = k1:v1,k2:v2\n')])

        self.conf(['--foo', 'x:y,x2:y2',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual({'k1': 'v1', 'k2': 'v2'}, self.conf.foo)

    def test_conf_file_dict_use_dname(self):
        self._do_dname_test_use(cfg.DictOpt,
                                'k1:a,k2:b,k3:c',
                                {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_use_dgroup(self):
        self._do_dgroup_test_use(cfg.DictOpt,
                                 'k1:a,k2:b,k3:c',
                                 {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.DictOpt,
                                         'k1:a,k2:b,k3:c',
                                         {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.DictOpt,
                                           'k1:a,k2:b,k3:c',
                                           {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_ignore_dname(self):
        self._do_dname_test_ignore(cfg.DictOpt,
                                   'k1:d,k2:e,k3:f',
                                   {'k1': 'd', 'k2': 'e', 'k3': 'f'})

    def test_conf_file_dict_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.DictOpt,
                                    'k1:d,k2:e,k3:f',
                                    {'k1': 'd', 'k2': 'e', 'k3': 'f'})

    def test_conf_file_dict_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.DictOpt,
                                              'k1:d,k2:e,k3:f',
                                              {'k1': 'd',
                                               'k2': 'e',
                                               'k3': 'f'})

    def test_conf_file_dict_spaces_use_dname(self):
        self._do_dname_test_use(cfg.DictOpt,
                                'k1:a,k2:b,k3:c',
                                {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_spaces_use_dgroup(self):
        self._do_dgroup_test_use(cfg.DictOpt,
                                 'k1:a,k2:b,k3:c',
                                 {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_spaces_use_default_dgroup(self):
        self._do_default_dgroup_test_use(cfg.DictOpt,
                                         'k1:a,k2:b,k3:c',
                                         {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_spaces_use_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_use(cfg.DictOpt,
                                           'k1:a,k2:b,k3:c',
                                           {'k1': 'a', 'k2': 'b', 'k3': 'c'})

    def test_conf_file_dict_spaces_ignore_dname(self):
        self._do_dname_test_ignore(cfg.DictOpt,
                                   'k1:d,k2:e,k3:f',
                                   {'k1': 'd', 'k2': 'e', 'k3': 'f'})

    def test_conf_file_dict_spaces_ignore_dgroup(self):
        self._do_dgroup_test_ignore(cfg.DictOpt,
                                    'k1:d,k2:e,k3:f',
                                    {'k1': 'd', 'k2': 'e', 'k3': 'f'})

    def test_conf_file_dict_spaces_ignore_dgroup_and_dname(self):
        self._do_dgroup_and_dname_test_ignore(cfg.DictOpt,
                                              'k1:d,k2:e,k3:f',
                                              {'k1': 'd',
                                               'k2': 'e',
                                               'k3': 'f'})

    def test_conf_file_port_outside_range(self):
        self.conf.register_opt(cfg.PortOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 65536\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_port_list(self):
        self.conf.register_opt(cfg.ListOpt('foo', item_type=types.Port()))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 22, 80\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual([22, 80], self.conf.foo)

    def test_conf_file_port_list_default(self):
        self.conf.register_opt(cfg.ListOpt('foo', item_type=types.Port(),
                                           default=[55, 77]))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 22, 80\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual([22, 80], self.conf.foo)

    def test_conf_file_port_list_only_default(self):
        self.conf.register_opt(cfg.ListOpt('foo', item_type=types.Port(),
                                           default=[55, 77]))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual([55, 77], self.conf.foo)

    def test_conf_file_port_list_outside_range(self):
        self.conf.register_opt(cfg.ListOpt('foo', item_type=types.Port()))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 1,65536\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_port_min_max_above_max(self):
        self.conf.register_opt(cfg.PortOpt('foo', min=1, max=5))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 10\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_port_only_max_above_max(self):
        self.conf.register_opt(cfg.PortOpt('foo', max=500))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 600\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_port_min_max_below_min(self):
        self.conf.register_opt(cfg.PortOpt('foo', min=100, max=500))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 99\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_port_only_min_below_min(self):
        self.conf.register_opt(cfg.PortOpt('foo', min=1025))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 1024\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_port_min_max_in_range(self):
        self.conf.register_opt(cfg.PortOpt('foo', min=1025, max=6000))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 2500\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(2500, self.conf.foo)

    def test_conf_file_port_only_max_in_range(self):
        self.conf.register_opt(cfg.PortOpt('foo', max=5000))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 45\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(45, self.conf.foo)

    def test_conf_file_port_only_min_in_range(self):
        self.conf.register_opt(cfg.PortOpt('foo', min=35))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 45\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(45, self.conf.foo)

    def test_conf_file_port_min_greater_max(self):
        self.assertRaises(ValueError, cfg.PortOpt, 'foo', min=55, max=15)

    def test_conf_file_multistr_default(self):
        self.conf.register_opt(cfg.MultiStrOpt('foo', default=['bar']))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(['bar'], self.conf.foo)

    def test_conf_file_multistr_value(self):
        self.conf.register_opt(cfg.MultiStrOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(['bar'], self.conf.foo)

    def test_conf_file_multistr_values_append_deprecated(self):
        self.conf.register_cli_opt(cfg.MultiStrOpt('foo',
                                   deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = bar1\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'oldfoo = bar2\n'
                                        'oldfoo = bar3\n')])

        self.conf(['--foo', 'bar0',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))

        self.assertEqual(['bar0', 'bar1', 'bar2', 'bar3'], self.conf.foo)

    def test_conf_file_multistr_values_append(self):
        self.conf.register_cli_opt(cfg.MultiStrOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = bar1\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = bar2\n'
                                        'foo = bar3\n')])

        self.conf(['--foo', 'bar0',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))

        self.assertEqual(['bar0', 'bar1', 'bar2', 'bar3'], self.conf.foo)

    def test_conf_file_multistr_deprecated(self):
        self.conf.register_opt(
            cfg.MultiStrOpt('newfoo', deprecated_name='oldfoo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'oldfoo= bar1\n'
                                        'oldfoo = bar2\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'newfoo'))
        self.assertEqual(['bar1', 'bar2'], self.conf.newfoo)

    def test_conf_file_multiple_opts(self):
        self.conf.register_opts([cfg.StrOpt('foo'), cfg.StrOpt('bar')])

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        'bar = foo\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)
        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual('foo', self.conf.bar)

    def test_conf_file_raw_value(self):
        self.conf.register_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar-%08x\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar-%08x', self.conf.foo)

    def test_conf_file_sorted_group(self):
        # Create enough groups for the sorted problem to appear
        for i in range(10):
            group = cfg.OptGroup('group%s' % i, 'options')
            self.conf.register_group(group)
            self.conf.register_cli_opt(cfg.StrOpt('opt1'), group=group)

        paths = self.create_tempfiles(
            [('test', '[group1]\nopt1 = foo\n[group2]\nopt2 = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertEqual('foo', self.conf.group1.opt1)


class ConfigFileReloadTestCase(BaseTestCase):

    def test_conf_files_reload(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = baar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = baaar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('baar', self.conf.foo)

        shutil.copy(paths[1], paths[0])

        self.conf.reload_config_files()
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('baaar', self.conf.foo)

    def test_conf_files_reload_default(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo1'))
        self.conf.register_cli_opt(cfg.StrOpt('foo2'))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo1 = default1\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo2 = default2\n')])

        paths_change = self.create_tempfiles([('1',
                                               '[DEFAULT]\n'
                                               'foo1 = change_default1\n'),
                                              ('2',
                                               '[DEFAULT]\n'
                                               'foo2 = change_default2\n')])

        self.conf(args=[], default_config_files=paths)
        self.assertTrue(hasattr(self.conf, 'foo1'))
        self.assertEqual('default1', self.conf.foo1)
        self.assertTrue(hasattr(self.conf, 'foo2'))
        self.assertEqual('default2', self.conf.foo2)

        shutil.copy(paths_change[0], paths[0])
        shutil.copy(paths_change[1], paths[1])

        self.conf.reload_config_files()
        self.assertTrue(hasattr(self.conf, 'foo1'))
        self.assertEqual('change_default1', self.conf.foo1)
        self.assertTrue(hasattr(self.conf, 'foo2'))
        self.assertEqual('change_default2', self.conf.foo2)

    def test_conf_files_reload_file_not_found(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', required=True))
        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = baar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('baar', self.conf.foo)

        os.remove(paths[0])

        self.conf.reload_config_files()
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('baar', self.conf.foo)

    def test_conf_files_reload_error(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', required=True))
        self.conf.register_cli_opt(cfg.StrOpt('foo1', required=True))
        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = test1\n'
                                        'foo1 = test11\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo2 = test2\n'
                                        'foo3 = test22\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('test1', self.conf.foo)
        self.assertTrue(hasattr(self.conf, 'foo1'))
        self.assertEqual('test11', self.conf.foo1)

        shutil.copy(paths[1], paths[0])

        self.conf.reload_config_files()
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('test1', self.conf.foo)
        self.assertTrue(hasattr(self.conf, 'foo1'))
        self.assertEqual('test11', self.conf.foo1)


class ConfigFileMutateTestCase(BaseTestCase):
    def setUp(self):
        super(ConfigFileMutateTestCase, self).setUp()
        self.my_group = cfg.OptGroup('group', 'group options')
        self.conf.register_group(self.my_group)

    def _test_conf_files_mutate(self):
        paths = self.create_tempfiles([
            ('1', '[DEFAULT]\n'
                  'foo = old_foo\n'
                  '[group]\n'
                  'boo = old_boo\n'),
            ('2', '[DEFAULT]\n'
                  'foo = new_foo\n'
                  '[group]\n'
                  'boo = new_boo\n')])

        self.conf(['--config-file', paths[0]])
        shutil.copy(paths[1], paths[0])
        return self.conf.mutate_config_files()

    def test_conf_files_mutate_none(self):
        """Test that immutable opts are not reloaded"""

        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self._test_conf_files_mutate()
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('old_foo', self.conf.foo)

    def test_conf_files_mutate_foo(self):
        """Test that a mutable opt can be reloaded."""

        self.conf.register_cli_opt(cfg.StrOpt('foo', mutable=True))
        self._test_conf_files_mutate()
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('new_foo', self.conf.foo)

    def test_conf_files_mutate_group(self):
        """Test that mutable opts in groups can be reloaded."""
        self.conf.register_cli_opt(cfg.StrOpt('boo', mutable=True),
                                   group=self.my_group)
        self._test_conf_files_mutate()
        self.assertTrue(hasattr(self.conf, 'group'))
        self.assertTrue(hasattr(self.conf.group, 'boo'))
        self.assertEqual('new_boo', self.conf.group.boo)

    def test_warn_immutability(self):
        self.log_fixture = self.useFixture(fixtures.FakeLogger())
        self.conf.register_cli_opt(cfg.StrOpt('foo', mutable=True))
        self.conf.register_cli_opt(cfg.StrOpt('boo'), group=self.my_group)
        self._test_conf_files_mutate()
        self.assertEqual(
            "Ignoring change to immutable option group.boo\n"
            "Option DEFAULT.foo changed from [old_foo] to [new_foo]\n",
            self.log_fixture.output)

    def test_diff(self):
        self.log_fixture = self.useFixture(fixtures.FakeLogger())
        self.conf.register_cli_opt(cfg.StrOpt('imm'))
        self.conf.register_cli_opt(cfg.StrOpt('blank', mutable=True))
        self.conf.register_cli_opt(cfg.StrOpt('foo', mutable=True))
        self.conf.register_cli_opt(cfg.StrOpt('boo', mutable=True),
                                   group=self.my_group)
        diff = self._test_conf_files_mutate()
        self.assertEqual(
            {(None, 'foo'): ('old_foo', 'new_foo'),
             ('group', 'boo'): ('old_boo', 'new_boo')},
            diff)
        expected = ("Option DEFAULT.foo changed from [old_foo] to [new_foo]\n"
                    "Option group.boo changed from [old_boo] to [new_boo]\n")
        self.assertEqual(expected, self.log_fixture.output)

    def test_hooks_invoked_once(self):
        fresh = {}
        result = [0]

        def foo(conf, foo_fresh):
            self.assertEqual(conf, self.conf)
            self.assertEqual(fresh, foo_fresh)
            result[0] += 1

        self.conf.register_mutate_hook(foo)
        self.conf.register_mutate_hook(foo)
        self._test_conf_files_mutate()
        self.assertEqual(1, result[0])

    def test_hooks_see_new_values(self):
        def foo(conf, fresh):
            # Verify that we see the new value inside the mutate hook.
            self.assertEqual('new_foo', conf.foo)

        self.conf.register_cli_opt(cfg.StrOpt('foo', mutable=True))
        self.conf.register_mutate_hook(foo)

        paths = self.create_tempfiles([
            ('1', '[DEFAULT]\n'
                  'foo = old_foo\n'
                  '[group]\n'
                  'boo = old_boo\n'),
            ('2', '[DEFAULT]\n'
                  'foo = new_foo\n'
                  '[group]\n'
                  'boo = new_boo\n')])

        self.conf(['--config-file', paths[0]])
        # We access the value once before mutating it to ensure the
        # cache is populated.
        self.assertEqual('old_foo', self.conf.foo)

        shutil.copy(paths[1], paths[0])
        self.conf.mutate_config_files()
        # Verify that we see the new value after mutation is complete.
        self.assertEqual('new_foo', self.conf.foo)

    def test_clear(self):
        """Show that #clear doesn't undeclare opts.

        This justifies not clearing mutate_hooks either. ResetAndClearTestCase
        shows that values are cleared.
        """
        self.conf.register_cli_opt(cfg.StrOpt('cli'))
        self.conf.register_opt(cfg.StrOpt('foo'))
        dests = [info['opt'].dest for info, _ in self.conf._all_opt_infos()]
        self.assertIn('cli', dests)
        self.assertIn('foo', dests)

        self.conf.clear()
        dests = [info['opt'].dest for info, _ in self.conf._all_opt_infos()]
        self.assertIn('cli', dests)
        self.assertIn('foo', dests)


class OptGroupsTestCase(BaseTestCase):

    def test_arg_group(self):
        blaa_group = cfg.OptGroup('blaa', 'blaa options')
        self.conf.register_group(blaa_group)
        self.conf.register_cli_opt(cfg.StrOpt('foo'), group=blaa_group)

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)
        self.assertEqual('blaa', str(blaa_group))

    def test_autocreate_group_by_name(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_autocreate_group_by_group(self):
        group = cfg.OptGroup(name='blaa', title='Blaa options')
        self.conf.register_cli_opt(cfg.StrOpt('foo'), group=group)

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_autocreate_title(self):
        blaa_group = cfg.OptGroup('blaa')
        self.assertEqual(blaa_group.title, 'blaa options')

    def test_arg_group_by_name(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(cfg.StrOpt('foo'), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_with_default(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', default='bar'), group='blaa')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_with_conf_and_group_opts(self):
        self.conf.register_cli_opt(cfg.StrOpt('conf'), group='blaa')
        self.conf.register_cli_opt(cfg.StrOpt('group'), group='blaa')

        self.conf(['--blaa-conf', 'foo', '--blaa-group', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'conf'))
        self.assertEqual('foo', self.conf.blaa.conf)
        self.assertTrue(hasattr(self.conf.blaa, 'group'))
        self.assertEqual('bar', self.conf.blaa.group)

    def test_arg_group_in_config_file(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_with_deprecated_name(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_name='oldfoo'),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_with_deprecated_group(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_group='DEFAULT'),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_with_deprecated_group_and_name(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(
            cfg.StrOpt('foo', deprecated_group='DEFAULT',
                       deprecated_name='oldfoo'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_override_deprecated_name(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_name='oldfoo'),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = bar\n'
                                        'oldfoo = blabla\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_override_deprecated_group(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_group='DEFAULT'),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = blabla\n'
                                        '[blaa]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_override_deprecated_group_and_name(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(
            cfg.StrOpt('foo', deprecated_group='DEFAULT',
                       deprecated_name='oldfoo'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'oldfoo = blabla\n'
                                        '[blaa]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_with_capital_name(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[BLAA]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertFalse(hasattr(self.conf, 'BLAA'))
        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_arg_group_in_config_file_with_capital_name_on_legacy_code(self):
        self.conf.register_group(cfg.OptGroup('BLAA'))
        self.conf.register_opt(cfg.StrOpt('foo'), group='BLAA')

        paths = self.create_tempfiles([('test',
                                        '[BLAA]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertFalse(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf, 'BLAA'))
        self.assertTrue(hasattr(self.conf.BLAA, 'foo'))
        self.assertEqual('bar', self.conf.BLAA.foo)


class MappingInterfaceTestCase(BaseTestCase):

    def test_mapping_interface(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))

        self.conf(['--foo', 'bar'])

        self.assertIn('foo', self.conf)
        self.assertIn('config_file', self.conf)
        self.assertEqual(len(self.conf), 4)
        self.assertEqual('bar', self.conf['foo'])
        self.assertEqual('bar', self.conf.get('foo'))
        self.assertIn('bar', list(self.conf.values()))

    def test_mapping_interface_with_group(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(cfg.StrOpt('foo'), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertIn('blaa', self.conf)
        self.assertIn('foo', list(self.conf['blaa']))
        self.assertEqual(len(self.conf['blaa']), 1)
        self.assertEqual('bar', self.conf['blaa']['foo'])
        self.assertEqual('bar', self.conf['blaa'].get('foo'))
        self.assertIn('bar', self.conf['blaa'].values())
        self.assertEqual(self.conf['blaa'], self.conf.blaa)


class OptNameSeparatorTestCase(BaseTestCase):

    # NOTE(bnemec): The broken* values in these scenarios are opt dests or
    # config file names that are not actually valid, but can be added via a
    # DeprecatedOpt.  The tests only verify that those values do not end up
    # in the final config object.
    scenarios = [
        ('hyphen',
         dict(opt_name='foo-bar',
              opt_dest='foo_bar',
              broken_opt_dest='foo-bar',
              cf_name='foo_bar',
              broken_cf_name='foo-bar',
              cli_name='foo-bar',
              hyphen=True)),
        ('underscore',
         dict(opt_name='foo_bar',
              opt_dest='foo_bar',
              broken_opt_dest='foo-bar',
              cf_name='foo_bar',
              broken_cf_name='foo-bar',
              cli_name='foo_bar',
              hyphen=False)),
    ]

    def test_attribute_and_key_name(self):
        self.conf.register_opt(cfg.StrOpt(self.opt_name))

        self.assertTrue(hasattr(self.conf, self.opt_dest))
        self.assertFalse(hasattr(self.conf, self.broken_opt_dest))
        self.assertIn(self.opt_dest, self.conf)
        self.assertNotIn(self.broken_opt_dest, self.conf)

    def test_cli_opt_name(self):
        self.conf.register_cli_opt(cfg.BoolOpt(self.opt_name))

        self.conf(['--' + self.cli_name])

        self.assertTrue(getattr(self.conf, self.opt_dest))

    def test_config_file_opt_name(self):
        self.conf.register_opt(cfg.BoolOpt(self.opt_name))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n' +
                                        self.cf_name + ' = True\n' +
                                        self.broken_cf_name + ' = False\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(getattr(self.conf, self.opt_dest))

    def test_deprecated_name(self):
        self.conf.register_opt(cfg.StrOpt('foobar',
                                          deprecated_name=self.opt_name))

        self.assertTrue(hasattr(self.conf, 'foobar'))
        # TODO(mtreinish): Add a check on the log message
        self.assertTrue(hasattr(self.conf, self.opt_dest))
        self.assertFalse(hasattr(self.conf, self.broken_opt_dest))
        self.assertIn('foobar', self.conf)
        self.assertNotIn(self.opt_dest, self.conf)
        self.assertNotIn(self.broken_opt_dest, self.conf)

    def test_deprecated_name_alternate_group(self):
        self.conf.register_opt(
            cfg.StrOpt('foobar',
                       deprecated_name=self.opt_name,
                       deprecated_group='testing'),
            group=cfg.OptGroup('testing'),
        )

        self.assertTrue(hasattr(self.conf.testing, 'foobar'))
        # TODO(mtreinish): Add a check on the log message
        self.assertTrue(hasattr(self.conf.testing, self.opt_dest))
        self.assertFalse(hasattr(self.conf.testing, self.broken_opt_dest))
        self.assertIn('foobar', self.conf.testing)
        self.assertNotIn(self.opt_dest, self.conf.testing)
        self.assertNotIn(self.broken_opt_dest, self.conf.testing)

    def test_deprecated_name_cli(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foobar',
                                               deprecated_name=self.opt_name))

        self.conf(['--' + self.cli_name])

        self.assertTrue(self.conf.foobar)

    def test_deprecated_name_config_file(self):
        self.conf.register_opt(cfg.BoolOpt('foobar',
                                           deprecated_name=self.opt_name))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n' +
                                        self.cf_name + ' = True\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(self.conf.foobar)

    def test_deprecated_opts(self):
        oldopts = [cfg.DeprecatedOpt(self.opt_name)]
        self.conf.register_opt(cfg.StrOpt('foobar',
                                          deprecated_opts=oldopts))

        self.assertTrue(hasattr(self.conf, 'foobar'))
        # TODO(mtreinish): Add check for the log message
        self.assertTrue(hasattr(self.conf, self.opt_dest))
        self.assertFalse(hasattr(self.conf, self.broken_opt_dest))
        self.assertIn('foobar', self.conf)
        self.assertNotIn(self.opt_dest, self.conf)
        self.assertNotIn(self.broken_opt_dest, self.conf)

    def test_deprecated_opts_cli(self):
        oldopts = [cfg.DeprecatedOpt(self.opt_name)]
        self.conf.register_cli_opt(cfg.BoolOpt('foobar',
                                               deprecated_opts=oldopts))

        self.conf(['--' + self.cli_name])

        self.assertTrue(self.conf.foobar)

    def test_deprecated_opts_config_file(self):
        oldopts = [cfg.DeprecatedOpt(self.opt_name)]
        self.conf.register_opt(cfg.BoolOpt('foobar',
                                           deprecated_opts=oldopts))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n' +
                                        self.cf_name + ' = True\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(self.conf.foobar)


class ReRegisterOptTestCase(BaseTestCase):

    def test_conf_file_re_register_opt(self):
        opt = cfg.StrOpt('foo')
        self.assertTrue(self.conf.register_opt(opt))
        self.assertFalse(self.conf.register_opt(opt))

    def test_conf_file_re_register_opt_in_group(self):
        group = cfg.OptGroup('blaa')
        self.conf.register_group(group)
        self.conf.register_group(group)  # not an error
        opt = cfg.StrOpt('foo')
        self.assertTrue(self.conf.register_opt(opt, group=group))
        self.assertFalse(self.conf.register_opt(opt, group='blaa'))


class RegisterOptNameTestCase(BaseTestCase):

    def test_register_opt_with_disallow_name(self):
        for name in cfg.ConfigOpts.disallow_names:
            opt = cfg.StrOpt(name)
            self.assertRaises(ValueError, self.conf.register_opt, opt)


class TemplateSubstitutionTestCase(BaseTestCase):

    def _prep_test_str_sub(self, foo_default=None, bar_default=None):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default=foo_default))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default=bar_default))

    def _assert_str_sub(self):
        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual('blaa', self.conf.bar)

    def test_str_sub_default_from_default(self):
        self._prep_test_str_sub(foo_default='blaa', bar_default='$foo')

        self.conf([])

        self._assert_str_sub()

    def test_str_sub_default_from_default_recurse(self):
        self.conf.register_cli_opt(cfg.StrOpt('blaa', default='blaa'))
        self._prep_test_str_sub(foo_default='$blaa', bar_default='$foo')

        self.conf([])

        self._assert_str_sub()

    def test_str_sub_default_from_arg(self):
        self._prep_test_str_sub(bar_default='$foo')

        self.conf(['--foo', 'blaa'])

        self._assert_str_sub()

    def test_str_sub_default_from_config_file(self):
        self._prep_test_str_sub(bar_default='$foo')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = blaa\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_str_sub()

    def test_str_sub_arg_from_default(self):
        self._prep_test_str_sub(foo_default='blaa')

        self.conf(['--bar', '$foo'])

        self._assert_str_sub()

    def test_str_sub_arg_from_arg(self):
        self._prep_test_str_sub()

        self.conf(['--foo', 'blaa', '--bar', '$foo'])

        self._assert_str_sub()

    def test_str_sub_arg_from_config_file(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = blaa\n')])

        self.conf(['--config-file', paths[0], '--bar=$foo'])

        self._assert_str_sub()

    def test_str_sub_config_file_from_default(self):
        self._prep_test_str_sub(foo_default='blaa')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_str_sub()

    def test_str_sub_config_file_from_arg(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n')])

        self.conf(['--config-file', paths[0], '--foo=blaa'])

        self._assert_str_sub()

    def test_str_sub_config_file_from_config_file(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n'
                                        'foo = blaa\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_str_sub()

    def test_str_sub_with_dollar_escape_char(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar=foo-somethin$$k2\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual('foo-somethin$k2', self.conf.bar)

    def test_str_sub_with_backslash_escape_char(self):
        self._prep_test_str_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar=foo-somethin\\$k2\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual('foo-somethin$k2', self.conf.bar)

    def test_str_sub_group_from_default(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default='blaa'))
        self.conf.register_group(cfg.OptGroup('ba'))
        self.conf.register_cli_opt(cfg.StrOpt('r', default='$foo'), group='ba')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'ba'))
        self.assertTrue(hasattr(self.conf.ba, 'r'))
        self.assertEqual('blaa', self.conf.ba.r)

    def test_str_sub_set_default(self):
        self._prep_test_str_sub()
        self.conf.set_default('bar', '$foo')
        self.conf.set_default('foo', 'blaa')

        self.conf([])

        self._assert_str_sub()

    def test_str_sub_set_override(self):
        self._prep_test_str_sub()
        self.conf.set_override('bar', '$foo')
        self.conf.set_override('foo', 'blaa')

        self.conf([])

        self._assert_str_sub()

    def _prep_test_str_int_sub(self, foo_default=None, bar_default=None):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default=foo_default))
        self.conf.register_cli_opt(cfg.IntOpt('bar', default=bar_default))

    def _assert_int_sub(self):
        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual(123, self.conf.bar)

    def test_sub_default_from_default(self):
        self._prep_test_str_int_sub(foo_default='123', bar_default='$foo')

        self.conf([])

        self._assert_int_sub()

    def test_sub_default_from_default_recurse(self):
        self.conf.register_cli_opt(cfg.StrOpt('blaa', default='123'))
        self._prep_test_str_int_sub(foo_default='$blaa', bar_default='$foo')

        self.conf([])

        self._assert_int_sub()

    def test_sub_default_from_arg(self):
        self._prep_test_str_int_sub(bar_default='$foo')

        self.conf(['--foo', '123'])

        self._assert_int_sub()

    def test_sub_default_from_config_file(self):
        self._prep_test_str_int_sub(bar_default='$foo')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 123\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_int_sub()

    def test_sub_arg_from_default(self):
        self._prep_test_str_int_sub(foo_default='123')

        self.conf(['--bar', '$foo'])

        self._assert_int_sub()

    def test_sub_arg_from_arg(self):
        self._prep_test_str_int_sub()

        self.conf(['--foo', '123', '--bar', '$foo'])

        self._assert_int_sub()

    def test_sub_arg_from_config_file(self):
        self._prep_test_str_int_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = 123\n')])

        self.conf(['--config-file', paths[0], '--bar=$foo'])

        self._assert_int_sub()

    def test_sub_config_file_from_default(self):
        self._prep_test_str_int_sub(foo_default='123')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_int_sub()

    def test_sub_config_file_from_arg(self):
        self._prep_test_str_int_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n')])

        self.conf(['--config-file', paths[0], '--foo=123'])

        self._assert_int_sub()

    def test_sub_config_file_from_config_file(self):
        self._prep_test_str_int_sub()

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'bar = $foo\n'
                                        'foo = 123\n')])

        self.conf(['--config-file', paths[0]])

        self._assert_int_sub()

    def test_sub_group_from_default(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default='123'))
        self.conf.register_group(cfg.OptGroup('ba'))
        self.conf.register_cli_opt(cfg.IntOpt('r', default='$foo'), group='ba')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'ba'))
        self.assertTrue(hasattr(self.conf.ba, 'r'))
        self.assertEqual('123', self.conf.foo)
        self.assertEqual(123, self.conf.ba.r)

    def test_sub_group_from_default_deprecated(self):
        self.conf.register_group(cfg.OptGroup('ba'))
        self.conf.register_cli_opt(cfg.StrOpt(
            'foo', default='123', deprecated_group='DEFAULT'), group='ba')
        self.conf.register_cli_opt(cfg.IntOpt('r', default='$foo'), group='ba')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'ba'))
        self.assertTrue(hasattr(self.conf.ba, 'foo'))
        self.assertEqual('123', self.conf.ba.foo)
        self.assertTrue(hasattr(self.conf.ba, 'r'))
        self.assertEqual(123, self.conf.ba.r)

    def test_sub_group_from_args_deprecated(self):
        self.conf.register_group(cfg.OptGroup('ba'))
        self.conf.register_cli_opt(cfg.StrOpt(
            'foo', default='123', deprecated_group='DEFAULT'), group='ba')
        self.conf.register_cli_opt(cfg.IntOpt('r', default='$foo'), group='ba')

        self.conf(['--ba-foo=4242'])

        self.assertTrue(hasattr(self.conf, 'ba'))
        self.assertTrue(hasattr(self.conf.ba, 'foo'))
        self.assertTrue(hasattr(self.conf.ba, 'r'))
        self.assertEqual('4242', self.conf.ba.foo)
        self.assertEqual(4242, self.conf.ba.r)

    def test_sub_group_from_configfile_deprecated(self):
        self.conf.register_group(cfg.OptGroup('ba'))
        self.conf.register_cli_opt(cfg.StrOpt(
            'foo', default='123', deprecated_group='DEFAULT'), group='ba')
        self.conf.register_cli_opt(cfg.IntOpt('r', default='$foo'), group='ba')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo=4242\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'ba'))
        self.assertTrue(hasattr(self.conf.ba, 'foo'))
        self.assertTrue(hasattr(self.conf.ba, 'r'))
        self.assertEqual('4242', self.conf.ba.foo)
        self.assertEqual(4242, self.conf.ba.r)

    def test_dict_sub_default_from_default(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default='floo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='blaa'))
        self.conf.register_cli_opt(cfg.DictOpt('dt', default={'$foo': '$bar'}))

        self.conf([])

        self.assertEqual('blaa', self.conf.dt['floo'])

    def test_dict_sub_default_from_default_multi(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default='floo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='blaa'))
        self.conf.register_cli_opt(cfg.StrOpt('goo', default='gloo'))
        self.conf.register_cli_opt(cfg.StrOpt('har', default='hlaa'))
        self.conf.register_cli_opt(cfg.DictOpt('dt', default={'$foo': '$bar',
                                                              '$goo': 'goo',
                                                              'har': '$har',
                                                              'key1': 'str',
                                                              'key2': 12345}))

        self.conf([])

        self.assertEqual('blaa', self.conf.dt['floo'])
        self.assertEqual('goo', self.conf.dt['gloo'])
        self.assertEqual('hlaa', self.conf.dt['har'])
        self.assertEqual('str', self.conf.dt['key1'])
        self.assertEqual(12345, self.conf.dt['key2'])

    def test_dict_sub_default_from_default_recurse(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default='$foo2'))
        self.conf.register_cli_opt(cfg.StrOpt('foo2', default='floo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='$bar2'))
        self.conf.register_cli_opt(cfg.StrOpt('bar2', default='blaa'))
        self.conf.register_cli_opt(cfg.DictOpt('dt', default={'$foo': '$bar'}))

        self.conf([])

        self.assertEqual('blaa', self.conf.dt['floo'])

    def test_dict_sub_default_from_arg(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default=None))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default=None))
        self.conf.register_cli_opt(cfg.DictOpt('dt', default={'$foo': '$bar'}))

        self.conf(['--foo', 'floo', '--bar', 'blaa'])

        self.assertTrue(hasattr(self.conf, 'dt'))
        self.assertEqual('blaa', self.conf.dt['floo'])

    def test_dict_sub_default_from_config_file(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', default='floo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='blaa'))
        self.conf.register_cli_opt(cfg.DictOpt('dt', default={}))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'dt = $foo:$bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'dt'))
        self.assertEqual('blaa', self.conf.dt['floo'])


class ConfigDirTestCase(BaseTestCase):

    def test_config_dir(self):
        snafu_group = cfg.OptGroup('snafu')
        self.conf.register_group(snafu_group)
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.conf.register_cli_opt(cfg.StrOpt('bell'), group=snafu_group)

        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, '00-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-00\n'
                                        '[snafu]\n'
                                        'bell = whistle-00\n'),
                                       (os.path.join(dir, '02-test'),
                                        '[snafu]\n'
                                        'bell = whistle-02\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-02\n'),
                                       (os.path.join(dir, '01-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-01\n')])

        self.conf(['--foo', 'bar',
                   '--config-dir', os.path.dirname(paths[0])])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar-02', self.conf.foo)
        self.assertTrue(hasattr(self.conf, 'snafu'))
        self.assertTrue(hasattr(self.conf.snafu, 'bell'))
        self.assertEqual('whistle-02', self.conf.snafu.bell)

    def test_config_dir_multistr(self):
        # Demonstrate that values for multistr options found in
        # different sources are combined.
        self.conf.register_cli_opt(cfg.MultiStrOpt('foo'))

        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, '00-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-00\n'),
                                       (os.path.join(dir, '02-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-02\n'),
                                       (os.path.join(dir, '01-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-01\n')])

        self.conf(['--foo', 'bar',
                   '--config-dir', os.path.dirname(paths[0])])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual(['bar', 'bar-00', 'bar-01', 'bar-02'], self.conf.foo)

    def test_config_dir_file_precedence(self):
        snafu_group = cfg.OptGroup('snafu')
        self.conf.register_group(snafu_group)
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.conf.register_cli_opt(cfg.StrOpt('bell'), group=snafu_group)

        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, '00-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-00\n'),
                                       ('01-test',
                                        '[snafu]\n'
                                        'bell = whistle-01\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-01\n'),
                                       ('03-test',
                                        '[snafu]\n'
                                        'bell = whistle-03\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-03\n'),
                                       (os.path.join(dir, '02-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-02\n')])

        self.conf(['--foo', 'bar',
                   '--config-file', paths[1],
                   '--config-dir', os.path.dirname(paths[0]),
                   '--config-file', paths[2], ])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar-03', self.conf.foo)
        self.assertTrue(hasattr(self.conf, 'snafu'))
        self.assertTrue(hasattr(self.conf.snafu, 'bell'))
        self.assertEqual('whistle-03', self.conf.snafu.bell)

    def test_config_dir_default_file_precedence(self):
        snafu_group = cfg.OptGroup('snafu')
        self.conf.register_group(snafu_group)
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.conf.register_cli_opt(cfg.StrOpt('bell'), group=snafu_group)

        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, '00-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-00\n'
                                        '[snafu]\n'
                                        'bell = whistle-11\n'),
                                       ('01-test',
                                        '[snafu]\n'
                                        'bell = whistle-01\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-01\n'),
                                       ('03-test',
                                        '[snafu]\n'
                                        'bell = whistle-03\n'
                                        '[DEFAULT]\n'
                                        'foo = bar-03\n'),
                                       (os.path.join(dir, '02-test'),
                                        '[DEFAULT]\n'
                                        'foo = bar-02\n')])

        self.conf(['--foo', 'bar', '--config-dir', os.path.dirname(paths[0])],
                  default_config_files=[paths[1], paths[2]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar-02', self.conf.foo)
        self.assertTrue(hasattr(self.conf, 'snafu'))
        self.assertTrue(hasattr(self.conf.snafu, 'bell'))
        self.assertEqual('whistle-11', self.conf.snafu.bell)

    def test_config_dir_doesnt_exist(self):
        tmpdir = tempfile.mkdtemp()
        os.rmdir(tmpdir)

        self.assertRaises(cfg.ConfigDirNotFoundError,
                          self.conf,
                          ['--config-dir', tmpdir]
                          )


class ReparseTestCase(BaseTestCase):

    def test_reparse(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', default='r'), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = b\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('b', self.conf.blaa.foo)

        self.conf(['--blaa-foo', 'a'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('a', self.conf.blaa.foo)

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('r', self.conf.blaa.foo)


class OverridesTestCase(BaseTestCase):

    def test_default_none(self):
        self.conf.register_opt(cfg.StrOpt('foo', default='foo'))
        self.conf([])
        self.assertEqual('foo', self.conf.foo)
        self.conf.set_default('foo', None)
        self.assertIsNone(self.conf.foo)
        self.conf.clear_default('foo')
        self.assertEqual('foo', self.conf.foo)

    def test_no_default_override(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        self.conf([])
        self.assertIsNone(self.conf.foo)
        self.conf.set_default('foo', 'bar')
        self.assertEqual('bar', self.conf.foo)
        self.conf.clear_default('foo')
        self.assertIsNone(self.conf.foo)

    def test_default_override(self):
        self.conf.register_opt(cfg.StrOpt('foo', default='foo'))
        self.conf([])
        self.assertEqual('foo', self.conf.foo)
        self.conf.set_default('foo', 'bar')
        self.assertEqual('bar', self.conf.foo)
        self.conf.clear_default('foo')
        self.assertEqual('foo', self.conf.foo)

    def test_set_default_not_in_choices(self):
        self.conf.register_group(cfg.OptGroup('f'))
        self.conf.register_cli_opt(cfg.StrOpt('oo', choices=('a', 'b')),
                                   group='f')
        self.assertRaises(ValueError,
                          self.conf.set_default, 'oo', 'c', 'f')

    def test_wrong_type_default_override(self):
        self.conf.register_opt(cfg.IntOpt('foo', default=1))
        self.conf([])
        self.assertEqual(1, self.conf.foo)
        self.assertRaises(ValueError, self.conf.set_default,
                          'foo', 'not_really_a_int')

    def test_override(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        self.conf.set_override('foo', 'bar')
        self.conf([])
        self.assertEqual('bar', self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)

    def test_override_none(self):
        self.conf.register_opt(cfg.StrOpt('foo', default='foo'))
        self.conf([])
        self.assertEqual('foo', self.conf.foo)
        self.conf.set_override('foo', None)
        self.assertIsNone(self.conf.foo)
        self.conf.clear_override('foo')
        self.assertEqual('foo', self.conf.foo)

    def test_group_no_default_override(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo'), group='blaa')
        self.conf([])
        self.assertIsNone(self.conf.blaa.foo)
        self.conf.set_default('foo', 'bar', group='blaa')
        self.assertEqual('bar', self.conf.blaa.foo)
        self.conf.clear_default('foo', group='blaa')
        self.assertIsNone(self.conf.blaa.foo)

    def test_group_default_override(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', default='foo'), group='blaa')
        self.conf([])
        self.assertEqual('foo', self.conf.blaa.foo)
        self.conf.set_default('foo', 'bar', group='blaa')
        self.assertEqual('bar', self.conf.blaa.foo)
        self.conf.clear_default('foo', group='blaa')
        self.assertEqual('foo', self.conf.blaa.foo)

    def test_group_override(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo'), group='blaa')
        self.assertIsNone(self.conf.blaa.foo)
        self.conf.set_override('foo', 'bar', group='blaa')
        self.conf([])
        self.assertEqual('bar', self.conf.blaa.foo)
        self.conf.clear_override('foo', group='blaa')
        self.assertIsNone(self.conf.blaa.foo)

    def test_cli_bool_default(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foo'))
        self.conf.set_default('foo', True)
        self.assertTrue(self.conf.foo)
        self.conf([])
        self.assertTrue(self.conf.foo)
        self.conf.set_default('foo', False)
        self.assertFalse(self.conf.foo)
        self.conf.clear_default('foo')
        self.assertIsNone(self.conf.foo)

    def test_cli_bool_override(self):
        self.conf.register_cli_opt(cfg.BoolOpt('foo'))
        self.conf.set_override('foo', True)
        self.assertTrue(self.conf.foo)
        self.conf([])
        self.assertTrue(self.conf.foo)
        self.conf.set_override('foo', False)
        self.assertFalse(self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)

    def test__str_override(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        self.conf.set_override('foo', True)
        self.conf([])
        self.assertEqual('True', self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)

    def test__wrong_type_override(self):
        self.conf.register_opt(cfg.IntOpt('foo'))
        self.assertRaises(ValueError, self.conf.set_override,
                          'foo', "not_really_a_int")

    def test_set_override_in_choices(self):
        self.conf.register_group(cfg.OptGroup('f'))
        self.conf.register_cli_opt(cfg.StrOpt('oo', choices=('a', 'b')),
                                   group='f')
        self.conf.set_override('oo', 'b', 'f')
        self.assertEqual('b', self.conf.f.oo)

    def test_set_override_not_in_choices(self):
        self.conf.register_group(cfg.OptGroup('f'))
        self.conf.register_cli_opt(cfg.StrOpt('oo', choices=('a', 'b')),
                                   group='f')
        self.assertRaises(ValueError,
                          self.conf.set_override, 'oo', 'c', 'f')

    def test_bool_override(self):
        self.conf.register_opt(cfg.BoolOpt('foo'))
        self.conf.set_override('foo', 'True')
        self.conf([])
        self.assertTrue(self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)

    def test_int_override_with_None(self):
        self.conf.register_opt(cfg.IntOpt('foo'))
        self.conf.set_override('foo', None)
        self.conf([])
        self.assertIsNone(self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)

    def test_str_override_with_None(self):
        self.conf.register_opt(cfg.StrOpt('foo'))
        self.conf.set_override('foo', None)
        self.conf([])
        self.assertIsNone(self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)

    def test_List_override(self):
        self.conf.register_opt(cfg.ListOpt('foo'))
        self.conf.set_override('foo', ['aa', 'bb'])
        self.conf([])
        self.assertEqual(['aa', 'bb'], self.conf.foo)
        self.conf.clear_override('foo')
        self.assertIsNone(self.conf.foo)


class ResetAndClearTestCase(BaseTestCase):

    def test_clear(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar'), group='blaa')

        self.assertIsNone(self.conf.foo)
        self.assertIsNone(self.conf.blaa.bar)

        self.conf(['--foo', 'foo', '--blaa-bar', 'bar'])

        self.assertEqual('foo', self.conf.foo)
        self.assertEqual('bar', self.conf.blaa.bar)

        self.conf.clear()

        self.assertIsNone(self.conf.foo)
        self.assertIsNone(self.conf.blaa.bar)

    def test_reset_and_clear_with_defaults_and_overrides(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar'), group='blaa')

        self.conf.set_default('foo', 'foo')
        self.conf.set_override('bar', 'bar', group='blaa')

        self.conf(['--foo', 'foofoo'])

        self.assertEqual('foofoo', self.conf.foo)
        self.assertEqual('bar', self.conf.blaa.bar)

        self.conf.clear()

        self.assertEqual('foo', self.conf.foo)
        self.assertEqual('bar', self.conf.blaa.bar)

        self.conf.reset()

        self.assertIsNone(self.conf.foo)
        self.assertIsNone(self.conf.blaa.bar)


class UnregisterOptTestCase(BaseTestCase):

    def test_unregister_opt(self):
        opts = [cfg.StrOpt('foo'), cfg.StrOpt('bar')]

        self.conf.register_opts(opts)

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertTrue(hasattr(self.conf, 'bar'))

        self.conf.unregister_opt(opts[0])

        self.assertFalse(hasattr(self.conf, 'foo'))
        self.assertTrue(hasattr(self.conf, 'bar'))

        self.conf([])

        self.assertRaises(cfg.ArgsAlreadyParsedError,
                          self.conf.unregister_opt, opts[1])

        self.conf.clear()

        self.assertTrue(hasattr(self.conf, 'bar'))

        self.conf.unregister_opts(opts)

    def test_unregister_opt_from_group(self):
        opt = cfg.StrOpt('foo')

        self.conf.register_opt(opt, group='blaa')

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))

        self.conf.unregister_opt(opt, group='blaa')

        self.assertFalse(hasattr(self.conf.blaa, 'foo'))


class ImportOptTestCase(BaseTestCase):

    def test_import_opt(self):
        self.assertFalse(hasattr(cfg.CONF, 'blaa'))
        cfg.CONF.import_opt('blaa', 'oslo_config.tests.testmods.blaa_opt')
        self.assertTrue(hasattr(cfg.CONF, 'blaa'))

    def test_import_opt_in_group(self):
        self.assertFalse(hasattr(cfg.CONF, 'bar'))
        cfg.CONF.import_opt('foo', 'oslo_config.tests.testmods.bar_foo_opt',
                            group='bar')
        self.assertTrue(hasattr(cfg.CONF, 'bar'))
        self.assertTrue(hasattr(cfg.CONF.bar, 'foo'))

    def test_import_opt_import_errror(self):
        self.assertRaises(ImportError, cfg.CONF.import_opt,
                          'blaa', 'oslo_config.tests.testmods.blaablaa_opt')

    def test_import_opt_no_such_opt(self):
        self.assertRaises(cfg.NoSuchOptError, cfg.CONF.import_opt,
                          'blaablaa', 'oslo_config.tests.testmods.blaa_opt')

    def test_import_opt_no_such_group(self):
        self.assertRaises(cfg.NoSuchGroupError, cfg.CONF.import_opt,
                          'blaa', 'oslo_config.tests.testmods.blaa_opt',
                          group='blaa')


class ImportGroupTestCase(BaseTestCase):

    def test_import_group(self):
        self.assertFalse(hasattr(cfg.CONF, 'qux'))
        cfg.CONF.import_group('qux', 'oslo_config.tests.testmods.baz_qux_opt')
        self.assertTrue(hasattr(cfg.CONF, 'qux'))
        self.assertTrue(hasattr(cfg.CONF.qux, 'baz'))

    def test_import_group_import_error(self):
        self.assertRaises(ImportError, cfg.CONF.import_group,
                          'qux', 'oslo_config.tests.testmods.bazzz_quxxx_opt')

    def test_import_group_no_such_group(self):
        self.assertRaises(cfg.NoSuchGroupError, cfg.CONF.import_group,
                          'quxxx', 'oslo_config.tests.testmods.baz_qux_opt')


class RequiredOptsTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.conf.register_opt(cfg.StrOpt('boo', required=False))

    def test_required_opt(self):
        self.conf.register_opt(cfg.StrOpt('foo', required=True))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_required_cli_opt(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', required=True))

        self.conf(['--foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_required_cli_opt_with_dash(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo-bar', required=True))

        self.conf(['--foo-bar', 'baz'])

        self.assertTrue(hasattr(self.conf, 'foo_bar'))
        self.assertEqual('baz', self.conf.foo_bar)

    def test_missing_required_opt(self):
        self.conf.register_opt(cfg.StrOpt('foo', required=True))
        self.assertRaises(cfg.RequiredOptError, self.conf, [])

    def test_missing_required_cli_opt(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', required=True))
        self.assertRaises(cfg.RequiredOptError, self.conf, [])

    def test_required_group_opt(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', required=True), group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[blaa]\n'
                                        'foo = bar')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_required_cli_group_opt(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=True), group='blaa')

        self.conf(['--blaa-foo', 'bar'])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'foo'))
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_missing_required_group_opt(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo', required=True), group='blaa')
        self.assertRaises(cfg.RequiredOptError, self.conf, [])

    def test_missing_required_cli_group_opt(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(
            cfg.StrOpt('foo', required=True), group='blaa')
        self.assertRaises(cfg.RequiredOptError, self.conf, [])

    def test_required_opt_with_default(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', required=True))
        self.conf.set_default('foo', 'bar')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_required_opt_with_override(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', required=True))
        self.conf.set_override('foo', 'bar')

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)


class SadPathTestCase(BaseTestCase):

    def test_unknown_attr(self):
        self.conf([])
        self.assertFalse(hasattr(self.conf, 'foo'))
        self.assertRaises(AttributeError, getattr, self.conf, 'foo')
        self.assertRaises(cfg.NoSuchOptError, self.conf._get, 'foo')
        self.assertRaises(cfg.NoSuchOptError, self.conf.__getattr__, 'foo')

    def test_unknown_attr_is_attr_error(self):
        self.conf([])
        self.assertFalse(hasattr(self.conf, 'foo'))
        self.assertRaises(AttributeError, getattr, self.conf, 'foo')

    def test_unknown_group_attr(self):
        self.conf.register_group(cfg.OptGroup('blaa'))

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertFalse(hasattr(self.conf.blaa, 'foo'))
        self.assertRaises(cfg.NoSuchOptError, getattr, self.conf.blaa, 'foo')

    def test_ok_duplicate(self):
        opt = cfg.StrOpt('foo')
        self.conf.register_cli_opt(opt)
        opt2 = cfg.StrOpt('foo')
        self.conf.register_cli_opt(opt2)

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertIsNone(self.conf.foo)

    def test_error_duplicate(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', help='bar'))
        self.assertRaises(cfg.DuplicateOptError,
                          self.conf.register_cli_opt, cfg.StrOpt('foo'))

    def test_error_duplicate_with_different_dest(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', dest='f'))
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.assertRaises(cfg.DuplicateOptError, self.conf, [])

    def test_error_duplicate_short(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', short='f'))
        self.conf.register_cli_opt(cfg.StrOpt('bar', short='f'))
        self.assertRaises(cfg.DuplicateOptError, self.conf, [])

    def test_already_parsed(self):
        self.conf([])

        self.assertRaises(cfg.ArgsAlreadyParsedError,
                          self.conf.register_cli_opt, cfg.StrOpt('foo'))

    def test_bad_cli_arg(self):
        self.conf.register_opt(cfg.BoolOpt('foo'))

        self.useFixture(fixtures.MonkeyPatch('sys.stderr', io.StringIO()))

        self.assertRaises(SystemExit, self.conf, ['--foo'])

        self.assertIn('error', sys.stderr.getvalue())
        self.assertIn('--foo', sys.stderr.getvalue())

    def _do_test_bad_cli_value(self, opt_class):
        self.conf.register_cli_opt(opt_class('foo'))

        self.useFixture(fixtures.MonkeyPatch('sys.stderr', io.StringIO()))

        self.assertRaises(SystemExit, self.conf, ['--foo', 'bar'])

        self.assertIn('foo', sys.stderr.getvalue())
        self.assertIn('bar', sys.stderr.getvalue())

    def test_bad_int_arg(self):
        self._do_test_bad_cli_value(cfg.IntOpt)

    def test_bad_float_arg(self):
        self._do_test_bad_cli_value(cfg.FloatOpt)

    def test_conf_file_not_found(self):
        (fd, path) = tempfile.mkstemp()

        os.remove(path)

        self.assertRaises(cfg.ConfigFilesNotFoundError,
                          self.conf, ['--config-file', path])

    def test_conf_file_permission_denied(self):
        (fd, path) = tempfile.mkstemp()

        os.chmod(path, 0x000)

        self.assertRaises(cfg.ConfigFilesPermissionDeniedError,
                          self.conf, ['--config-file', path])
        os.remove(path)

    def test_conf_file_broken(self):
        paths = self.create_tempfiles([('test', 'foo')])

        self.assertRaises(cfg.ConfigFileParseError,
                          self.conf, ['--config-file', paths[0]])

    def _do_test_conf_file_bad_value(self, opt_class):
        self.conf.register_opt(opt_class('foo'))

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n')])

        self.conf(['--config-file', paths[0]])

        self.assertRaises(ValueError, getattr, self.conf, 'foo')
        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')

    def test_conf_file_bad_bool(self):
        self._do_test_conf_file_bad_value(cfg.BoolOpt)

    def test_conf_file_bad_int(self):
        self._do_test_conf_file_bad_value(cfg.IntOpt)

    def test_conf_file_bad_float(self):
        self._do_test_conf_file_bad_value(cfg.FloatOpt)

    def test_str_sub_none_value(self):
        self.conf.register_cli_opt(cfg.StrOpt('oo'))
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='$oo'))
        self.conf.register_cli_opt(cfg.StrOpt('barbar', default='foo $oo foo'))

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual('', self.conf.bar)
        self.assertEqual("foo  foo", self.conf.barbar)

    def test_str_sub_from_group(self):
        self.conf.register_group(cfg.OptGroup('f'))
        self.conf.register_cli_opt(cfg.StrOpt('oo', default='blaa'), group='f')
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='$f.oo'))

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual("blaa", self.conf.bar)

    def test_str_sub_from_group_with_brace(self):
        self.conf.register_group(cfg.OptGroup('f'))
        self.conf.register_cli_opt(cfg.StrOpt('oo', default='blaa'), group='f')
        self.conf.register_cli_opt(cfg.StrOpt('bar', default='${f.oo}'))

        self.conf([])

        self.assertTrue(hasattr(self.conf, 'bar'))
        self.assertEqual("blaa", self.conf.bar)

    def test_set_default_unknown_attr(self):
        self.conf([])
        self.assertRaises(
            cfg.NoSuchOptError, self.conf.set_default, 'foo', 'bar')

    def test_set_default_unknown_group(self):
        self.conf([])
        self.assertRaises(cfg.NoSuchGroupError,
                          self.conf.set_default, 'foo', 'bar', group='blaa')

    def test_set_override_unknown_attr(self):
        self.conf([])
        self.assertRaises(
            cfg.NoSuchOptError, self.conf.set_override, 'foo', 'bar')

    def test_set_override_unknown_group(self):
        self.conf([])
        self.assertRaises(cfg.NoSuchGroupError,
                          self.conf.set_override, 'foo', 'bar', group='blaa')


class FindFileTestCase(BaseTestCase):

    def test_find_file_without_init(self):
        self.assertRaises(cfg.NotInitializedError,
                          self.conf.find_file, 'foo.json')

    def test_find_policy_file(self):
        policy_file = '/etc/policy.json'

        self.useFixture(fixtures.MonkeyPatch(
                        'os.path.exists',
                        lambda p: p == policy_file))

        self.conf([])

        self.assertIsNone(self.conf.find_file('foo.json'))
        self.assertEqual(policy_file, self.conf.find_file('policy.json'))

    def test_find_policy_file_with_config_file(self):
        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        paths = self.create_tempfiles([(os.path.join(dir, 'test.conf'),
                                        '[DEFAULT]'),
                                       (os.path.join(dir, 'policy.json'),
                                        '{}')],
                                      ext='')

        self.conf(['--config-file', paths[0]])

        self.assertEqual(paths[1], self.conf.find_file('policy.json'))

    def test_find_policy_file_with_multiple_config_dirs(self):
        dir1 = tempfile.mkdtemp()
        self.tempdirs.append(dir1)

        dir2 = tempfile.mkdtemp()
        self.tempdirs.append(dir2)

        self.conf(['--config-dir', dir1, '--config-dir', dir2])
        self.assertEqual(2, len(self.conf.config_dirs))
        self.assertEqual(dir1, self.conf.config_dirs[0])
        self.assertEqual(dir2, self.conf.config_dirs[1])

    def test_config_dirs_empty_list_when_nothing_parsed(self):
        self.assertEqual([], self.conf.config_dirs)

    def test_find_policy_file_with_config_dir(self):
        dir = tempfile.mkdtemp()
        self.tempdirs.append(dir)

        dir2 = tempfile.mkdtemp()
        self.tempdirs.append(dir2)

        path = self.create_tempfiles([(os.path.join(dir, 'policy.json'),
                                       '{}')],
                                     ext='')[0]

        self.conf(['--config-dir', dir, '--config-dir', dir2])

        self.assertEqual(path, self.conf.find_file('policy.json'))


class OptDumpingTestCase(BaseTestCase):

    class FakeLogger(object):

        def __init__(self, test_case, expected_lvl):
            self.test_case = test_case
            self.expected_lvl = expected_lvl
            self.logged = []

        def log(self, lvl, fmt, *args):
            self.test_case.assertEqual(lvl, self.expected_lvl)
            self.logged.append(fmt % args)

    def setUp(self):
        super(OptDumpingTestCase, self).setUp()
        self._args = ['--foo', 'this', '--blaa-bar', 'that',
                      '--blaa-key', 'admin', '--passwd', 'hush']

    def _do_test_log_opt_values(self, args):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        self.conf.register_cli_opt(cfg.StrOpt('passwd', secret=True))
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(cfg.StrOpt('bar'), 'blaa')
        self.conf.register_cli_opt(cfg.StrOpt('key', secret=True), 'blaa')

        self.conf(args)

        logger = self.FakeLogger(self, 666)

        self.conf.log_opt_values(logger, 666)

        self.assertEqual([
                         "*" * 80,
                         "Configuration options gathered from:",
                         "command line args: ['--foo', 'this', '--blaa-bar', "
                         "'that', '--blaa-key', 'admin', '--passwd', 'hush']",
                         "config files: []",
                         "=" * 80,
                         "config_dir                     = []",
                         "config_file                    = []",
                         "config_source                  = []",
                         "foo                            = this",
                         "passwd                         = ****",
                         "blaa.bar                       = that",
                         "blaa.key                       = ****",
                         "*" * 80,
                         ], logger.logged)

    def test_log_opt_values(self):
        self._do_test_log_opt_values(self._args)

    def test_log_opt_values_from_sys_argv(self):
        self.useFixture(fixtures.MonkeyPatch('sys.argv', ['foo'] + self._args))
        self._do_test_log_opt_values(None)

    def test_log_opt_values_empty_config(self):
        empty_conf = cfg.ConfigOpts()

        logger = self.FakeLogger(self, 666)

        empty_conf.log_opt_values(logger, 666)
        self.assertEqual([
                         "*" * 80,
                         "Configuration options gathered from:",
                         "command line args: None",
                         "config files: []",
                         "=" * 80,
                         "config_source                  = []",
                         "*" * 80,
                         ], logger.logged)


class ConfigParserTestCase(BaseTestCase):

    def test_parse_file(self):
        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        '[BLAA]\n'
                                        'bar = foo\n')])

        sections = {}
        parser = cfg.ConfigParser(paths[0], sections)
        parser.parse()

        self.assertIn('DEFAULT', sections)
        self.assertIn('BLAA', sections)
        self.assertEqual(sections['DEFAULT']['foo'], ['bar'])
        self.assertEqual(sections['BLAA']['bar'], ['foo'])

    def test_parse_file_with_normalized(self):
        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        '[BLAA]\n'
                                        'bar = foo\n')])

        sections = {}
        normalized = {}
        parser = cfg.ConfigParser(paths[0], sections)
        parser._add_normalized(normalized)
        parser.parse()

        self.assertIn('DEFAULT', sections)
        self.assertIn('DEFAULT', normalized)
        self.assertIn('BLAA', sections)
        self.assertIn('blaa', normalized)
        self.assertEqual(sections['DEFAULT']['foo'], ['bar'])
        self.assertEqual(normalized['DEFAULT']['foo'], ['bar'])
        self.assertEqual(sections['BLAA']['bar'], ['foo'])
        self.assertEqual(normalized['blaa']['bar'], ['foo'])

    def test_no_section(self):
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'foo = bar')
            tmpfile.flush()

            parser = cfg.ConfigParser(tmpfile.name, {})
            self.assertRaises(cfg.ParseError, parser.parse)

    def test__parse_file_ioerror(self):
        # Test that IOErrors (other than 'No such file or directory')
        # are propagated.
        filename = 'fake'
        namespace = mock.Mock()
        with mock.patch('oslo_config.cfg.ConfigParser.parse') as parse:
            parse.side_effect = IOError(errno.EMFILE, filename,
                                        'Too many open files')
            self.assertRaises(IOError, cfg.ConfigParser._parse_file, filename,
                              namespace)


class NamespaceTestCase(BaseTestCase):
    def setUp(self):
        super(NamespaceTestCase, self).setUp()
        self.ns = cfg._Namespace(self.conf)

    def read(self, *texts):
        paths = ((str(i), t) for i, t in enumerate(texts))
        for path in self.create_tempfiles(paths):
            cfg.ConfigParser._parse_file(path, self.ns)

    def assertAbsent(self, key, normalized=False):
        self.assertRaises(KeyError, self.ns._get_value, [key],
                          normalized=normalized)

    def assertValue(self, key, expect, multi=False, normalized=False):
        actual, _ = self.ns._get_value([key], multi=multi,
                                       normalized=normalized)
        self.assertEqual(actual, expect)

    def test_cli(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo'))
        key = (None, 'foo')
        self.assertAbsent(key)

        self.read('[DEFAULT]\n'
                  'foo = file0\n')
        self.assertValue(key, 'file0')

        self.read('[DEFAULT]\n'
                  'foo = file1\n')
        self.assertEqual('file1', self.ns._get_cli_value([key]))

    def test_single_file(self):
        self.read('[DEFAULT]\n'
                  'foo = bar\n'
                  '[BLAA]\n'
                  'bar = foo\n')

        self.assertValue(('DEFAULT', 'foo'), 'bar')
        self.assertValue(('DEFAULT', 'foo'), ['bar'], multi=True)
        self.assertValue(('DEFAULT', 'foo'), ['bar'], multi=True)
        self.assertValue((None, 'foo'), ['bar'], multi=True)
        self.assertValue(('DEFAULT', 'foo'), ['bar'], multi=True,
                         normalized=True)

        self.assertValue(('BLAA', 'bar'), 'foo')
        self.assertValue(('BLAA', 'bar'), ['foo'], multi=True)
        self.assertValue(('blaa', 'bar'), ['foo'], multi=True,
                         normalized=True)

    def test_multiple_files(self):
        self.read('[DEFAULT]\n'
                  'foo = bar\n'
                  '[BLAA]\n'
                  'bar = foo',

                  '[DEFAULT]\n'
                  'foo = barbar\n'
                  '[BLAA]\n'
                  'bar = foofoo\n'
                  '[bLAa]\n'
                  'bar = foofoofoo\n')

        self.assertValue(('DEFAULT', 'foo'), 'barbar')
        self.assertValue(('DEFAULT', 'foo'), ['bar', 'barbar'], multi=True)

        self.assertValue(('BLAA', 'bar'), 'foofoo')
        self.assertValue(('bLAa', 'bar'), 'foofoofoo')
        self.assertValue(('BLAA', 'bar'), ['foo', 'foofoo'], multi=True)
        self.assertValue(('Blaa', 'bar'), ['foo', 'foofoo', 'foofoofoo'],
                         multi=True, normalized=True)

    def test_attrs_subparser(self):
        CONF = cfg.ConfigOpts()
        CONF.register_cli_opt(cfg.SubCommandOpt(
            'foo', handler=lambda sub: sub.add_parser('foo')))
        CONF(['foo'])

    def test_attrs_subparser_failure(self):
        CONF = cfg.ConfigOpts()
        CONF.register_cli_opt(cfg.SubCommandOpt(
            'foo', handler=lambda sub: sub.add_parser('foo')))
        self.assertRaises(SystemExit, CONF, ['foo', 'bar'])


class TildeExpansionTestCase(BaseTestCase):

    def test_config_file_tilde(self):
        homedir = os.path.expanduser('~')
        tmpfile = tempfile.mktemp(dir=homedir, prefix='cfg-', suffix='.conf')
        tmpbase = os.path.basename(tmpfile)

        try:
            self.conf(['--config-file', os.path.join('~', tmpbase)])
        except cfg.ConfigFilesNotFoundError as cfnfe:
            self.assertIn(homedir, str(cfnfe))

        self.useFixture(fixtures.MonkeyPatch(
            'os.path.exists',
            lambda p: p == tmpfile))

        self.assertEqual(tmpfile, self.conf.find_file(tmpbase))

    def test_config_dir_tilde(self):
        homedir = os.path.expanduser('~')
        try:
            tmpdir = tempfile.mkdtemp(dir=homedir,
                                      prefix='cfg-',
                                      suffix='.d')
            tmpfile = os.path.join(tmpdir, 'foo.conf')

            self.useFixture(fixtures.MonkeyPatch(
                            'glob.glob',
                            lambda p: [tmpfile]))

            e = self.assertRaises(cfg.ConfigFilesNotFoundError,
                                  self.conf,
                                  ['--config-dir',
                                   os.path.join('~',
                                                os.path.basename(tmpdir))]
                                  )
            self.assertIn(tmpdir, str(e))
        finally:
            try:
                shutil.rmtree(tmpdir)
            except OSError as exc:
                if exc.errno != 2:
                    raise


class SubCommandTestCase(BaseTestCase):

    def test_sub_command(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')
            sub.add_argument('bar', type=int)

        self.conf.register_cli_opt(
            cfg.SubCommandOpt('cmd', handler=add_parsers))
        self.assertTrue(hasattr(self.conf, 'cmd'))
        self.conf(['a', '10'])
        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertTrue(hasattr(self.conf.cmd, 'bar'))
        self.assertEqual('a', self.conf.cmd.name)
        self.assertEqual(10, self.conf.cmd.bar)

    def test_sub_command_with_parent(self):
        def add_parsers(subparsers):
            parent = argparse.ArgumentParser(add_help=False)
            parent.add_argument('bar', type=int)
            subparsers.add_parser('a', parents=[parent])

        self.conf.register_cli_opt(
            cfg.SubCommandOpt('cmd', handler=add_parsers))
        self.assertTrue(hasattr(self.conf, 'cmd'))
        self.conf(['a', '10'])
        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertTrue(hasattr(self.conf.cmd, 'bar'))
        self.assertEqual('a', self.conf.cmd.name)
        self.assertEqual(10, self.conf.cmd.bar)

    def test_sub_command_with_dest(self):
        def add_parsers(subparsers):
            subparsers.add_parser('a')

        self.conf.register_cli_opt(
            cfg.SubCommandOpt('cmd', dest='command', handler=add_parsers))
        self.assertTrue(hasattr(self.conf, 'command'))
        self.conf(['a'])
        self.assertEqual('a', self.conf.command.name)

    def test_sub_command_with_group(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')
            sub.add_argument('--bar', choices='XYZ')

        self.conf.register_cli_opt(
            cfg.SubCommandOpt('cmd', handler=add_parsers), group='blaa')
        self.assertTrue(hasattr(self.conf, 'blaa'))
        self.assertTrue(hasattr(self.conf.blaa, 'cmd'))
        self.conf(['a', '--bar', 'Z'])
        self.assertTrue(hasattr(self.conf.blaa.cmd, 'name'))
        self.assertTrue(hasattr(self.conf.blaa.cmd, 'bar'))
        self.assertEqual('a', self.conf.blaa.cmd.name)
        self.assertEqual('Z', self.conf.blaa.cmd.bar)

    def test_sub_command_not_cli(self):
        self.conf.register_opt(cfg.SubCommandOpt('cmd'))
        self.conf([])

    def test_sub_command_resparse(self):
        def add_parsers(subparsers):
            subparsers.add_parser('a')

        self.conf.register_cli_opt(
            cfg.SubCommandOpt('cmd', handler=add_parsers))

        foo_opt = cfg.StrOpt('foo')
        self.conf.register_cli_opt(foo_opt)

        self.conf(['--foo=bar', 'a'])

        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertEqual('a', self.conf.cmd.name)
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

        self.conf.clear()
        self.conf.unregister_opt(foo_opt)
        self.conf(['a'])

        self.assertTrue(hasattr(self.conf.cmd, 'name'))
        self.assertEqual('a', self.conf.cmd.name)
        self.assertFalse(hasattr(self.conf, 'foo'))

    def test_sub_command_no_handler(self):
        self.conf.register_cli_opt(cfg.SubCommandOpt('cmd'))
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, [])
        self.assertIn('error', sys.stderr.getvalue())

    def test_sub_command_with_help(self):
        def add_parsers(subparsers):
            subparsers.add_parser('a')

        self.conf.register_cli_opt(cfg.SubCommandOpt('cmd',
                                                     title='foo foo',
                                                     description='bar bar',
                                                     help='blaa blaa',
                                                     handler=add_parsers))
        self.useFixture(fixtures.MonkeyPatch('sys.stdout', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, ['--help'])
        self.assertIn('foo foo', sys.stdout.getvalue())
        self.assertIn('bar bar', sys.stdout.getvalue())
        self.assertIn('blaa blaa', sys.stdout.getvalue())

    def test_sub_command_errors(self):
        def add_parsers(subparsers):
            sub = subparsers.add_parser('a')
            sub.add_argument('--bar')

        self.conf.register_cli_opt(cfg.BoolOpt('bar'))
        self.conf.register_cli_opt(
            cfg.SubCommandOpt('cmd', handler=add_parsers))
        self.conf(['a'])
        self.assertRaises(cfg.DuplicateOptError, getattr, self.conf.cmd, 'bar')
        self.assertRaises(cfg.NoSuchOptError, getattr, self.conf.cmd, 'foo')

    def test_sub_command_multiple(self):
        self.conf.register_cli_opt(cfg.SubCommandOpt('cmd1'))
        self.conf.register_cli_opt(cfg.SubCommandOpt('cmd2'))
        self.useFixture(fixtures.MonkeyPatch('sys.stderr', io.StringIO()))
        self.assertRaises(SystemExit, self.conf, [])
        self.assertIn('multiple', sys.stderr.getvalue())


class SetDefaultsTestCase(BaseTestCase):

    def test_default_to_none(self):
        opts = [cfg.StrOpt('foo', default='foo')]
        self.conf.register_opts(opts)
        cfg.set_defaults(opts, foo=None)
        self.conf([])
        self.assertIsNone(self.conf.foo)

    def test_default_from_none(self):
        opts = [cfg.StrOpt('foo')]
        self.conf.register_opts(opts)
        cfg.set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEqual('bar', self.conf.foo)

    def test_change_default(self):
        opts = [cfg.StrOpt('foo', default='foo')]
        self.conf.register_opts(opts)
        cfg.set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEqual('bar', self.conf.foo)

    def test_change_default_many(self):
        opts = [cfg.StrOpt('foo', default='foo'),
                cfg.StrOpt('foo2', default='foo2')]
        self.conf.register_opts(opts)
        cfg.set_defaults(opts, foo='bar', foo2='bar2')
        self.conf([])
        self.assertEqual('bar', self.conf.foo)
        self.assertEqual('bar2', self.conf.foo2)

    def test_group_default_to_none(self):
        opts = [cfg.StrOpt('foo', default='foo')]
        self.conf.register_opts(opts, group='blaa')
        cfg.set_defaults(opts, foo=None)
        self.conf([])
        self.assertIsNone(self.conf.blaa.foo)

    def test_group_default_from_none(self):
        opts = [cfg.StrOpt('foo')]
        self.conf.register_opts(opts, group='blaa')
        cfg.set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_group_change_default(self):
        opts = [cfg.StrOpt('foo', default='foo')]
        self.conf.register_opts(opts, group='blaa')
        cfg.set_defaults(opts, foo='bar')
        self.conf([])
        self.assertEqual('bar', self.conf.blaa.foo)


class DeprecatedOptionsTestCase(BaseTestCase):

    def test_deprecated_opts_equal(self):
        d1 = cfg.DeprecatedOpt('oldfoo', group='oldgroup')
        d2 = cfg.DeprecatedOpt('oldfoo', group='oldgroup')
        self.assertEqual(d1, d2)

    def test_deprecated_opts_not_equal(self):
        d1 = cfg.DeprecatedOpt('oldfoo', group='oldgroup')
        d2 = cfg.DeprecatedOpt('oldfoo2', group='oldgroup')
        self.assertNotEqual(d1, d2)


class MultipleDeprecatedOptionsTestCase(BaseTestCase):

    def test_conf_file_override_use_deprecated_name_and_group(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_opt(cfg.StrOpt('foo',
                                          deprecated_name='oldfoo',
                                          deprecated_group='oldgroup'),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[oldgroup]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_conf_file_override_use_deprecated_opts(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        oldopts = [cfg.DeprecatedOpt('oldfoo', group='oldgroup')]
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_opts=oldopts),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[oldgroup]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_conf_file_override_use_deprecated_multi_opts(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        oldopts = [cfg.DeprecatedOpt('oldfoo', group='oldgroup'),
                   cfg.DeprecatedOpt('oldfoo2', group='oldgroup2')]
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_opts=oldopts),
                               group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[oldgroup2]\n'
                                        'oldfoo2 = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bar', self.conf.blaa.foo)


class MultipleDeprecatedCliOptionsTestCase(BaseTestCase):

    def test_conf_file_override_use_deprecated_name_and_group(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              deprecated_name='oldfoo',
                                              deprecated_group='oldgroup'),
                                   group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[oldgroup]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_conf_file_override_use_deprecated_opts(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        oldopts = [cfg.DeprecatedOpt('oldfoo', group='oldgroup')]
        self.conf.register_cli_opt(cfg.StrOpt('foo', deprecated_opts=oldopts),
                                   group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[oldgroup]\n'
                                        'oldfoo = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_conf_file_override_use_deprecated_multi_opts(self):
        self.conf.register_group(cfg.OptGroup('blaa'))
        oldopts = [cfg.DeprecatedOpt('oldfoo', group='oldgroup'),
                   cfg.DeprecatedOpt('oldfoo2', group='oldgroup2')]
        self.conf.register_cli_opt(cfg.StrOpt('foo', deprecated_opts=oldopts),
                                   group='blaa')

        paths = self.create_tempfiles([('test',
                                        '[oldgroup2]\n'
                                        'oldfoo2 = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bar', self.conf.blaa.foo)

    def test_conf_file_common_deprecated_group(self):
        self.conf.register_group(cfg.OptGroup('foo'))
        self.conf.register_group(cfg.OptGroup('bar'))
        oldopts = [cfg.DeprecatedOpt('foo', group='DEFAULT')]
        self.conf.register_opt(cfg.StrOpt('common_opt',
                                          deprecated_opts=oldopts),
                               group='bar')
        self.conf.register_opt(cfg.StrOpt('common_opt',
                                          deprecated_opts=oldopts),
                               group='foo')

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bla\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bla', self.conf.foo.common_opt)
        self.assertEqual('bla', self.conf.bar.common_opt)

        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n'
                                        'foo = bla\n'
                                        '[bar]\n'
                                        'common_opt = blabla\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bla', self.conf.foo.common_opt)
        self.assertEqual('blabla', self.conf.bar.common_opt)

        paths = self.create_tempfiles([('test',
                                        '[foo]\n'
                                        'common_opt = bla\n'
                                        '[bar]\n'
                                        'common_opt = blabla\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('bla', self.conf.foo.common_opt)
        self.assertEqual('blabla', self.conf.bar.common_opt)


class ChoicesTestCase(BaseTestCase):

    def test_choice_default(self):
        self.conf.register_cli_opt(cfg.StrOpt('protocol',
                                   default='http',
                                   choices=['http', 'https', 'ftp']))
        self.conf([])
        self.assertEqual('http', self.conf.protocol)

    def test_choice_good(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                   choices=['bar1', 'bar2']))
        self.conf(['--foo', 'bar1'])
        self.assertEqual('bar1', self.conf.foo)

    def test_choice_bad(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                   choices=['bar1', 'bar2']))
        self.assertRaises(SystemExit, self.conf, ['--foo', 'bar3'])

    def test_conf_file_choice_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                               choices=['bar1', 'bar2']))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bar1\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar1', self.conf.foo)

    def test_conf_file_choice_empty_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                               choices=['', 'bar1', 'bar2']))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = \n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('', self.conf.foo)

    def test_conf_file_choice_none_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                               default=None,
                               choices=[None, 'bar1', 'bar2']))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertIsNone(self.conf.foo)

    def test_conf_file_bad_choice_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                               choices=['bar1', 'bar2']))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bar3\n')])

        self.conf(['--config-file', paths[0]])

        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'foo')
        self.assertRaises(ValueError, getattr, self.conf, 'foo')

    def test_conf_file_choice_value_override(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                   choices=['baar', 'baaar']))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'foo = baar\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'foo = baaar\n')])

        self.conf(['--foo', 'baar',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('baaar', self.conf.foo)

    def test_conf_file_choice_bad_default(self):
        self.assertRaises(cfg.DefaultValueError, cfg.StrOpt, 'foo',
                          choices=['baar', 'baaar'], default='foobaz')


class PortChoicesTestCase(BaseTestCase):

    def test_choice_default(self):
        self.conf.register_cli_opt(cfg.PortOpt('port',
                                   default=455,
                                   choices=[80, 455]))
        self.conf([])
        self.assertEqual(455, self.conf.port)

    def test_choice_good_with_list(self):
        self.conf.register_cli_opt(cfg.PortOpt('port',
                                   choices=[80, 8080]))
        self.conf(['--port', '80'])
        self.assertEqual(80, self.conf.port)

    def test_choice_good_with_tuple(self):
        self.conf.register_cli_opt(cfg.PortOpt('port',
                                   choices=(80, 8080)))
        self.conf(['--port', '80'])
        self.assertEqual(80, self.conf.port)

    def test_choice_bad(self):
        self.conf.register_cli_opt(cfg.PortOpt('port',
                                   choices=[80, 8080]))
        self.assertRaises(SystemExit, self.conf, ['--port', '8181'])

    def test_choice_out_range(self):
        self.assertRaisesRegex(ValueError, 'out of bounds',
                               cfg.PortOpt, 'port', choices=[80, 65537, 0])

    def test_conf_file_choice_value(self):
        self.conf.register_opt(cfg.PortOpt('port',
                               choices=[80, 8080]))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''port = 80\n')])

        self.conf(['--config-file', paths[0]])

        self.assertTrue(hasattr(self.conf, 'port'))
        self.assertEqual(80, self.conf.port)

    def test_conf_file_bad_choice_value(self):
        self.conf.register_opt(cfg.PortOpt('port',
                               choices=[80, 8080]))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''port = 8181\n')])

        self.conf(['--config-file', paths[0]])

        self.assertRaises(cfg.ConfigFileValueError, self.conf._get, 'port')
        self.assertRaises(ValueError, getattr, self.conf, 'port')

    def test_conf_file_choice_value_override(self):
        self.conf.register_cli_opt(cfg.PortOpt('port',
                                   choices=[80, 8080]))

        paths = self.create_tempfiles([('1',
                                        '[DEFAULT]\n'
                                        'port = 80\n'),
                                       ('2',
                                        '[DEFAULT]\n'
                                        'port = 8080\n')])

        self.conf(['--port', '80',
                   '--config-file', paths[0],
                   '--config-file', paths[1]])

        self.assertTrue(hasattr(self.conf, 'port'))
        self.assertEqual(8080, self.conf.port)

    def test_conf_file_choice_bad_default(self):
        self.assertRaises(cfg.DefaultValueError, cfg.PortOpt, 'port',
                          choices=[80, 8080], default=8181)


class RegexTestCase(BaseTestCase):

    def test_regex_good(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              regex='foo|bar'))
        self.conf(['--foo', 'bar'])
        self.assertEqual('bar', self.conf.foo)
        self.conf(['--foo', 'foo'])
        self.assertEqual('foo', self.conf.foo)
        self.conf(['--foo', 'foobar'])
        self.assertEqual('foobar', self.conf.foo)

    def test_regex_bad(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              regex='bar'))
        self.assertRaises(SystemExit, self.conf, ['--foo', 'foo'])

    def test_conf_file_regex_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          regex='bar'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_conf_file_regex_bad_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          regex='bar'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = other\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaisesRegex(cfg.ConfigFileValueError, "doesn't match regex",
                               self.conf._get, 'foo')
        self.assertRaisesRegex(ValueError, "doesn't match regex",
                               getattr, self.conf, 'foo')

    def test_regex_with_choice(self):
        self.assertRaises(ValueError, cfg.StrOpt,
                          'foo', choices=['bar1'], regex='bar2')


class QuotesTestCase(BaseTestCase):

    def test_quotes_good(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              quotes=True))
        self.conf(['--foo', '"foobar1"'])
        self.assertEqual('foobar1', self.conf.foo)
        self.conf(['--foo', "'foobar2'"])
        self.assertEqual('foobar2', self.conf.foo)
        self.conf(['--foo', 'foobar3'])
        self.assertEqual('foobar3', self.conf.foo)
        self.conf(['--foo', 'foobar4"'])
        self.assertEqual('foobar4"', self.conf.foo)

    def test_quotes_bad(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              quotes=True))
        self.assertRaises(SystemExit, self.conf, ['--foo', '"foobar\''])
        self.assertRaises(SystemExit, self.conf, ['--foo', '\'foobar"'])
        self.assertRaises(SystemExit, self.conf, ['--foo', '"foobar'])
        self.assertRaises(SystemExit, self.conf, ['--foo', "'foobar"])

    def test_conf_file_quotes_good_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          quotes=True))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = "bar"\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bar', self.conf.foo)

    def test_conf_file_quotes_bad_value(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          quotes=True))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = "bar\n')])

        self.conf(['--config-file', paths[0]])
        self.assertRaisesRegex(cfg.ConfigFileValueError, 'Non-closed quote:',
                               self.conf._get, 'foo')
        self.assertRaisesRegex(ValueError, 'Non-closed quote:',
                               getattr, self.conf, 'foo')


class IgnoreCaseTestCase(BaseTestCase):

    def test_ignore_case_with_choices(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              ignore_case=True,
                                              choices=['bar1',
                                                       'bar2',
                                                       'BAR3']))
        self.conf(['--foo', 'bAr1'])
        self.assertEqual('bAr1', self.conf.foo)
        self.conf(['--foo', 'BaR2'])
        self.assertEqual('BaR2', self.conf.foo)
        self.conf(['--foo', 'baR3'])
        self.assertEqual('baR3', self.conf.foo)

    def test_ignore_case_with_regex(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo',
                                              ignore_case=True,
                                              regex='fOO|bar'))
        self.conf(['--foo', 'foo'])
        self.assertEqual('foo', self.conf.foo)
        self.conf(['--foo', 'Bar'])
        self.assertEqual('Bar', self.conf.foo)
        self.conf(['--foo', 'FOObar'])
        self.assertEqual('FOObar', self.conf.foo)

    def test_conf_file_ignore_case_with_choices(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          ignore_case=True,
                                          choices=['bar1', 'bar2', 'BAR3']))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = bAr2\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('bAr2', self.conf.foo)

    def test_conf_file_ignore_case_with_regex(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          ignore_case=True,
                                          regex='bAr'))

        paths = self.create_tempfiles([('test', '[DEFAULT]\n''foo = BaR\n')])

        self.conf(['--config-file', paths[0]])
        self.assertTrue(hasattr(self.conf, 'foo'))
        self.assertEqual('BaR', self.conf.foo)


class StrOptMaxLengthTestCase(BaseTestCase):

    def test_stropt_max_length_good(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', max_length=5))
        self.conf(['--foo', '12345'])
        self.assertEqual('12345', self.conf.foo)

    def test_stropt_max_length_bad(self):
        self.conf.register_cli_opt(cfg.StrOpt('foo', max_length=5))
        self.assertRaises(SystemExit, self.conf, ['--foo', '123456'])


class URIOptMaxLengthTestCase(BaseTestCase):

    def test_uriopt_max_length_good(self):
        self.conf.register_cli_opt(cfg.URIOpt('foo', max_length=30))
        self.conf(['--foo', 'http://www.example.com'])
        self.assertEqual('http://www.example.com', self.conf.foo)

    def test_uriopt_max_length_bad(self):
        self.conf.register_cli_opt(cfg.URIOpt('foo', max_length=30))
        self.assertRaises(SystemExit, self.conf,
                          ['--foo', 'http://www.example.com/versions'])


class URIOptSchemesTestCase(BaseTestCase):

    def test_uriopt_schemes_good(self):
        self.conf.register_cli_opt(cfg.URIOpt('foo', schemes=['http', 'ftp']))
        self.conf(['--foo', 'http://www.example.com'])
        self.assertEqual('http://www.example.com', self.conf.foo)
        self.conf(['--foo', 'ftp://example.com/archives'])
        self.assertEqual('ftp://example.com/archives', self.conf.foo)

    def test_uriopt_schemes_bad(self):
        self.conf.register_cli_opt(cfg.URIOpt('foo', schemes=['http', 'ftp']))
        self.assertRaises(SystemExit, self.conf,
                          ['--foo', 'https://www.example.com'])
        self.assertRaises(SystemExit, self.conf,
                          ['--foo', 'file://www.example.com'])


class PrintHelpTestCase(base.BaseTestCase):

    def test_print_help_without_init(self):
        conf = cfg.ConfigOpts()
        conf.register_opts([])
        self.assertRaises(cfg.NotInitializedError,
                          conf.print_help)

    def test_print_help_with_clear(self):
        conf = cfg.ConfigOpts()
        conf.register_opts([])
        conf([])
        conf.clear()
        self.assertRaises(cfg.NotInitializedError,
                          conf.print_help)


class OptTestCase(base.BaseTestCase):

    def test_opt_eq(self):
        d1 = cfg.ListOpt('oldfoo')
        d2 = cfg.ListOpt('oldfoo')
        self.assertEqual(d1, d2)

    def test_opt_not_eq(self):
        d1 = cfg.ListOpt('oldfoo')
        d2 = cfg.ListOpt('oldbar')
        self.assertNotEqual(d1, d2)

    def test_illegal_name(self):
        self.assertRaises(ValueError, cfg.BoolOpt, '_foo')


class SectionsTestCase(BaseTestCase):
    def test_list_all_sections(self):
        paths = self.create_tempfiles([('test.ini',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        '[BLAA]\n'
                                        'bar = foo\n'),
                                       ('test2.ini',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        '[BLAA]\n'
                                        'bar = foo\n')])
        self.conf(args=[], default_config_files=paths)
        self.assertEqual(['BLAA', 'DEFAULT'],
                         self.conf.list_all_sections())

    def test_list_all_sections_post_mutate(self):
        paths = self.create_tempfiles([('test.ini',
                                        '[DEFAULT]\n'
                                        'foo = bar\n'
                                        '[BLAA]\n'
                                        'bar = foo\n'),
                                       ('test2.ini',
                                        '[WOMBAT]\n'
                                        'woo = war\n'
                                        '[BLAA]\n'
                                        'bar = foo\n')])
        self.conf(args=[], default_config_files=paths[:1])
        self.assertEqual(['BLAA', 'DEFAULT'],
                         self.conf.list_all_sections())

        shutil.copy(paths[1], paths[0])
        self.conf.mutate_config_files()
        self.assertEqual(['BLAA', 'DEFAULT', 'WOMBAT'],
                         self.conf.list_all_sections())


class DeprecationWarningTestBase(BaseTestCase):
    def setUp(self):
        super(DeprecationWarningTestBase, self).setUp()
        self.log_fixture = self.useFixture(fixtures.FakeLogger())
        self._parser_class = cfg.ConfigParser


@mock.patch('oslo_log.versionutils.report_deprecated_feature',
            _fake_deprecated_feature)
class DeprecationWarningTestScenarios(DeprecationWarningTestBase):
    scenarios = [('default-deprecated', dict(deprecated=True,
                                             group='DEFAULT')),
                 ('default-not-deprecated', dict(deprecated=False,
                                                 group='DEFAULT')),
                 ('other-deprecated', dict(deprecated=True,
                                           group='other')),
                 ('other-not-deprecated', dict(deprecated=False,
                                               group='other')),
                 ]

    def test_deprecated_logging(self):
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_name='bar'))
        self.conf.register_group(cfg.OptGroup('other'))
        self.conf.register_opt(cfg.StrOpt('foo', deprecated_name='bar'),
                               group='other')
        if self.deprecated:
            content = 'bar=baz'
        else:
            content = 'foo=baz'
        paths = self.create_tempfiles([('test',
                                        '[' + self.group + ']\n' +
                                        content + '\n')])

        self.conf(['--config-file', paths[0]])
        # Reference these twice to verify they only get logged once
        if self.group == 'DEFAULT':
            self.assertEqual('baz', self.conf.foo)
            self.assertEqual('baz', self.conf.foo)
        else:
            self.assertEqual('baz', self.conf.other.foo)
            self.assertEqual('baz', self.conf.other.foo)
        if self.deprecated:
            expected = ('Deprecated: ' +
                        cfg._Namespace._deprecated_opt_message %
                        {'dep_option': 'bar',
                         'dep_group': self.group,
                         'option': 'foo',
                         'group': self.group} + '\n')
        else:
            expected = ''
        self.assertEqual(expected, self.log_fixture.output)


@mock.patch('oslo_log.versionutils.report_deprecated_feature',
            _fake_deprecated_feature)
class DeprecationWarningTests(DeprecationWarningTestBase):
    log_prefix = 'Deprecated: '

    def test_DeprecatedOpt(self):
        default_deprecated = [cfg.DeprecatedOpt('bar')]
        other_deprecated = [cfg.DeprecatedOpt('baz', group='other')]
        self.conf.register_group(cfg.OptGroup('other'))
        self.conf.register_opt(cfg.StrOpt('foo',
                                          deprecated_opts=default_deprecated))
        self.conf.register_opt(cfg.StrOpt('foo',
                                          deprecated_opts=other_deprecated),
                               group='other')
        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n' +
                                        'bar=baz\n' +
                                        '[other]\n' +
                                        'baz=baz\n')])
        self.conf(['--config-file', paths[0]])
        self.assertEqual('baz', self.conf.foo)
        self.assertEqual('baz', self.conf.other.foo)
        self.assertIn('Option "bar" from group "DEFAULT"',
                      self.log_fixture.output)
        self.assertIn('Option "baz" from group "other"',
                      self.log_fixture.output)

    def test_check_deprecated(self):
        namespace = cfg._Namespace(None)
        deprecated_list = [('DEFAULT', 'bar')]
        namespace._check_deprecated(('DEFAULT', 'bar'), (None, 'foo'),
                                    deprecated_list)
        self.assert_message_logged('bar', 'DEFAULT', 'foo', 'DEFAULT')

    def assert_message_logged(self, deprecated_name, deprecated_group,
                              current_name, current_group):
        expected = (cfg._Namespace._deprecated_opt_message %
                    {'dep_option': deprecated_name,
                     'dep_group': deprecated_group,
                     'option': current_name,
                     'group': current_group}
                    )
        self.assertEqual(self.log_prefix + expected + '\n',
                         self.log_fixture.output)

    def test_deprecated_for_removal(self):
        self.conf.register_opt(cfg.StrOpt('foo',
                                          deprecated_for_removal=True))
        self.conf.register_opt(cfg.StrOpt('bar',
                                          deprecated_for_removal=True))
        paths = self.create_tempfiles([('test',
                                        '[DEFAULT]\n' +
                                        'foo=bar\n')])
        self.conf(['--config-file', paths[0]])
        # Multiple references should be logged only once.
        self.assertEqual('bar', self.conf.foo)
        self.assertEqual('bar', self.conf.foo)
        # Options not set in the config should not be logged.
        self.assertIsNone(self.conf.bar)
        expected = ('Option "foo" from group "DEFAULT" is deprecated for '
                    'removal.  Its value may be silently ignored in the '
                    'future.\n')
        self.assertEqual(self.log_prefix + expected, self.log_fixture.output)

    def test_deprecated_for_removal_with_group(self):
        self.conf.register_group(cfg.OptGroup('other'))
        self.conf.register_opt(cfg.StrOpt('foo',
                                          deprecated_for_removal=True),
                               group='other')
        self.conf.register_opt(cfg.StrOpt('bar',
                                          deprecated_for_removal=True),
                               group='other')
        paths = self.create_tempfiles([('test',
                                        '[other]\n' +
                                        'foo=bar\n')])
        self.conf(['--config-file', paths[0]])
        # Multiple references should be logged only once.
        self.assertEqual('bar', self.conf.other.foo)
        self.assertEqual('bar', self.conf.other.foo)
        # Options not set in the config should not be logged.
        self.assertIsNone(self.conf.other.bar)
        expected = ('Option "foo" from group "other" is deprecated for '
                    'removal.  Its value may be silently ignored in the '
                    'future.\n')
        self.assertEqual(self.log_prefix + expected, self.log_fixture.output)

    def test_deprecated_with_dest(self):
        self.conf.register_group(cfg.OptGroup('other'))
        self.conf.register_opt(cfg.StrOpt('foo-bar', deprecated_name='bar',
                                          dest='foo'),
                               group='other')
        content = 'bar=baz'
        paths = self.create_tempfiles([('test',
                                        '[other]\n' +
                                        content + '\n')])

        self.conf(['--config-file', paths[0]])
        self.assertEqual('baz', self.conf.other.foo)
        expected = (cfg._Namespace._deprecated_opt_message %
                    {'dep_option': 'bar',
                     'dep_group': 'other',
                     'option': 'foo-bar',
                     'group': 'other'} + '\n')
        self.assertEqual(self.log_prefix + expected, self.log_fixture.output)


class DeprecationWarningTestsNoOsloLog(DeprecationWarningTests):
    log_prefix = ''

    def setUp(self):
        super(DeprecationWarningTestsNoOsloLog, self).setUp()
        # NOTE(bnemec): For some reason if I apply this as a class decorator
        # it ends up applying to the parent class too and breaks those tests.
        self.useFixture(fixtures.MockPatchObject(cfg, 'oslo_log', None))
