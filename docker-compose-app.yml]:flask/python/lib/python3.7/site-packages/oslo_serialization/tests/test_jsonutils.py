# Copyright 2011 OpenStack Foundation.
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

import collections
import datetime
import functools
import io
import ipaddress
import itertools
import json
from unittest import mock
from xmlrpc import client as xmlrpclib

import netaddr
from oslo_i18n import fixture
from oslotest import base as test_base

from oslo_serialization import jsonutils


class ReprObject(object):
    def __repr__(self):
        return 'repr'


class JSONUtilsTestMixin(object):

    json_impl = None

    def setUp(self):
        super(JSONUtilsTestMixin, self).setUp()
        self.json_patcher = mock.patch.multiple(
            jsonutils, json=self.json_impl,
        )
        self.json_impl_mock = self.json_patcher.start()

    def tearDown(self):
        self.json_patcher.stop()
        super(JSONUtilsTestMixin, self).tearDown()

    def test_dumps(self):
        self.assertEqual('{"a": "b"}', jsonutils.dumps({'a': 'b'}))

    def test_dumps_default(self):
        args = [ReprObject()]
        convert = functools.partial(jsonutils.to_primitive, fallback=repr)
        self.assertEqual('["repr"]', jsonutils.dumps(args, default=convert))

    def test_dump_as_bytes(self):
        self.assertEqual(b'{"a": "b"}', jsonutils.dump_as_bytes({'a': 'b'}))

    def test_dumps_namedtuple(self):
        n = collections.namedtuple("foo", "bar baz")(1, 2)
        self.assertEqual('[1, 2]', jsonutils.dumps(n))

    def test_dump(self):
        expected = '{"a": "b"}'
        json_dict = {'a': 'b'}

        fp = io.StringIO()
        jsonutils.dump(json_dict, fp)

        self.assertEqual(expected, fp.getvalue())

    def test_dump_namedtuple(self):
        expected = '[1, 2]'
        json_dict = collections.namedtuple("foo", "bar baz")(1, 2)

        fp = io.StringIO()
        jsonutils.dump(json_dict, fp)

        self.assertEqual(expected, fp.getvalue())

    def test_loads(self):
        self.assertEqual({'a': 'b'}, jsonutils.loads('{"a": "b"}'))

    def test_loads_unicode(self):
        self.assertIsInstance(jsonutils.loads(b'"foo"'), str)
        self.assertIsInstance(jsonutils.loads(u'"foo"'), str)

        # 'test' in Ukrainian
        i18n_str_unicode = u'"\u0442\u0435\u0441\u0442"'
        self.assertIsInstance(jsonutils.loads(i18n_str_unicode), str)

        i18n_str = i18n_str_unicode.encode('utf-8')
        self.assertIsInstance(jsonutils.loads(i18n_str), str)

    def test_loads_with_kwargs(self):
        jsontext = u'{"foo": 3}'
        result = jsonutils.loads(jsontext, parse_int=lambda x: 5)
        self.assertEqual(5, result['foo'])

    def test_load(self):

        jsontext = u'{"a": "\u0442\u044d\u0441\u0442"}'
        expected = {u'a': u'\u0442\u044d\u0441\u0442'}

        for encoding in ('utf-8', 'cp1251'):
            fp = io.BytesIO(jsontext.encode(encoding))
            result = jsonutils.load(fp, encoding=encoding)
            self.assertEqual(expected, result)
            for key, val in result.items():
                self.assertIsInstance(key, str)
                self.assertIsInstance(val, str)

    def test_dumps_exception_value(self):
        self.assertIn(jsonutils.dumps({"a": ValueError("hello")}),
                      ['{"a": "ValueError(\'hello\',)"}',
                       '{"a": "ValueError(\'hello\')"}'])


class JSONUtilsTestJson(JSONUtilsTestMixin, test_base.BaseTestCase):
    json_impl = json


