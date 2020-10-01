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

import uuid

from testtools import matchers

from keystoneauth1 import exceptions
from keystoneauth1 import loading
from keystoneauth1.tests.unit.loading import utils


class PluginA(object):

    def __init__(self, a):
        self.val = a


class PluginB(object):

    def __init__(self, b):
        self.val = b


class TestSplitLoader(loading.BaseLoader):

    def get_options(self):
        opts = super(TestSplitLoader, self).get_options()
        opts += [loading.Opt('a'), loading.Opt('b')]
        return opts

    def create_plugin(self, a=None, b=None, **kwargs):
        if a:
            return PluginA(a)
        if b:
            return PluginB(b)

        raise AssertionError('Expected A or B')


class LoadingTests(utils.TestCase):

    def test_required_values(self):
        opts = [loading.Opt('a', required=False),
                loading.Opt('b', required=True)]

        Plugin, Loader = utils.create_plugin(opts=opts)

        lo = Loader()
        v = uuid.uuid4().hex

        p1 = lo.load_from_options(b=v)
        self.assertEqual(v, p1['b'])

        e = self.assertRaises(exceptions.MissingRequiredOptions,
                              lo.load_from_options,
                              a=v)

        self.assertEqual(1, len(e.options))

        for o in e.options:
            self.assertIsInstance(o, loading.Opt)

        self.assertEqual('b', e.options[0].name)

    def test_loaders(self):
        loaders = loading.get_available_plugin_loaders()
        self.assertThat(len(loaders), matchers.GreaterThan(0))

        for loader in loaders.values():
            self.assertIsInstance(loader, loading.BaseLoader)

    def test_loading_getter(self):

        called_opts = []

        vals = {'a-int': 44,
                'a-bool': False,
                'a-float': 99.99,
                'a-str': 'value'}

        val = uuid.uuid4().hex

        def _getter(opt):
            called_opts.append(opt.name)
            # return str because oslo.config should convert them back
            return str(vals[opt.name])

        p = utils.MockLoader().load_from_options_getter(_getter, other=val)

        self.assertEqual(set(vals), set(called_opts))

        for k, v in vals.items():
            # replace - to _ because it's the dest used to create kwargs
            self.assertEqual(v, p[k.replace('-', '_')])

        # check that additional kwargs get passed through
        self.assertEqual(val, p['other'])

    def test_loading_getter_with_kwargs(self):
        called_opts = set()

        vals = {'a-bool': False,
                'a-float': 99.99}

        def _getter(opt):
            called_opts.add(opt.name)
            # return str because oslo.config should convert them back
            return str(vals[opt.name])

        p = utils.MockLoader().load_from_options_getter(_getter,
                                                        a_int=66,
                                                        a_str='another')

        # only the options not passed by kwargs should get passed to getter
        self.assertEqual(set(('a-bool', 'a-float')), called_opts)

        self.assertFalse(p['a_bool'])
        self.assertEqual(99.99, p['a_float'])
        self.assertEqual('another', p['a_str'])
        self.assertEqual(66, p['a_int'])

    def test_create_plugin_loader(self):
        val_a = uuid.uuid4().hex
        val_b = uuid.uuid4().hex

        loader = TestSplitLoader()

        plugin_a = loader.load_from_options(a=val_a)
        plugin_b = loader.load_from_options(b=val_b)

        self.assertIsInstance(plugin_a, PluginA)
        self.assertIsInstance(plugin_b, PluginB)

        self.assertEqual(val_a, plugin_a.val)
        self.assertEqual(val_b, plugin_b.val)
