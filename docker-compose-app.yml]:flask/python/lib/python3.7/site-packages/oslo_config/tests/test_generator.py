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

import io
import sys
import textwrap
from unittest import mock

import fixtures
from oslotest import base
import tempfile
import testscenarios

from oslo_config import cfg
from oslo_config import fixture as config_fixture
from oslo_config import generator
from oslo_config import types

import yaml


load_tests = testscenarios.load_tests_apply_scenarios


def custom_type(a):
    """Something that acts like a type, but isn't known"""
    return a


def build_formatter(output_file, **kwargs):
    conf = cfg.ConfigOpts()
    conf.register_opts(generator._generator_opts)
    for k, v in kwargs.items():
        conf.set_override(k, v)
    return generator._OptFormatter(conf, output_file=output_file)


class GeneratorTestCase(base.BaseTestCase):

    groups = {
        'group1': cfg.OptGroup(name='group1',
                               help='Lorem ipsum dolor sit amet, consectetur '
                                    'adipisicing elit, sed do eiusmod tempor '
                                    'incididunt ut labore et dolore magna '
                                    'aliqua. Ut enim ad minim veniam, quis '
                                    'nostrud exercitation ullamco laboris '
                                    'nisi ut aliquip ex ea commodo '
                                    'consequat. Duis aute irure dolor in.'),
        'group2': cfg.OptGroup(name='group2', title='Group 2'),
        'foo': cfg.OptGroup(name='foo', title='Foo Title', help='foo help'),
    }

    opts = {
        'foo': cfg.StrOpt('foo', help='foo option'),
        'bar': cfg.StrOpt('bar', help='bar option'),
        'foo-bar': cfg.StrOpt('foo-bar', help='foobar'),
        'no_help': cfg.StrOpt('no_help'),
        'long_help': cfg.StrOpt('long_help',
                                help='Lorem ipsum dolor sit amet, consectetur '
                                     'adipisicing elit, sed do eiusmod tempor '
                                     'incididunt ut labore et dolore magna '
                                     'aliqua. Ut enim ad minim veniam, quis '
                                     'nostrud exercitation ullamco laboris '
                                     'nisi ut aliquip ex ea commodo '
                                     'consequat. Duis aute irure dolor in '
                                     'reprehenderit in voluptate velit esse '
                                     'cillum dolore eu fugiat nulla '
                                     'pariatur. Excepteur sint occaecat '
                                     'cupidatat non proident, sunt in culpa '
                                     'qui officia deserunt mollit anim id est '
                                     'laborum.'),
        'long_help_pre': cfg.StrOpt('long_help_pre',
                                    help='This is a very long help text which '
                                         'is preformatted with line breaks. '
                                         'It should break when it is too long '
                                         'but also keep the specified line '
                                         'breaks. This makes it possible to '
                                         'create lists with items:\n'
                                         '\n'
                                         '* item 1\n'
                                         '* item 2\n'
                                         '\n'
                                         'and should increase the '
                                         'readability.'),
        'choices_opt': cfg.StrOpt('choices_opt',
                                  default='a',
                                  choices=(None, '', 'a', 'b', 'c'),
                                  help='a string with choices'),
        'deprecated_opt_without_deprecated_group': cfg.StrOpt(
            'bar', deprecated_name='foobar', help='deprecated'),
        'deprecated_for_removal_opt': cfg.StrOpt(
            'bar', deprecated_for_removal=True, help='deprecated for removal'),
        'deprecated_reason_opt': cfg.BoolOpt(
            'turn_off_stove',
            default=False,
            deprecated_for_removal=True,
            deprecated_reason='This was supposed to work but it really, '
                              'really did not. Always buy house insurance.',
            help='DEPRECATED: Turn off stove'),
        'deprecated_opt_with_deprecated_since': cfg.BoolOpt(
            'tune_in',
            deprecated_for_removal=True,
            deprecated_since='13.0'),
        'deprecated_opt_with_deprecated_group': cfg.StrOpt(
            'bar', deprecated_name='foobar', deprecated_group='group1',
            help='deprecated'),
        'opt_with_DeprecatedOpt': cfg.BoolOpt(
            'foo-bar',
            help='Opt with DeprecatedOpt',
            deprecated_opts=[cfg.DeprecatedOpt('foo-bar',
                                               group='deprecated')]),
        # Unknown Opt default must be a string
        'unknown_type': cfg.Opt('unknown_opt',
                                default='123',
                                help='unknown',
                                type=types.String(type_name='unknown type')),
        'str_opt': cfg.StrOpt('str_opt',
                              default='foo bar',
                              help='a string'),
        'str_opt_sample_default': cfg.StrOpt('str_opt',
                                             default='fooishbar',
                                             help='a string'),
        'str_opt_with_space': cfg.StrOpt('str_opt',
                                         default='  foo bar  ',
                                         help='a string with spaces'),
        'str_opt_multiline': cfg.StrOpt('str_opt',
                                        default='foo\nbar\nbaz',
                                        help='a string with newlines'),
        'bool_opt': cfg.BoolOpt('bool_opt',
                                default=False,
                                help='a boolean'),
        'int_opt': cfg.IntOpt('int_opt',
                              default=10,
                              min=1,
                              max=20,
                              help='an integer'),
        'int_opt_min_0': cfg.IntOpt('int_opt_min_0',
                                    default=10,
                                    min=0,
                                    max=20,
                                    help='an integer'),
        'int_opt_max_0': cfg.IntOpt('int_opt_max_0',
                                    default=-1,
                                    max=0,
                                    help='an integer'),
        'float_opt': cfg.FloatOpt('float_opt',
                                  default=0.1,
                                  help='a float'),
        'list_opt': cfg.ListOpt('list_opt',
                                default=['1', '2', '3'],
                                help='a list'),
        'list_opt_with_bounds': cfg.ListOpt('list_opt_with_bounds',
                                            default=['1', '2', '3'],
                                            help='a list',
                                            bounds=True),
        'list_opt_single': cfg.ListOpt('list_opt_single',
                                       default='1',
                                       help='a list'),
        'list_int_opt': cfg.ListOpt('list_int_opt',
                                    default=[1, 2, 3],
                                    help='a list'),
        'dict_opt': cfg.DictOpt('dict_opt',
                                default={'1': 'yes', '2': 'no'},
                                help='a dict'),
        'ip_opt': cfg.IPOpt('ip_opt',
                            default='127.0.0.1',
                            help='an ip address'),
        'port_opt': cfg.PortOpt('port_opt',
                                default=80,
                                help='a port'),
        'hostname_opt': cfg.HostnameOpt('hostname_opt',
                                        default='compute01.nova.site1',
                                        help='a hostname'),
        'uri_opt': cfg.URIOpt('uri_opt',
                              default='http://example.com',
                              help='a URI'),
        'multi_opt': cfg.MultiStrOpt('multi_opt',
                                     default=['1', '2', '3'],
                                     help='multiple strings'),
        'multi_opt_none': cfg.MultiStrOpt('multi_opt_none',
                                          help='multiple strings'),
        'multi_opt_empty': cfg.MultiStrOpt('multi_opt_empty',
                                           default=[],
                                           help='multiple strings'),
        'multi_opt_sample_default': cfg.MultiStrOpt('multi_opt',
                                                    default=['1', '2', '3'],
                                                    sample_default=['5', '6'],
                                                    help='multiple strings'),
        'string_type_with_bad_default': cfg.Opt('string_type_with_bad_default',
                                                help='string with bad default',
                                                default=4096),
        'native_str_type': cfg.Opt('native_str_type',
                                   help='native help',
                                   type=str),
        'native_int_type': cfg.Opt('native_int_type',
                                   help='native help',
                                   type=int),
        'native_float_type': cfg.Opt('native_float_type',
                                     help='native help',
                                     type=float),
        'custom_type': cfg.Opt('custom_type',
                               help='custom help',
                               type=custom_type),
        'custom_type_name': cfg.Opt('custom_opt_type',
                                    type=types.Integer(type_name='port'
                                                       ' number'),
                                    default=5511,
                                    help='this is a port'),
    }

    content_scenarios = [
        ('empty',
         dict(opts=[], expected='''[DEFAULT]
''')),
        ('single_namespace',
         dict(opts=[('test', [(None, [opts['foo']])])],
              expected='''[DEFAULT]

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('multiple_namespaces',
         dict(opts=[('test', [(None, [opts['foo']])]),
                    ('other', [(None, [opts['bar']])])],
              expected='''[DEFAULT]

#
# From other
#

# bar option (string value)
#bar = <None>

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('group',
         dict(opts=[('test', [(groups['group1'], [opts['foo']])])],
              expected='''[DEFAULT]


[group1]
# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in.

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('empty_group',
         dict(opts=[('test', [(groups['group1'], [])])],
              expected='''[DEFAULT]
''')),
        ('multiple_groups',
         dict(opts=[('test', [(groups['group1'], [opts['foo']]),
                              (groups['group2'], [opts['bar']])])],
              expected='''[DEFAULT]


[group1]
# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in.

#
# From test
#

# foo option (string value)
#foo = <None>


[group2]

#
# From test
#

# bar option (string value)
#bar = <None>
''')),
        ('group_in_multiple_namespaces',
         dict(opts=[('test', [(groups['group1'], [opts['foo']])]),
                    ('other', [(groups['group1'], [opts['bar']])])],
              expected='''[DEFAULT]


[group1]
# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in.

#
# From other
#

# bar option (string value)
#bar = <None>

#
# From test
#

# foo option (string value)
#foo = <None>
''')),
        ('hyphenated_name',
         dict(opts=[('test', [(None, [opts['foo-bar']])])],
              expected='''[DEFAULT]

#
# From test
#

# foobar (string value)
#foo_bar = <None>
''')),
        ('no_help',
         dict(opts=[('test', [(None, [opts['no_help']])])],
              log_warning=('"%s" is missing a help string', 'no_help'),
              expected='''[DEFAULT]

#
# From test
#

# (string value)
#no_help = <None>
''')),
        ('long_help',
         dict(opts=[('test', [(None, [opts['long_help']])])],
              expected='''[DEFAULT]

#
# From test
#

# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
# ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
# aliquip ex ea commodo consequat. Duis aute irure dolor in
# reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
# pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
# culpa qui officia deserunt mollit anim id est laborum. (string
# value)
#long_help = <None>
''')),
        ('long_help_wrap_at_40',
         dict(opts=[('test', [(None, [opts['long_help']])])],
              wrap_width=40,
              expected='''[DEFAULT]

#
# From test
#

# Lorem ipsum dolor sit amet,
# consectetur adipisicing elit, sed do
# eiusmod tempor incididunt ut labore et
# dolore magna aliqua. Ut enim ad minim
# veniam, quis nostrud exercitation
# ullamco laboris nisi ut aliquip ex ea
# commodo consequat. Duis aute irure
# dolor in reprehenderit in voluptate
# velit esse cillum dolore eu fugiat
# nulla pariatur. Excepteur sint
# occaecat cupidatat non proident, sunt
# in culpa qui officia deserunt mollit
# anim id est laborum. (string value)
#long_help = <None>
''')),
        ('long_help_no_wrapping',
         dict(opts=[('test', [(None, [opts['long_help']])])],
              wrap_width=0,
              expected='''[DEFAULT]

#
# From test
#

'''   # noqa
'# Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod '
'tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, '
'quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo '
'consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse '
'cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat '
'non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. '
'(string value)'
'''
#long_help = <None>
''')),
        ('long_help_with_preformatting',
         dict(opts=[('test', [(None, [opts['long_help_pre']])])],
              wrap_width=70,
              expected='''[DEFAULT]

#
# From test
#

# This is a very long help text which is preformatted with line
# breaks. It should break when it is too long but also keep the
# specified line breaks. This makes it possible to create lists with
# items:
#
# * item 1
# * item 2
#
# and should increase the readability. (string value)
#long_help_pre = <None>
''')),
        ('choices_opt',
         dict(opts=[('test', [(None, [opts['choices_opt']])])],
              expected="""[DEFAULT]

#
# From test
#

# a string with choices (string value)
# Possible values:
# <None> - <No description provided>
# '' - <No description provided>
# a - <No description provided>
# b - <No description provided>
# c - <No description provided>
#choices_opt = a
""")),
        ('deprecated opt without deprecated group',
         dict(opts=[('test',
                     [(groups['foo'],
                       [opts['deprecated_opt_without_deprecated_group']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# deprecated (string value)
# Deprecated group/name - [foo]/foobar
#bar = <None>
''')),
        ('deprecated_for_removal',
         dict(opts=[('test', [(groups['foo'],
                              [opts['deprecated_for_removal_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# DEPRECATED: deprecated for removal (string value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
#bar = <None>
''')),
        ('deprecated_reason',
         dict(opts=[('test', [(groups['foo'],
                              [opts['deprecated_reason_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# DEPRECATED: Turn off stove (boolean value)
# This option is deprecated for removal.
# Its value may be silently ignored in the future.
# Reason: This was supposed to work but it really, really did not.
# Always buy house insurance.
#turn_off_stove = false
''')),
        ('deprecated_opt_with_deprecated_group',
         dict(opts=[('test',
                     [(groups['foo'],
                       [opts['deprecated_opt_with_deprecated_group']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From test
#

# deprecated (string value)
# Deprecated group/name - [group1]/foobar
#bar = <None>
''')),
        ('unknown_type',
         dict(opts=[('test', [(None, [opts['unknown_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# unknown (unknown type)
#unknown_opt = 123
''')),
        ('str_opt',
         dict(opts=[('test', [(None, [opts['str_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string (string value)
#str_opt = foo bar
''')),
        ('str_opt_with_space',
         dict(opts=[('test', [(None, [opts['str_opt_with_space']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string with spaces (string value)
#str_opt = "  foo bar  "
''')),
        ('str_opt_multiline',
         dict(opts=[('test', [(None, [opts['str_opt_multiline']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string with newlines (string value)
#str_opt = foo
#    bar
#    baz
''')),
        ('bool_opt',
         dict(opts=[('test', [(None, [opts['bool_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a boolean (boolean value)
#bool_opt = false
''')),
        ('int_opt',
         dict(opts=[('test', [(None, [opts['int_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# an integer (integer value)
# Minimum value: 1
# Maximum value: 20
#int_opt = 10
''')),
        ('int_opt_min_0',
         dict(opts=[('test', [(None, [opts['int_opt_min_0']])])],
              expected='''[DEFAULT]

#
# From test
#

# an integer (integer value)
# Minimum value: 0
# Maximum value: 20
#int_opt_min_0 = 10
''')),
        ('int_opt_max_0',
         dict(opts=[('test', [(None, [opts['int_opt_max_0']])])],
              expected='''[DEFAULT]

#
# From test
#

# an integer (integer value)
# Maximum value: 0
#int_opt_max_0 = -1
''')),

        ('float_opt',
         dict(opts=[('test', [(None, [opts['float_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a float (floating point value)
#float_opt = 0.1
''')),
        ('list_opt',
         dict(opts=[('test', [(None, [opts['list_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a list (list value)
#list_opt = 1,2,3
''')),
        ('list_opt_with_bounds',
         dict(opts=[('test', [(None, [opts['list_opt_with_bounds']])])],
              expected='''[DEFAULT]

#
# From test
#

# a list (list value)
#list_opt_with_bounds = [1,2,3]
''')),
        ('list_opt_single',
         dict(opts=[('test', [(None, [opts['list_opt_single']])])],
              expected='''[DEFAULT]

#
# From test
#

# a list (list value)
#list_opt_single = 1
''')),
        ('list_int_opt',
         dict(opts=[('test', [(None, [opts['list_int_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a list (list value)
#list_int_opt = 1,2,3
''')),
        ('dict_opt',
         dict(opts=[('test', [(None, [opts['dict_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a dict (dict value)
#dict_opt = 1:yes,2:no
''')),
        ('ip_opt',
         dict(opts=[('test', [(None, [opts['ip_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# an ip address (IP address value)
#ip_opt = 127.0.0.1
''')),
        ('port_opt',
         dict(opts=[('test', [(None, [opts['port_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a port (port value)
# Minimum value: 0
# Maximum value: 65535
#port_opt = 80
''')),
        ('hostname_opt',
         dict(opts=[('test', [(None, [opts['hostname_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# a hostname (hostname value)
#hostname_opt = compute01.nova.site1
''')),
        ('multi_opt',
         dict(opts=[('test', [(None, [opts['multi_opt']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt = 1
#multi_opt = 2
#multi_opt = 3
''')),
        ('multi_opt_none',
         dict(opts=[('test', [(None, [opts['multi_opt_none']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt_none =
''')),
        ('multi_opt_empty',
         dict(opts=[('test', [(None, [opts['multi_opt_empty']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#multi_opt_empty =
''')),
        ('str_opt_sample_default',
         dict(opts=[('test', [(None, [opts['str_opt_sample_default']])])],
              expected='''[DEFAULT]

#
# From test
#

# a string (string value)
#str_opt = fooishbar
''')),
        ('native_str_type',
         dict(opts=[('test', [(None, [opts['native_str_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# native help (string value)
#native_str_type = <None>
''')),
        ('native_int_type',
         dict(opts=[('test', [(None, [opts['native_int_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# native help (integer value)
#native_int_type = <None>
''')),
        ('native_float_type',
         dict(opts=[('test', [(None, [opts['native_float_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# native help (floating point value)
#native_float_type = <None>
''')),
        ('multi_opt_sample_default',
         dict(opts=[('test', [(None, [opts['multi_opt_sample_default']])])],
              expected='''[DEFAULT]

#
# From test
#

# multiple strings (multi valued)
#
# This option has a sample default set, which means that
# its actual default value may vary from the one documented
# below.
#multi_opt = 5
#multi_opt = 6
''')),
        ('custom_type_name',
         dict(opts=[('test', [(None, [opts['custom_type_name']])])],
              expected='''[DEFAULT]

#
# From test
#

# this is a port (port number)
#custom_opt_type = 5511
''')),
        ('custom_type',
         dict(opts=[('test', [(None, [opts['custom_type']])])],
              expected='''[DEFAULT]

#
# From test
#

# custom help (unknown value)
#custom_type = <None>
''')),
        ('string_type_with_bad_default',
         dict(opts=[('test', [(None,
                               [opts['string_type_with_bad_default']])])],
              expected='''[DEFAULT]

#
# From test
#

# string with bad default (string value)
#string_type_with_bad_default = 4096
''')),
        ('str_opt_str_group',
         dict(opts=[('test', [('foo',
                               [opts['str_opt']]),
                              (groups['foo'],
                               [opts['int_opt']])]),
                    ('foo', [('foo',
                              [opts['bool_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From foo
#

# a boolean (boolean value)
#bool_opt = false

#
# From test
#

# a string (string value)
#str_opt = foo bar

#
# From test
#

# an integer (integer value)
# Minimum value: 1
# Maximum value: 20
#int_opt = 10
''')),
        ('opt_str_opt_group',
         dict(opts=[('test', [(groups['foo'],
                               [opts['int_opt']]),
                              ('foo',
                               [opts['str_opt']])]),
                    ('foo', [(groups['foo'],
                              [opts['bool_opt']])])],
              expected='''[DEFAULT]


[foo]
# foo help

#
# From foo
#

# a boolean (boolean value)
#bool_opt = false

#
# From test
#

# an integer (integer value)
# Minimum value: 1
# Maximum value: 20
#int_opt = 10

#
# From test
#

# a string (string value)
#str_opt = foo bar
''')),
        ('opt_with_DeprecatedOpt',
         dict(opts=[('test', [(None, [opts['opt_with_DeprecatedOpt']])])],
              expected='''[DEFAULT]

#
# From test
#

# Opt with DeprecatedOpt (boolean value)
# Deprecated group/name - [deprecated]/foo_bar
#foo_bar = <None>
''')),
    ]

    output_file_scenarios = [
        ('stdout',
         dict(stdout=True, output_file=None)),
        ('output_file',
         dict(output_file='sample.conf', stdout=False)),
    ]

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(
            cls.content_scenarios,
            cls.output_file_scenarios)

    def setUp(self):
        super(GeneratorTestCase, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.config_fixture = config_fixture.Config(self.conf)
        self.config = self.config_fixture.config
        self.useFixture(self.config_fixture)

        self.tempdir = self.useFixture(fixtures.TempDir())

    def _capture_stream(self, stream_name):
        self.useFixture(fixtures.MonkeyPatch("sys.%s" % stream_name,
                                             io.StringIO()))
        return getattr(sys, stream_name)

    def _capture_stdout(self):
        return self._capture_stream('stdout')

    @mock.patch.object(generator, '_get_raw_opts_loaders')
    @mock.patch.object(generator, 'LOG')
    def test_generate(self, mock_log, raw_opts_loader):
        generator.register_cli_opts(self.conf)

        namespaces = [i[0] for i in self.opts]
        self.config(namespace=namespaces)

        for group in self.groups.values():
            self.conf.register_group(group)

        wrap_width = getattr(self, 'wrap_width', None)
        if wrap_width is not None:
            self.config(wrap_width=wrap_width)

        if self.stdout:
            stdout = self._capture_stdout()
        else:
            output_file = self.tempdir.join(self.output_file)
            self.config(output_file=output_file)

        # We have a static data structure matching what should be
        # returned by _list_opts() but we're mocking out a lower level
        # function that needs to return a namespace and a callable to
        # return options from that namespace. We have to pass opts to
        # the lambda to cache a reference to the name because the list
        # comprehension changes the thing pointed to by the name each
        # time through the loop.
        raw_opts_loader.return_value = [
            (ns, lambda opts=opts: opts)
            for ns, opts in self.opts
        ]

        generator.generate(self.conf)

        if self.stdout:
            self.assertEqual(self.expected, stdout.getvalue())
        else:
            with open(output_file, 'r') as f:
                actual = f.read()
            self.assertEqual(self.expected, actual)

        log_warning = getattr(self, 'log_warning', None)
        if log_warning is not None:
            mock_log.warning.assert_called_once_with(*log_warning)
        else:
            self.assertFalse(mock_log.warning.called)


class GeneratorFileHandlingTestCase(base.BaseTestCase):

    def setUp(self):
        super(GeneratorFileHandlingTestCase, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.config_fixture = config_fixture.Config(self.conf)
        self.config = self.config_fixture.config

    @mock.patch.object(generator, '_get_groups')
    @mock.patch.object(generator, '_list_opts')
    def test_close_generated_file(self, a, b):
        generator.register_cli_opts(self.conf)
        self.config(output_file='somefile')

        m = mock.mock_open()
        m.close = mock.Mock()

        with mock.patch.object(generator, 'open', m, create=True):
            generator.generate(self.conf, output_file=None)

        m().close.assert_called_once()

    @mock.patch.object(generator, '_get_groups')
    @mock.patch.object(generator, '_list_opts')
    def test_not_close_external_file(self, a, b):
        generator.register_cli_opts(self.conf)
        self.config()

        m = mock.Mock()
        generator.generate(self.conf, output_file=m)

        m().close.assert_not_called()


class DriverOptionTestCase(base.BaseTestCase):

    def setUp(self):
        super(DriverOptionTestCase, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.config_fixture = config_fixture.Config(self.conf)
        self.config = self.config_fixture.config
        self.useFixture(self.config_fixture)

    @mock.patch.object(generator, '_get_driver_opts_loaders')
    @mock.patch.object(generator, '_get_raw_opts_loaders')
    @mock.patch.object(generator, 'LOG')
    def test_driver_option(self, mock_log, raw_opts_loader,
                           driver_opts_loader):
        group = cfg.OptGroup(
            name='test_group',
            title='Test Group',
            driver_option='foo',
        )
        regular_opts = [
            cfg.MultiStrOpt('foo', help='foo option'),
            cfg.StrOpt('bar', help='bar option'),
        ]
        driver_opts = {
            'd1': [
                cfg.StrOpt('d1-foo', help='foo option'),
            ],
            'd2': [
                cfg.StrOpt('d2-foo', help='foo option'),
            ],
        }

        # We have a static data structure matching what should be
        # returned by _list_opts() but we're mocking out a lower level
        # function that needs to return a namespace and a callable to
        # return options from that namespace. We have to pass opts to
        # the lambda to cache a reference to the name because the list
        # comprehension changes the thing pointed to by the name each
        # time through the loop.
        raw_opts_loader.return_value = [
            ('testing', lambda: [(group, regular_opts)]),
        ]
        driver_opts_loader.return_value = [
            ('testing', lambda: driver_opts),
        ]

        # Initialize the generator to produce YAML output to a buffer.
        generator.register_cli_opts(self.conf)
        self.config(namespace=['test_generator'], format_='yaml')
        stdout = io.StringIO()

        # Generate the output and parse it back to a data structure.
        generator.generate(self.conf, output_file=stdout)
        body = stdout.getvalue()
        actual = yaml.safe_load(body)

        test_section = actual['options']['test_group']

        self.assertEqual('foo', test_section['driver_option'])
        found_option_names = [
            o['name']
            for o in test_section['opts']
        ]
        self.assertEqual(
            ['foo', 'bar', 'd1-foo', 'd2-foo'],
            found_option_names
        )
        self.assertEqual(
            {'d1': ['d1-foo'], 'd2': ['d2-foo']},
            test_section['driver_opts'],
        )


GENERATOR_OPTS = {'format_': 'yaml',
                  'minimal': False,
                  'namespace': ['test'],
                  'output_file': None,
                  'summarize': False,
                  'wrap_width': 70,
                  'config_source': []}


class MachineReadableGeneratorTestCase(base.BaseTestCase):
    all_opts = GeneratorTestCase.opts
    all_groups = GeneratorTestCase.groups
    content_scenarios = [
        ('single_namespace',
         dict(opts=[('test', [(None, [all_opts['foo']])])],
              expected={'deprecated_options': {},
                        'generator_options': GENERATOR_OPTS,
                        'options': {
                            'DEFAULT': {
                                'driver_option': '',
                                'driver_opts': {},
                                'dynamic_group_owner': '',
                                'help': '',
                                'standard_opts': ['foo'],
                                'opts': [{'advanced': False,
                                          'choices': [],
                                          'default': None,
                                          'deprecated_for_removal': False,
                                          'deprecated_opts': [],
                                          'deprecated_reason': None,
                                          'deprecated_since': None,
                                          'dest': 'foo',
                                          'help': 'foo option',
                                          'max': None,
                                          'metavar': None,
                                          'min': None,
                                          'mutable': False,
                                          'name': 'foo',
                                          'namespace': 'test',
                                          'positional': False,
                                          'required': False,
                                          'sample_default': None,
                                          'secret': False,
                                          'short': None,
                                          'type': 'string value'}]}}})),
        ('long_help',
         dict(opts=[('test', [(None, [all_opts['long_help']])])],
              expected={'deprecated_options': {},
                        'generator_options': GENERATOR_OPTS,
                        'options': {
                            'DEFAULT': {
                                'driver_option': '',
                                'driver_opts': {},
                                'dynamic_group_owner': '',
                                'help': '',
                                'standard_opts': ['long_help'],
                                'opts': [{'advanced': False,
                                          'choices': [],
                                          'default': None,
                                          'deprecated_for_removal': False,
                                          'deprecated_opts': [],
                                          'deprecated_reason': None,
                                          'deprecated_since': None,
                                          'dest': 'long_help',
                                          'help': all_opts['long_help'].help,
                                          'max': None,
                                          'metavar': None,
                                          'min': None,
                                          'mutable': False,
                                          'name': 'long_help',
                                          'namespace': 'test',
                                          'positional': False,
                                          'required': False,
                                          'sample_default': None,
                                          'secret': False,
                                          'short': None,
                                          'type': 'string value'}]}}})),
        ('long_help_pre',
         dict(opts=[('test', [(None, [all_opts['long_help_pre']])])],
              expected={'deprecated_options': {},
                        'generator_options': GENERATOR_OPTS,
                        'options': {
                            'DEFAULT': {
                                'driver_option': '',
                                'driver_opts': {},
                                'dynamic_group_owner': '',
                                'help': '',
                                'standard_opts': ['long_help_pre'],
                                'opts': [{'advanced': False,
                                          'choices': [],
                                          'default': None,
                                          'deprecated_for_removal': False,
                                          'deprecated_opts': [],
                                          'deprecated_reason': None,
                                          'deprecated_since': None,
                                          'dest': 'long_help_pre',
                                          'help':
                                              all_opts['long_help_pre'].help,
                                          'max': None,
                                          'metavar': None,
                                          'min': None,
                                          'mutable': False,
                                          'name': 'long_help_pre',
                                          'namespace': 'test',
                                          'positional': False,
                                          'required': False,
                                          'sample_default': None,
                                          'secret': False,
                                          'short': None,
                                          'type': 'string value'}]}}})),
        ('opt_with_DeprecatedOpt',
         dict(opts=[('test', [(None, [all_opts['opt_with_DeprecatedOpt']])])],
              expected={
                  'deprecated_options': {
                      'deprecated': [{'name': 'foo_bar',
                                      'replacement_group': 'DEFAULT',
                                      'replacement_name': 'foo-bar'}]},
                  'generator_options': GENERATOR_OPTS,
                  'options': {
                      'DEFAULT': {
                          'driver_option': '',
                          'driver_opts': {},
                          'dynamic_group_owner': '',
                          'help': '',
                          'standard_opts': ['foo-bar'],
                          'opts': [{
                              'advanced': False,
                              'choices': [],
                              'default': None,
                              'deprecated_for_removal': False,
                              'deprecated_opts': [{'group': 'deprecated',
                                                   'name': 'foo_bar'}],
                              'deprecated_reason': None,
                              'deprecated_since': None,
                              'dest': 'foo_bar',
                              'help':
                                  all_opts['opt_with_DeprecatedOpt'].help,
                              'max': None,
                              'metavar': None,
                              'min': None,
                              'mutable': False,
                              'name': 'foo-bar',
                              'namespace': 'test',
                              'positional': False,
                              'required': False,
                              'sample_default': None,
                              'secret': False,
                              'short': None,
                              'type': 'boolean value'}]}}})),
        ('choices_opt',
         dict(opts=[('test', [(None, [all_opts['choices_opt']])])],
              expected={'deprecated_options': {},
                        'generator_options': GENERATOR_OPTS,
                        'options': {
                            'DEFAULT': {
                                'driver_option': '',
                                'driver_opts': {},
                                'dynamic_group_owner': '',
                                'help': '',
                                'standard_opts': ['choices_opt'],
                                'opts': [{'advanced': False,
                                          'choices': [
                                              (None, None),
                                              ('', None),
                                              ('a', None),
                                              ('b', None),
                                              ('c', None)
                                          ],
                                          'default': 'a',
                                          'deprecated_for_removal': False,
                                          'deprecated_opts': [],
                                          'deprecated_reason': None,
                                          'deprecated_since': None,
                                          'dest': 'choices_opt',
                                          'help': all_opts['choices_opt'].help,
                                          'max': None,
                                          'metavar': None,
                                          'min': None,
                                          'mutable': False,
                                          'name': 'choices_opt',
                                          'namespace': 'test',
                                          'positional': False,
                                          'required': False,
                                          'sample_default': None,
                                          'secret': False,
                                          'short': None,
                                          'type': 'string value'}]}}})),
        ('int_opt',
         dict(opts=[('test', [(None, [all_opts['int_opt']])])],
              expected={'deprecated_options': {},
                        'generator_options': GENERATOR_OPTS,
                        'options': {
                            'DEFAULT': {
                                'driver_option': '',
                                'driver_opts': {},
                                'dynamic_group_owner': '',
                                'help': '',
                                'standard_opts': ['int_opt'],
                                'opts': [{'advanced': False,
                                          'choices': [],
                                          'default': 10,
                                          'deprecated_for_removal': False,
                                          'deprecated_opts': [],
                                          'deprecated_reason': None,
                                          'deprecated_since': None,
                                          'dest': 'int_opt',
                                          'help': all_opts['int_opt'].help,
                                          'max': 20,
                                          'metavar': None,
                                          'min': 1,
                                          'mutable': False,
                                          'name': 'int_opt',
                                          'namespace': 'test',
                                          'positional': False,
                                          'required': False,
                                          'sample_default': None,
                                          'secret': False,
                                          'short': None,
                                          'type': 'integer value'}]}}})),
        ('group_help',
         dict(opts=[('test', [(all_groups['group1'], [all_opts['foo']])])],
              expected={'deprecated_options': {},
                        'generator_options': GENERATOR_OPTS,
                        'options': {
                            'DEFAULT': {
                                # 'driver_option': '',
                                # 'driver_opts': [],
                                # 'dynamic_group_owner': '',
                                'help': '',
                                'standard_opts': [],
                                'opts': []
                            },
                            'group1': {
                                'driver_option': '',
                                'driver_opts': {},
                                'dynamic_group_owner': '',
                                'help': all_groups['group1'].help,
                                'standard_opts': ['foo'],
                                'opts': [{'advanced': False,
                                          'choices': [],
                                          'default': None,
                                          'deprecated_for_removal': False,
                                          'deprecated_opts': [],
                                          'deprecated_reason': None,
                                          'deprecated_since': None,
                                          'dest': 'foo',
                                          'help': all_opts['foo'].help,
                                          'max': None,
                                          'metavar': None,
                                          'min': None,
                                          'mutable': False,
                                          'name': 'foo',
                                          'namespace': 'test',
                                          'positional': False,
                                          'required': False,
                                          'sample_default': None,
                                          'secret': False,
                                          'short': None,
                                          'type': 'string value'}]}}})),
        ]

    def setUp(self):
        super(MachineReadableGeneratorTestCase, self).setUp()

        self.conf = cfg.ConfigOpts()
        self.config_fixture = config_fixture.Config(self.conf)
        self.config = self.config_fixture.config
        self.useFixture(self.config_fixture)

    @classmethod
    def generate_scenarios(cls):
        cls.scenarios = testscenarios.multiply_scenarios(
            cls.content_scenarios)

    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_generate(self, raw_opts_loader):
        generator.register_cli_opts(self.conf)
        namespaces = [i[0] for i in self.opts]
        self.config(namespace=namespaces, format_='yaml')

        # We have a static data structure matching what should be
        # returned by _list_opts() but we're mocking out a lower level
        # function that needs to return a namespace and a callable to
        # return options from that namespace. We have to pass opts to
        # the lambda to cache a reference to the name because the list
        # comprehension changes the thing pointed to by the name each
        # time through the loop.
        raw_opts_loader.return_value = [
            (ns, lambda opts=opts: opts)
            for ns, opts in self.opts
        ]
        test_groups = generator._get_groups(
            generator._list_opts(self.conf.namespace))
        self.assertEqual(self.expected,
                         generator._generate_machine_readable_data(test_groups,
                                                                   self.conf))


class IgnoreDoublesTestCase(base.BaseTestCase):

    opts = [cfg.StrOpt('foo', help='foo option'),
            cfg.StrOpt('bar', help='bar option'),
            cfg.StrOpt('foo_bar', help='foobar'),
            cfg.StrOpt('str_opt', help='a string'),
            cfg.BoolOpt('bool_opt', help='a boolean'),
            cfg.IntOpt('int_opt', help='an integer')]

    def test_cleanup_opts_default(self):
        o = [("namespace1", [
              ("group1", self.opts)])]
        self.assertEqual(o, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_opt(self):
        o = [("namespace1", [
              ("group1", self.opts + [self.opts[0]])])]
        e = [("namespace1", [
              ("group1", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_groups_opt(self):
        o = [("namespace1", [
              ("group1", self.opts + [self.opts[1]]),
              ("group2", self.opts),
              ("group3", self.opts + [self.opts[2]])])]
        e = [("namespace1", [
              ("group1", self.opts),
              ("group2", self.opts),
              ("group3", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_mixed_case_groups_opt(self):
        o = [("namespace1", [
              ("default", self.opts),
              ("Default", self.opts + [self.opts[1]]),
              ("DEFAULT", self.opts + [self.opts[2]]),
              ("group1", self.opts + [self.opts[1]]),
              ("Group1", self.opts),
              ("GROUP1", self.opts + [self.opts[2]])])]
        e = [("namespace1", [
              ("DEFAULT", self.opts),
              ("group1", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    def test_cleanup_opts_dup_namespace_groups_opts(self):
        o = [("namespace1", [
              ("group1", self.opts + [self.opts[1]]),
              ("group2", self.opts)]),
             ("namespace2", [
              ("group1", self.opts + [self.opts[2]]),
              ("group2", self.opts)])]
        e = [("namespace1", [
              ("group1", self.opts),
              ("group2", self.opts)]),
             ("namespace2", [
              ("group1", self.opts),
              ("group2", self.opts)])]
        self.assertEqual(e, generator._cleanup_opts(o))

    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_list_ignores_doubles(self, raw_opts_loaders):
        config_opts = [
            (None, [cfg.StrOpt('foo'), cfg.StrOpt('bar')]),
        ]

        # These are the very same config options, but read twice.
        # This is possible if one misconfigures the entry point for the
        # sample config generator.
        raw_opts_loaders.return_value = [
            ('namespace', lambda: config_opts),
            ('namespace', lambda: config_opts),
        ]

        slurped_opts = 0
        for _, listing in generator._list_opts(['namespace']):
            for _, opts in listing:
                slurped_opts += len(opts)
        self.assertEqual(2, slurped_opts)


class GeneratorAdditionalTestCase(base.BaseTestCase):

    opts = [cfg.StrOpt('foo', help='foo option', default='fred'),
            cfg.StrOpt('bar', help='bar option'),
            cfg.StrOpt('foo_bar', help='foobar'),
            cfg.StrOpt('str_opt', help='a string'),
            cfg.BoolOpt('bool_opt', help='a boolean'),
            cfg.IntOpt('int_opt', help='an integer')]

    def test_get_groups_empty_ns(self):
        groups = generator._get_groups([])
        self.assertEqual({'DEFAULT': {'object': None, 'namespaces': []}},
                         groups)

    def test_get_groups_single_ns(self):
        config = [("namespace1", [
                   ("beta", self.opts),
                   ("alpha", self.opts)])]
        groups = generator._get_groups(config)
        self.assertEqual(['DEFAULT', 'alpha', 'beta'], sorted(groups))

    def test_get_groups_multiple_ns(self):
        config = [("namespace1", [
                   ("beta", self.opts),
                   ("alpha", self.opts)]),
                  ("namespace2", [
                   ("gamma", self.opts),
                   ("alpha", self.opts)])]
        groups = generator._get_groups(config)
        self.assertEqual(['DEFAULT', 'alpha', 'beta', 'gamma'], sorted(groups))

    def test_output_opts_empty_default(self):

        config = [("namespace1", [
                   ("alpha", [])])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = build_formatter(f)
            generator._output_opts(formatter, 'DEFAULT', groups.pop('DEFAULT'))
        expected = '''[DEFAULT]
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)

    def test_output_opts_group(self):

        config = [("namespace1", [
                   ("alpha", [self.opts[0]])])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = build_formatter(f)
            generator._output_opts(formatter, 'alpha', groups.pop('alpha'))
        expected = '''[alpha]

#
# From namespace1
#

# foo option (string value)
#foo = fred
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)

    def _test_output_default_list_opt_with_string_value(self, default):
        opt = cfg.ListOpt('list_opt', help='a list', default=default)
        config = [("namespace1", [
                   ("alpha", [opt])])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        f = open(tmp_file, 'w+')
        formatter = build_formatter(f)
        expected = '''[alpha]

#
# From namespace1
#

# a list (list value)
#list_opt = %(default)s
''' % {'default': default}
        generator._output_opts(formatter, 'alpha', groups.pop('alpha'))
        f.close()
        content = open(tmp_file).read()
        self.assertEqual(expected, content)

    def test_output_default_list_opt_with_string_value_multiple_entries(self):
        self._test_output_default_list_opt_with_string_value('foo,bar')

    def test_output_default_list_opt_with_string_value_single_entry(self):
        self._test_output_default_list_opt_with_string_value('foo')


class GeneratorMutableOptionTestCase(base.BaseTestCase):

    def test_include_message(self):
        out = io.StringIO()
        opt = cfg.StrOpt('foo', help='foo option', mutable=True)
        gen = build_formatter(out)
        gen.format(opt, 'group1')
        result = out.getvalue()
        self.assertIn(
            'This option can be changed without restarting.',
            result,
        )

    def test_do_not_include_message(self):
        out = io.StringIO()
        opt = cfg.StrOpt('foo', help='foo option', mutable=False)
        gen = build_formatter(out)
        gen.format(opt, 'group1')
        result = out.getvalue()
        self.assertNotIn(
            'This option can be changed without restarting.',
            result,
        )


class GeneratorRaiseErrorTestCase(base.BaseTestCase):

    def test_generator_raises_error(self):
        """Verifies that errors from extension manager are not suppressed."""
        class FakeException(Exception):
            pass

        class FakeEP(object):

            def __init__(self):
                self.name = 'callback_is_expected'
                self.require = self.resolve
                self.load = self.resolve

            def resolve(self, *args, **kwargs):
                raise FakeException()

        fake_ep = FakeEP()
        self.conf = cfg.ConfigOpts()
        self.conf.register_opts(generator._generator_opts)
        self.conf.set_default('namespace', [fake_ep.name])
        with mock.patch('stevedore.named.NamedExtensionManager',
                        side_effect=FakeException()):
            self.assertRaises(FakeException, generator.generate, self.conf)

    def test_generator_call_with_no_arguments_raises_system_exit(self):
        testargs = ['oslo-config-generator']
        with mock.patch('sys.argv', testargs):
            self.assertRaises(SystemExit, generator.main, [])


class ChangeDefaultsTestCase(base.BaseTestCase):

    @mock.patch.object(generator, '_get_opt_default_updaters')
    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_no_modifiers_registered(self, raw_opts_loaders, get_updaters):
        orig_opt = cfg.StrOpt('foo', default='bar')
        raw_opts_loaders.return_value = [
            ('namespace', lambda: [(None, [orig_opt])]),
        ]
        get_updaters.return_value = []

        opts = generator._list_opts(['namespace'])
        # NOTE(dhellmann): Who designed this data structure?
        the_opt = opts[0][1][0][1][0]

        self.assertEqual('bar', the_opt.default)
        self.assertIs(orig_opt, the_opt)

    @mock.patch.object(generator, '_get_opt_default_updaters')
    @mock.patch.object(generator, '_get_raw_opts_loaders')
    def test_change_default(self, raw_opts_loaders, get_updaters):
        orig_opt = cfg.StrOpt('foo', default='bar')
        raw_opts_loaders.return_value = [
            ('namespace', lambda: [(None, [orig_opt])]),
        ]

        def updater():
            cfg.set_defaults([orig_opt], foo='blah')

        get_updaters.return_value = [updater]

        opts = generator._list_opts(['namespace'])
        # NOTE(dhellmann): Who designed this data structure?
        the_opt = opts[0][1][0][1][0]

        self.assertEqual('blah', the_opt.default)
        self.assertIs(orig_opt, the_opt)


class RequiredOptionTestCase(base.BaseTestCase):

    opts = [cfg.StrOpt('foo', help='foo option', default='fred'),
            cfg.StrOpt('bar', help='bar option', required=True),
            cfg.StrOpt('foo_bar', help='foobar'),
            cfg.StrOpt('bars', help='bars foo', required=True)]

    def test_required_option_order_single_ns(self):

        config = [("namespace1", [
                   ("alpha", self.opts)])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = build_formatter(f, minimal=True)
            generator._output_opts(formatter,
                                   'alpha',
                                   groups.pop('alpha'))
        expected = '''[alpha]

#
# From namespace1
#

# bar option (string value)
bar = <None>

# bars foo (string value)
bars = <None>
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)


class SummarizedOptionsTestCase(base.BaseTestCase):
    """Validate 'summarize' config option.

    The 'summarize' switch ensures only summaries of each configuration
    option are output.
    """

    opts = [
        cfg.StrOpt(
            'foo',
            default='fred',
            help="""This is the summary line for a config option.

I can provide a lot more detail here, but I may not want to bloat my
config file. In this scenario, I can use the 'summarize' config option
to ensure only a summary of the option is output to the config file.
However, the Sphinx-generated documentation, hosted online, remains
unchanged.

Hopefully this works.
"""),
        cfg.StrOpt(
            'bar',
            required=True,
            help="""This is a less carefully formatted configuration
option, where the author has not broken their description into a brief
summary line and larger description. Watch this person's commit
messages!""")]

    def test_summarized_option_order_single_ns(self):

        config = [('namespace1', [('alpha', self.opts)])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = build_formatter(f, summarize=True)
            generator._output_opts(formatter,
                                   'alpha',
                                   groups.pop('alpha'))
        expected = '''[alpha]

#
# From namespace1
#

# This is the summary line for a config option. For more information,
# refer to the documentation. (string value)
#foo = fred

# This is a less carefully formatted configuration
# option, where the author has not broken their description into a
# brief
# summary line and larger description. Watch this person's commit
# messages! (string value)
#bar = <None>
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)


class AdvancedOptionsTestCase(base.BaseTestCase):

    opts = [cfg.StrOpt('foo', help='foo option', default='fred'),
            cfg.StrOpt('bar', help='bar option', advanced=True),
            cfg.StrOpt('foo_bar', help='foobar'),
            cfg.BoolOpt('bars', help='bars foo', default=True, advanced=True)]

    def test_advanced_option_order_single_ns(self):

        config = [("namespace1", [
                   ("alpha", self.opts)])]
        groups = generator._get_groups(config)

        fd, tmp_file = tempfile.mkstemp()
        with open(tmp_file, 'w+') as f:
            formatter = build_formatter(f)
            generator._output_opts(formatter, 'alpha', groups.pop('alpha'))
        expected = '''[alpha]

#
# From namespace1
#

# foo option (string value)
#foo = fred

# foobar (string value)
#foo_bar = <None>

# bar option (string value)
# Advanced Option: intended for advanced users and not used
# by the majority of users, and might have a significant
# effect on stability and/or performance.
#bar = <None>

# bars foo (boolean value)
# Advanced Option: intended for advanced users and not used
# by the majority of users, and might have a significant
# effect on stability and/or performance.
#bars = true
'''
        with open(tmp_file, 'r') as f:
            actual = f.read()
        self.assertEqual(expected, actual)


class HostAddressTestCase(base.BaseTestCase):

    opts = [cfg.HostAddressOpt('foo', help='foo option', default='0.0.0.0')]

    def test_host_address(self):

        config = [("namespace", [("alpha", self.opts)])]
        groups = generator._get_groups(config)

        out = io.StringIO()
        formatter = build_formatter(out)
        generator._output_opts(formatter, 'alpha', groups.pop('alpha'))
        result = out.getvalue()

        expected = textwrap.dedent('''
        [alpha]

        #
        # From namespace
        #

        # foo option (host address value)
        #foo = 0.0.0.0
        ''').lstrip()
        self.assertEqual(expected, result)


GeneratorTestCase.generate_scenarios()
MachineReadableGeneratorTestCase.generate_scenarios()