class ToPrimitiveTestCase(test_base.BaseTestCase):
    def setUp(self):
        super(ToPrimitiveTestCase, self).setUp()
        self.trans_fixture = self.useFixture(fixture.Translation())

    def test_bytes(self):
        self.assertEqual(jsonutils.to_primitive(b'abc'), 'abc')

    def test_list(self):
        self.assertEqual([1, 2, 3], jsonutils.to_primitive([1, 2, 3]))

    def test_empty_list(self):
        self.assertEqual([], jsonutils.to_primitive([]))

    def test_tuple(self):
        self.assertEqual([1, 2, 3], jsonutils.to_primitive((1, 2, 3)))

    def test_dict(self):
        self.assertEqual(dict(a=1, b=2, c=3),
                         jsonutils.to_primitive(dict(a=1, b=2, c=3)))

    def test_empty_dict(self):
        self.assertEqual({}, jsonutils.to_primitive({}))

    def test_datetime(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        self.assertEqual('1920-02-03T04:05:06.000007',
                         jsonutils.to_primitive(x))

    def test_datetime_preserve(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        self.assertEqual(x, jsonutils.to_primitive(x, convert_datetime=False))

    def test_DateTime(self):
        x = xmlrpclib.DateTime()
        x.decode("19710203T04:05:06")
        self.assertEqual('1971-02-03T04:05:06.000000',
                         jsonutils.to_primitive(x))

    def test_iter(self):
        class IterClass(object):
            def __init__(self):
                self.data = [1, 2, 3, 4, 5]
                self.index = 0

            def __iter__(self):
                return self

            def next(self):
                if self.index == len(self.data):
                    raise StopIteration
                self.index = self.index + 1
                return self.data[self.index - 1]
            __next__ = next

        x = IterClass()
        self.assertEqual([1, 2, 3, 4, 5], jsonutils.to_primitive(x))

    def test_iteritems(self):
        class IterItemsClass(object):
            def __init__(self):
                self.data = dict(a=1, b=2, c=3).items()
                self.index = 0

            def iteritems(self):
                return self.data

        x = IterItemsClass()
        p = jsonutils.to_primitive(x)
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, p)

    def test_iteritems_with_cycle(self):
        class IterItemsClass(object):
            def __init__(self):
                self.data = dict(a=1, b=2, c=3)
                self.index = 0

            def iteritems(self):
                return self.data.items()

        x = IterItemsClass()
        x2 = IterItemsClass()
        x.data['other'] = x2
        x2.data['other'] = x

        # If the cycle isn't caught, to_primitive() will eventually result in
        # an exception due to excessive recursion depth.
        jsonutils.to_primitive(x)

    def test_items(self):
        # Use items() when iteritems() is not available.
        class ItemsClass(object):
            def __init__(self):
                self.data = dict(a=1, b=2, c=3)

            def items(self):
                return self.data.items()

        x = ItemsClass()
        p = jsonutils.to_primitive(x)
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, p)

    def test_precedence_items_iteritems(self):
        class ItemsIterItemsClass(object):
            def items(self):
                return {'items': 'items'}

            def iteritems(self):
                return {'iteritems': 'iteritems'}

        x = ItemsIterItemsClass()
        p = jsonutils.to_primitive(x)
        # Prefer iteritems over items
        self.assertEqual({'iteritems': 'iteritems'}, p)

    def test_mapping(self):
        # Make sure collections.Mapping is converted to a dict
        # and not a list.
        class MappingClass(collections.Mapping):
            def __init__(self):
                self.data = dict(a=1, b=2, c=3)

            def __getitem__(self, val):
                return self.data[val]

            def __iter__(self):
                return iter(self.data)

            def __len__(self):
                return len(self.data)

        x = MappingClass()
        p = jsonutils.to_primitive(x)
        self.assertEqual({'a': 1, 'b': 2, 'c': 3}, p)

    @mock.patch('warnings.warn')
    def test_instance(self, warn_mock):
        class MysteryClass(object):
            a = 10

            def __init__(self):
                self.b = 1

        x = MysteryClass()
        self.assertEqual(dict(b=1),
                         jsonutils.to_primitive(x, convert_instances=True))

        self.assertEqual(x, jsonutils.to_primitive(x))
        warn_mock.assert_called_once()

    def test_typeerror(self):
        x = bytearray  # Class, not instance
        self.assertEqual(u"<class 'bytearray'>", jsonutils.to_primitive(x))

    def test_nasties(self):
        def foo():
            pass
        x = [datetime, foo, dir]
        ret = jsonutils.to_primitive(x)
        self.assertEqual(3, len(ret))
        self.assertTrue(ret[0].startswith(u"<module 'datetime' from ") or
                        ret[0].startswith(u"<module 'datetime' (built-in)"))
        self.assertTrue(ret[1].startswith(
            '<function ToPrimitiveTestCase.test_nasties.<locals>.foo at 0x'
        ))
        self.assertEqual('<built-in function dir>', ret[2])

    def test_depth(self):
        class LevelsGenerator(object):
            def __init__(self, levels):
                self._levels = levels

            def iteritems(self):
                if self._levels == 0:
                    return iter([])
                else:
                    return iter([(0, LevelsGenerator(self._levels - 1))])

        l4_obj = LevelsGenerator(4)

        json_l2 = {0: {0: None}}
        json_l3 = {0: {0: {0: None}}}
        json_l4 = {0: {0: {0: {0: None}}}}

        ret = jsonutils.to_primitive(l4_obj, max_depth=2)
        self.assertEqual(json_l2, ret)

        ret = jsonutils.to_primitive(l4_obj, max_depth=3)
        self.assertEqual(json_l3, ret)

        ret = jsonutils.to_primitive(l4_obj, max_depth=4)
        self.assertEqual(json_l4, ret)

    def test_ipaddr_using_netaddr(self):
        thing = {'ip_addr': netaddr.IPAddress('1.2.3.4')}
        ret = jsonutils.to_primitive(thing)
        self.assertEqual({'ip_addr': '1.2.3.4'}, ret)

    def test_ipaddr_using_ipaddress_v4(self):
        thing = {'ip_addr': ipaddress.ip_address(u'192.168.0.1')}
        ret = jsonutils.to_primitive(thing)
        self.assertEqual({'ip_addr': '192.168.0.1'}, ret)

    def test_ipaddr_using_ipaddress_v6(self):
        thing = {'ip_addr': ipaddress.ip_address(u'2001:db8::')}
        ret = jsonutils.to_primitive(thing)
        self.assertEqual({'ip_addr': '2001:db8::'}, ret)

    def test_ipnet_using_netaddr(self):
        thing = {'ip_net': netaddr.IPNetwork('1.2.3.0/24')}
        ret = jsonutils.to_primitive(thing)
        self.assertEqual({'ip_net': '1.2.3.0/24'}, ret)

    def test_message_with_param(self):
        msg = self.trans_fixture.lazy('A message with param: %s')
        msg = msg % 'test_domain'
        ret = jsonutils.to_primitive(msg)
        self.assertEqual(msg, ret)

    def test_message_with_named_param(self):
        msg = self.trans_fixture.lazy('A message with params: %(param)s')
        msg = msg % {'param': 'hello'}
        ret = jsonutils.to_primitive(msg)
        self.assertEqual(msg, ret)

    def test_fallback(self):
        obj = ReprObject()

        ret = jsonutils.to_primitive(obj)
        self.assertIs(obj, ret)

        ret = jsonutils.to_primitive(obj, fallback=repr)
        self.assertEqual('repr', ret)

    def test_fallback_list(self):
        obj = ReprObject()
        obj_list = [obj]

        ret = jsonutils.to_primitive(obj_list)
        self.assertEqual([obj], ret)

        ret = jsonutils.to_primitive(obj_list, fallback=repr)
        self.assertEqual(['repr'], ret)

    def test_fallback_itertools_count(self):
        obj = itertools.count(1)

        ret = jsonutils.to_primitive(obj)
        self.assertEqual(str(obj), ret)

        ret = jsonutils.to_primitive(obj, fallback=lambda _: 'itertools_count')
        self.assertEqual('itertools_count', ret)

    def test_fallback_nasty(self):
        obj = int
        ret = jsonutils.to_primitive(obj)
        self.assertEqual(str(obj), ret)

        def formatter(typeobj):
            return 'type:%s' % typeobj.__name__
        ret = jsonutils.to_primitive(obj, fallback=formatter)
        self.assertEqual("type:int", ret)

    def test_fallback_typeerror(self):
        class NotIterable(object):
            # __iter__ is not callable, cause a TypeError in to_primitive()
            __iter__ = None

        obj = NotIterable()

        ret = jsonutils.to_primitive(obj)
        self.assertEqual(str(obj), ret)

        ret = jsonutils.to_primitive(obj, fallback=lambda _: 'fallback')
        self.assertEqual('fallback', ret)

    def test_exception(self):
        self.assertIn(jsonutils.to_primitive(ValueError("an exception")),
                      ["ValueError('an exception',)",
                       "ValueError('an exception')"])
