#    Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
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

import datetime
import itertools
from xmlrpc import client as xmlrpclib

import netaddr
from oslotest import base as test_base
from pytz import timezone

from oslo_serialization import msgpackutils
from oslo_utils import uuidutils


_TZ_FMT = '%Y-%m-%d %H:%M:%S %Z%z'


class Color(object):
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


class ColorHandler(object):
    handles = (Color,)
    identity = (
        msgpackutils.HandlerRegistry.non_reserved_extension_range.min_value + 1
    )

    @staticmethod
    def serialize(obj):
        blob = '%s, %s, %s' % (obj.r, obj.g, obj.b)
        blob = blob.encode('ascii')
        return blob

    @staticmethod
    def deserialize(data):
        chunks = [int(c.strip()) for c in data.split(b",")]
        return Color(chunks[0], chunks[1], chunks[2])


class MySpecialSetHandler(object):
    handles = (set,)
    identity = msgpackutils.SetHandler.identity


def _dumps_loads(obj):
    obj = msgpackutils.dumps(obj)
    return msgpackutils.loads(obj)


class MsgPackUtilsTest(test_base.BaseTestCase):
    def test_list(self):
        self.assertEqual([1, 2, 3], _dumps_loads([1, 2, 3]))

    def test_empty_list(self):
        self.assertEqual([], _dumps_loads([]))

    def test_tuple(self):
        # Seems like we do lose whether it was a tuple or not...
        #
        # Maybe fixed someday:
        #
        # https://github.com/msgpack/msgpack-python/issues/98
        self.assertEqual([1, 2, 3], _dumps_loads((1, 2, 3)))

    def test_dict(self):
        self.assertEqual(dict(a=1, b=2, c=3),
                         _dumps_loads(dict(a=1, b=2, c=3)))

    def test_empty_dict(self):
        self.assertEqual({}, _dumps_loads({}))

    def test_complex_dict(self):
        src = {
            'now': datetime.datetime(1920, 2, 3, 4, 5, 6, 7),
            'later': datetime.datetime(1921, 2, 3, 4, 5, 6, 9),
            'a': 1,
            'b': 2.0,
            'c': [],
            'd': set([1, 2, 3]),
            'zzz': uuidutils.generate_uuid(),
            'yyy': 'yyy',
            'ddd': b'bbb',
            'today': datetime.date.today(),
        }
        self.assertEqual(src, _dumps_loads(src))

    def test_itercount(self):
        it = itertools.count(1)
        next(it)
        next(it)
        it2 = _dumps_loads(it)
        self.assertEqual(next(it), next(it2))

        it = itertools.count(0)
        it2 = _dumps_loads(it)
        self.assertEqual(next(it), next(it2))

    def test_itercount_step(self):
        it = itertools.count(1, 3)
        it2 = _dumps_loads(it)
        self.assertEqual(next(it), next(it2))

    def test_set(self):
        self.assertEqual(set([1, 2]), _dumps_loads(set([1, 2])))

    def test_empty_set(self):
        self.assertEqual(set([]), _dumps_loads(set([])))

    def test_frozenset(self):
        self.assertEqual(frozenset([1, 2]), _dumps_loads(frozenset([1, 2])))

    def test_empty_frozenset(self):
        self.assertEqual(frozenset([]), _dumps_loads(frozenset([])))

    def test_datetime_preserve(self):
        x = datetime.datetime(1920, 2, 3, 4, 5, 6, 7)
        self.assertEqual(x, _dumps_loads(x))

    def test_datetime(self):
        x = xmlrpclib.DateTime()
        x.decode("19710203T04:05:06")
        self.assertEqual(x, _dumps_loads(x))

    def test_ipaddr(self):
        thing = {'ip_addr': netaddr.IPAddress('1.2.3.4')}
        self.assertEqual(thing, _dumps_loads(thing))

    def test_today(self):
        today = datetime.date.today()
        self.assertEqual(today, _dumps_loads(today))

    def test_datetime_tz_clone(self):
        eastern = timezone('US/Eastern')
        now = datetime.datetime.now()
        e_dt = eastern.localize(now)
        e_dt2 = _dumps_loads(e_dt)
        self.assertEqual(e_dt, e_dt2)
        self.assertEqual(e_dt.strftime(_TZ_FMT), e_dt2.strftime(_TZ_FMT))

    def test_datetime_tz_different(self):
        eastern = timezone('US/Eastern')
        pacific = timezone('US/Pacific')
        now = datetime.datetime.now()

        e_dt = eastern.localize(now)
        p_dt = pacific.localize(now)

        self.assertNotEqual(e_dt, p_dt)
        self.assertNotEqual(e_dt.strftime(_TZ_FMT), p_dt.strftime(_TZ_FMT))

        e_dt2 = _dumps_loads(e_dt)
        p_dt2 = _dumps_loads(p_dt)

        self.assertNotEqual(e_dt2, p_dt2)
        self.assertNotEqual(e_dt2.strftime(_TZ_FMT), p_dt2.strftime(_TZ_FMT))

        self.assertEqual(e_dt, e_dt2)
        self.assertEqual(p_dt, p_dt2)

    def test_copy_then_register(self):
        registry = msgpackutils.default_registry
        self.assertRaises(ValueError,
                          registry.register, MySpecialSetHandler(),
                          reserved=True, override=True)
        registry = registry.copy(unfreeze=True)
        registry.register(MySpecialSetHandler(),
                          reserved=True, override=True)
        h = registry.match(set())
        self.assertIsInstance(h, MySpecialSetHandler)

    def test_bad_register(self):
        registry = msgpackutils.default_registry
        self.assertRaises(ValueError,
                          registry.register, MySpecialSetHandler(),
                          reserved=True, override=True)
        self.assertRaises(ValueError,
                          registry.register, MySpecialSetHandler())
        registry = registry.copy(unfreeze=True)
        registry.register(ColorHandler())

        self.assertRaises(ValueError,
                          registry.register, ColorHandler())

    def test_custom_register(self):
        registry = msgpackutils.default_registry.copy(unfreeze=True)
        registry.register(ColorHandler())

        c = Color(255, 254, 253)
        c_b = msgpackutils.dumps(c, registry=registry)
        c = msgpackutils.loads(c_b, registry=registry)

        self.assertEqual(255, c.r)
        self.assertEqual(254, c.g)
        self.assertEqual(253, c.b)

    def test_object(self):
        self.assertRaises(ValueError, msgpackutils.dumps, object())
