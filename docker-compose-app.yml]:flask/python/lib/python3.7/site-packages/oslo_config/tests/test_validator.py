# Copyright 2019 Red Hat, Inc.
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

from unittest import mock

from oslotest import base

from oslo_config import cfg
from oslo_config import fixture
from oslo_config import validator


OPT_DATA = {'options': {'foo': {'opts': [{'name': 'opt'}]},
                        'bar': {'opts': [{'name': 'opt'}]},
                        },
            'deprecated_options': {'bar': [{'name': 'opt'}]}}
VALID_CONF = """
[foo]
opt = value
"""
DEPRECATED_CONF = """
[bar]
opt = value
"""
INVALID_CONF = """
[foo]
opts = value
"""
MISSING_GROUP_CONF = """
[oo]
opt = value
"""


class TestValidator(base.BaseTestCase):
    def setUp(self):
        super(TestValidator, self).setUp()
        self.conf = cfg.ConfigOpts()
        self.conf_fixture = self.useFixture(fixture.Config(self.conf))
        validator._register_cli_opts(self.conf)

    @mock.patch('oslo_config.validator.load_opt_data')
    def test_passing(self, mock_lod):
        mock_lod.return_value = OPT_DATA
        self.conf_fixture.config(opt_data='mocked.yaml',
                                 input_file='mocked.conf')
        m = mock.mock_open(read_data=VALID_CONF)
        with mock.patch('builtins.open', m):
            self.assertEqual(0, validator._validate(self.conf))

    @mock.patch('oslo_config.validator.load_opt_data')
    def test_deprecated(self, mock_lod):
        mock_lod.return_value = OPT_DATA
        self.conf_fixture.config(opt_data='mocked.yaml',
                                 input_file='mocked.conf')
        m = mock.mock_open(read_data=DEPRECATED_CONF)
        with mock.patch('builtins.open', m):
            self.assertEqual(0, validator._validate(self.conf))

    @mock.patch('oslo_config.validator.load_opt_data')
    def test_deprecated_fatal_warnings(self, mock_lod):
        mock_lod.return_value = OPT_DATA
        self.conf_fixture.config(opt_data='mocked.yaml',
                                 input_file='mocked.conf',
                                 fatal_warnings=True)
        m = mock.mock_open(read_data=DEPRECATED_CONF)
        with mock.patch('builtins.open', m):
            self.assertEqual(1, validator._validate(self.conf))

    @mock.patch('oslo_config.validator.load_opt_data')
    def test_missing(self, mock_lod):
        mock_lod.return_value = OPT_DATA
        self.conf_fixture.config(opt_data='mocked.yaml',
                                 input_file='mocked.conf')
        m = mock.mock_open(read_data=INVALID_CONF)
        with mock.patch('builtins.open', m):
            self.assertEqual(1, validator._validate(self.conf))

    @mock.patch('oslo_config.validator.load_opt_data')
    def test_missing_group(self, mock_lod):
        mock_lod.return_value = OPT_DATA
        self.conf_fixture.config(opt_data='mocked.yaml',
                                 input_file='mocked.conf')
        m = mock.mock_open(read_data=MISSING_GROUP_CONF)
        with mock.patch('builtins.open', m):
            self.assertEqual(1, validator._validate(self.conf))

    @mock.patch('oslo_config.validator.load_opt_data')
    def test_exclude_groups(self, mock_lod):
        mock_lod.return_value = OPT_DATA
        self.conf_fixture.config(opt_data='mocked.yaml',
                                 input_file='mocked.conf',
                                 exclude_group=['oo'])
        m = mock.mock_open(read_data=MISSING_GROUP_CONF)
        with mock.patch('builtins.open', m):
            self.assertEqual(0, validator._validate(self.conf))

    def test_invalid_options(self):
        self.assertRaises(RuntimeError, validator._validate, self.conf)
