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

import textwrap
from unittest import mock

from oslotest import base

from oslo_config import cfg
from oslo_config import sphinxext


class FormatGroupTest(base.BaseTestCase):

    def test_none_in_default(self):
        # option with None group placed in DEFAULT
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           help='this appears in the default group'),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``

          this appears in the default group
        ''').lstrip(), results)

    def test_with_default_value(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           default='this is the default',
                           help='this appears in the default group'),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``this is the default``

          this appears in the default group
        ''').lstrip(), results)

    def test_with_min(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.IntOpt('opt_name',
                           min=1),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: integer
          :Default: ``<None>``
          :Minimum Value: 1
        ''').lstrip(), results)

    def test_with_min_0(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.IntOpt('opt_name',
                           min=0),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: integer
          :Default: ``<None>``
          :Minimum Value: 0
        ''').lstrip(), results)

    def test_with_max(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.IntOpt('opt_name',
                           max=1),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: integer
          :Default: ``<None>``
          :Maximum Value: 1
        ''').lstrip(), results)

    def test_with_max_0(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.IntOpt('opt_name',
                           max=0),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: integer
          :Default: ``<None>``
          :Maximum Value: 0
        ''').lstrip(), results)

    def test_with_choices(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           choices=['a', 'b', 'c', None, '']),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``
          :Valid Values: a, b, c, <None>, ''
        ''').lstrip(), results)

    def test_with_choices_with_descriptions(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt(
                    'opt_name',
                    choices=[
                        ('a', 'a is the best'),
                        ('b', 'Actually, may-b I am better'),
                        ('c', 'c, I am clearly the greatest'),
                        (None, 'I am having none of this'),
                        ('', '')]),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``
          :Valid Values: a, b, c, <None>, ''

          .. rubric:: Possible values

          a
            a is the best

          b
            Actually, may-b I am better

          c
            c, I am clearly the greatest

          <None>
            I am having none of this

          ''
            <No description provided>
        ''').lstrip(), results)

    def test_group_obj_without_help(self):
        # option with None group placed in DEFAULT
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name='group',
            group_obj=cfg.OptGroup('group'),
            opt_list=[cfg.StrOpt('opt_name')],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: group

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``
        ''').lstrip(), results)

    def test_group_obj_with_help(self):
        # option with None group placed in DEFAULT
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name='group',
            group_obj=cfg.OptGroup('group', help='group help'),
            opt_list=[cfg.StrOpt('opt_name')],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: group

          group help

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``
        ''').lstrip(), results)

    def test_deprecated_opts_without_deprecated_group(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           deprecated_name='deprecated_name',
                           )
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``

          .. list-table:: Deprecated Variations
             :header-rows: 1

             - * Group
               * Name
             - * DEFAULT
               * deprecated_name
        ''').lstrip(), results)

    def test_deprecated_opts_with_deprecated_group(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           deprecated_name='deprecated_name',
                           deprecated_group='deprecated_group',
                           )
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``

          .. list-table:: Deprecated Variations
             :header-rows: 1

             - * Group
               * Name
             - * deprecated_group
               * deprecated_name
        ''').lstrip(), results)

    def test_deprecated_for_removal(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           deprecated_for_removal=True,
                           deprecated_reason='because I said so',
                           deprecated_since='13.0',
                           )
            ],
        )))
        self.assertIn('.. warning::', results)
        self.assertIn('because I said so', results)
        self.assertIn('since 13.0', results)

    def test_mutable(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.IntOpt('opt_name',
                           mutable=True),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: integer
          :Default: ``<None>``
          :Mutable: This option can be changed without restarting.
        ''').lstrip(), results)

    def test_not_mutable(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.IntOpt('opt_name',
                           mutable=False),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: integer
          :Default: ``<None>``
        ''').lstrip(), results)

    def test_advanced(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           advanced=True),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``
          :Advanced Option: Intended for advanced users and not used
              by the majority of users, and might have a significant
              effect on stability and/or performance.
        ''').lstrip(), results)

    def test_not_advanced(self):
        results = '\n'.join(list(sphinxext._format_group_opts(
            namespace=None,
            group_name=None,
            group_obj=None,
            opt_list=[
                cfg.StrOpt('opt_name',
                           advanced=False),
            ],
        )))
        self.assertEqual(textwrap.dedent('''
        .. oslo.config:group:: DEFAULT

        .. oslo.config:option:: opt_name

          :Type: string
          :Default: ``<None>``
        ''').lstrip(), results)


class FormatOptionHelpTest(base.BaseTestCase):

    @mock.patch('oslo_config.generator._list_opts')
    @mock.patch('oslo_config.sphinxext._format_group_opts')
    def test_split_namespaces(self, _format_group_opts, _list_opts):
        _list_opts.return_value = [
            ('namespace1', [(None, ['opt1'])]),
            ('namespace2', [(None, ['opt2'])]),
        ]
        list(sphinxext._format_option_help(
            namespaces=['namespace1', 'namespace2'],
            split_namespaces=True))
        _format_group_opts.assert_any_call(
            namespace='namespace1',
            group_name='DEFAULT',
            group_obj=None,
            opt_list=['opt1'],
        )
        _format_group_opts.assert_any_call(
            namespace='namespace2',
            group_name='DEFAULT',
            group_obj=None,
            opt_list=['opt2'],
        )

    @mock.patch('oslo_config.generator._list_opts')
    @mock.patch('oslo_config.sphinxext._format_group_opts')
    def test_dont_split_namespaces(self, _format_group_opts, _list_opts):
        _list_opts.return_value = [
            ('namespace1', [(None, ['opt1'])]),
            ('namespace2', [(None, ['opt2'])]),
        ]
        list(sphinxext._format_option_help(
            namespaces=['namespace1', 'namespace2'],
            split_namespaces=False))
        _format_group_opts.assert_called_once_with(
            namespace=None,
            group_name='DEFAULT',
            group_obj=None,
            opt_list=['opt1', 'opt2'],
        )

    @mock.patch('oslo_config.generator._list_opts')
    @mock.patch('oslo_config.sphinxext._format_group_opts')
    def test_dont_split_namespaces_with_group(self, _format_group_opts,
                                              _list_opts):
        grp_obj = cfg.OptGroup('grp1')
        _list_opts.return_value = [
            ('namespace1', [(grp_obj, ['opt1'])]),
            ('namespace2', [('grp1', ['opt2'])]),
        ]
        list(sphinxext._format_option_help(
            namespaces=['namespace1', 'namespace2'],
            split_namespaces=False))
        _format_group_opts.assert_any_call(
            namespace=None,
            group_name='grp1',
            group_obj=grp_obj,
            opt_list=['opt1', 'opt2'],
        )

    @mock.patch('oslo_config.generator._list_opts')
    @mock.patch('oslo_config.sphinxext._format_group_opts')
    def test_split_namespaces_with_group(self, _format_group_opts,
                                         _list_opts):
        grp_obj = cfg.OptGroup('grp1')
        _list_opts.return_value = [
            ('namespace1', [(grp_obj, ['opt1'])]),
            ('namespace2', [('grp1', ['opt2'])]),
        ]
        list(sphinxext._format_option_help(
            namespaces=['namespace1', 'namespace2'],
            split_namespaces=True))
        print(_format_group_opts.call_args_list)
        _format_group_opts.assert_any_call(
            namespace='namespace1',
            group_name='grp1',
            group_obj=grp_obj,
            opt_list=['opt1'],
        )
        _format_group_opts.assert_any_call(
            namespace='namespace2',
            group_name='grp1',
            group_obj=None,
            opt_list=['opt2'],
        )
