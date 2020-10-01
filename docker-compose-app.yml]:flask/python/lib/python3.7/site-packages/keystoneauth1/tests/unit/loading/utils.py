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

import functools
from unittest import mock
import uuid


from keystoneauth1 import loading
from keystoneauth1.loading import base
from keystoneauth1 import plugin
from keystoneauth1.tests.unit import utils


class TestCase(utils.TestCase):

    GROUP = 'auth'
    V2PASS = 'v2password'
    V3TOKEN = 'v3token'

    a_int = 88
    a_float = 88.8
    a_bool = False

    TEST_VALS = {'a_int': a_int,
                 'a_float': a_float,
                 'a_bool': a_bool}

    def assertTestVals(self, plugin, vals=TEST_VALS):
        for k, v in vals.items():
            self.assertEqual(v, plugin[k])


def create_plugin(opts=[], token=None, endpoint=None):

    class Plugin(plugin.BaseAuthPlugin):

        def __init__(self, **kwargs):
            self._data = kwargs

        def __getitem__(self, key):
            return self._data[key]

        def get_token(self, *args, **kwargs):
            return token

        def get_endpoint(self, *args, **kwargs):
            return endpoint

    class Loader(loading.BaseLoader):

        @property
        def plugin_class(self):
            return Plugin

        def get_options(self):
            return opts

    return Plugin, Loader


class BoolType(object):

    def __eq__(self, other):
        """Define equiality for many bool types."""
        # hack around oslo.config equality comparison
        return type(self) == type(other)

    # NOTE: This function is only needed by Python 2. If we get to point where
    # we don't support Python 2 anymore, this function should be removed.
    def __ne__(self, other):
        """Define inequiality for many bool types."""
        return not self.__eq__(other)

    def __call__(self, value):
        return str(value).lower() in ('1', 'true', 't', 'yes', 'y')


INT_DESC = 'test int'
FLOAT_DESC = 'test float'
BOOL_DESC = 'test bool'
STR_DESC = 'test str'
STR_DEFAULT = uuid.uuid4().hex


MockPlugin, MockLoader = create_plugin(
    endpoint='http://test',
    token='aToken',
    opts=[
        loading.Opt('a-int', default=3, type=int, help=INT_DESC),
        loading.Opt('a-bool', type=BoolType(), help=BOOL_DESC),
        loading.Opt('a-float', type=float, help=FLOAT_DESC),
        loading.Opt('a-str', help=STR_DESC, default=STR_DEFAULT),
    ]
)


class MockManager(object):

    def __init__(self, driver):
        self.driver = driver


def mock_plugin(loader=MockLoader):
    def _wrapper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            with mock.patch.object(base, 'get_plugin_loader') as m:
                m.return_value = loader()
                args = list(args) + [m]
                return f(*args, **kwargs)

        return inner
    return _wrapper
