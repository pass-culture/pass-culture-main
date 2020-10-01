# Copyright 2012, Red Hat, Inc.
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

import threading
from unittest import mock
import warnings

import eventlet
from eventlet import greenthread
from oslotest import base as test_base
import six

from oslo_utils import eventletutils


class EventletUtilsTest(test_base.BaseTestCase):
    def setUp(self):
        super(EventletUtilsTest, self).setUp()
        self._old_avail = eventletutils.EVENTLET_AVAILABLE
        eventletutils.EVENTLET_AVAILABLE = True

    def tearDown(self):
        super(EventletUtilsTest, self).tearDown()
        eventletutils.EVENTLET_AVAILABLE = self._old_avail

    @mock.patch("oslo_utils.eventletutils._patcher")
    def test_warning_not_patched(self, mock_patcher):
        mock_patcher.already_patched = True
        mock_patcher.is_monkey_patched.return_value = False
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['os'])
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(RuntimeWarning, w.category)
        self.assertIn('os', six.text_type(w.message))

    @mock.patch("oslo_utils.eventletutils._patcher")
    def test_warning_not_patched_none_provided(self, mock_patcher):
        mock_patcher.already_patched = True
        mock_patcher.is_monkey_patched.return_value = False
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(RuntimeWarning, w.category)
        for m in eventletutils._ALL_PATCH:
            self.assertIn(m, six.text_type(w.message))

    @mock.patch("oslo_utils.eventletutils._patcher")
    def test_warning_not_patched_all(self, mock_patcher):
        mock_patcher.already_patched = True
        mock_patcher.is_monkey_patched.return_value = False
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['all'])
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(RuntimeWarning, w.category)
        for m in eventletutils._ALL_PATCH:
            self.assertIn(m, six.text_type(w.message))

    @mock.patch("oslo_utils.eventletutils._patcher")
    def test_no_warning(self, mock_patcher):
        mock_patcher.already_patched = True
        mock_patcher.is_monkey_patched.return_value = True
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['os'])
        self.assertEqual(0, len(capture))

    @mock.patch("oslo_utils.eventletutils._patcher")
    def test_eventlet_is_patched(self, mock_patcher):
        mock_patcher.is_monkey_patched.return_value = True
        self.assertTrue(eventletutils.is_monkey_patched('os'))
        mock_patcher.is_monkey_patched.return_value = False
        self.assertFalse(eventletutils.is_monkey_patched('os'))

    @mock.patch("oslo_utils.eventletutils._patcher", None)
    def test_eventlet_no_patcher(self):
        self.assertFalse(eventletutils.is_monkey_patched('os'))

    @mock.patch("oslo_utils.eventletutils._patcher")
    def test_partially_patched_warning(self, mock_patcher):
        is_patched = set()
        mock_patcher.already_patched = True
        mock_patcher.is_monkey_patched.side_effect = lambda m: m in is_patched
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['os'])
        self.assertEqual(1, len(capture))
        is_patched.add('os')
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['os'])
        self.assertEqual(0, len(capture))
        is_patched.add('thread')
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['os', 'thread'])
        self.assertEqual(0, len(capture))
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            eventletutils.warn_eventlet_not_patched(['all'])
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(RuntimeWarning, w.category)
        for m in ['os', 'thread']:
            self.assertNotIn(m, six.text_type(w.message))

    def test_invalid_patch_check(self):
        self.assertRaises(ValueError,
                          eventletutils.warn_eventlet_not_patched,
                          ['blah.blah'])

    @mock.patch('oslo_utils.eventletutils._eventlet')
    def test_event_api_compat(self, mock_eventlet):
        with mock.patch('oslo_utils.eventletutils.is_monkey_patched',
                        return_value=True):
            e_event = eventletutils.Event()
        self.assertIsInstance(e_event, eventletutils.EventletEvent)

        t_event = eventletutils.Event()
        if six.PY3:
            t_event_cls = threading.Event
        else:
            t_event_cls = threading._Event
        self.assertIsInstance(t_event, t_event_cls)

        public_methods = [m for m in dir(t_event) if not m.startswith("_") and
                          callable(getattr(t_event, m))]

        for method in public_methods:
            self.assertTrue(hasattr(e_event, method))

        # Ensure set() allows multiple invocations, same as in
        # threading implementation.
        e_event.set()
        self.assertTrue(e_event.isSet())
        e_event.set()
        self.assertTrue(e_event.isSet())

    def test_event_no_timeout(self):
        event = eventletutils.EventletEvent()

        def thread_a():
            self.assertTrue(event.wait())

        a = greenthread.spawn(thread_a)

        with eventlet.timeout.Timeout(0.5, False):
            a.wait()
            self.fail('wait() timed out')

    def test_event_race(self):
        event = eventletutils.EventletEvent()

        def thread_a():
            self.assertTrue(event.wait(2))

        a = greenthread.spawn(thread_a)

        def thread_b():
            eventlet.sleep(0.1)
            event.clear()
            event.set()
            a.wait()

        b = greenthread.spawn(thread_b)
        with eventlet.timeout.Timeout(0.5):
            b.wait()

    def test_event_clear_timeout(self):
        event = eventletutils.EventletEvent()

        def thread_a():
            self.assertFalse(event.wait(0.5))

        a = greenthread.spawn(thread_a)

        def thread_b():
            eventlet.sleep(0.1)
            event.clear()
            eventlet.sleep(0.1)
            event.clear()
            a.wait()

        b = greenthread.spawn(thread_b)
        with eventlet.timeout.Timeout(0.7):
            b.wait()

    def test_event_set_clear_timeout(self):
        event = eventletutils.EventletEvent()
        wakes = []

        def thread_func():
            result = event.wait(0.2)
            wakes.append(result)
            if len(wakes) == 1:
                self.assertTrue(result)
                event.clear()
            else:
                self.assertFalse(result)

        a = greenthread.spawn(thread_func)
        b = greenthread.spawn(thread_func)
        eventlet.sleep(0)  # start threads
        event.set()

        with eventlet.timeout.Timeout(0.3):
            a.wait()
            b.wait()
        self.assertFalse(event.is_set())
        self.assertEqual([True, False], wakes)

    @mock.patch('oslo_utils.eventletutils._eventlet.event.Event')
    def test_event_clear_already_sent(self, mock_event):
        old_event = mock.Mock()
        new_event = mock.Mock()
        mock_event.side_effect = [old_event, new_event]
        event = eventletutils.EventletEvent()
        event.set()
        event.clear()
        self.assertEqual(1, old_event.send.call_count)
