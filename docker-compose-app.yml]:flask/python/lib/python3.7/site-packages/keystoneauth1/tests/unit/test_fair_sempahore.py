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

from threading import Thread
from timeit import default_timer as timer
from unittest import mock

from six.moves import queue
import testtools

from keystoneauth1 import _fair_semaphore


class SemaphoreTests(testtools.TestCase):

    def _thread_worker(self):
        while True:
            # get returns the Item, but we don't care about the value so we
            # purposely don't assign it to anything.
            self.q.get()
            with self.s:
                self.mock_payload.do_something()
            self.q.task_done()

    # Have 5 threads do 10 different "things" coordinated by the fair
    # semaphore.
    def _concurrency_core(self, concurrency, delay):
        self.s = _fair_semaphore.FairSemaphore(concurrency, delay)

        self.q = queue.Queue()
        for i in range(5):
            t = Thread(target=self._thread_worker)
            t.daemon = True
            t.start()

        for item in range(0, 10):
            self.q.put(item)

        self.q.join()

    def setUp(self):
        super(SemaphoreTests, self).setUp()
        self.mock_payload = mock.Mock()

    # We should be waiting at least 0.1s between operations, so
    # the 10 operations must take at *least* 1 second
    def test_semaphore_no_concurrency(self):
        start = timer()
        self._concurrency_core(None, 0.1)
        end = timer()
        self.assertTrue((end - start) > 1.0)
        self.assertEqual(self.mock_payload.do_something.call_count, 10)

    def test_semaphore_single_concurrency(self):
        start = timer()
        self._concurrency_core(1, 0.1)
        end = timer()
        self.assertTrue((end - start) > 1.0)
        self.assertEqual(self.mock_payload.do_something.call_count, 10)

    def test_semaphore_multiple_concurrency(self):
        start = timer()
        self._concurrency_core(5, 0.1)
        end = timer()
        self.assertTrue((end - start) > 1.0)
        self.assertEqual(self.mock_payload.do_something.call_count, 10)

    # do some high speed tests; I don't think we can really assert
    # much about these other than they don't deadlock...
    def test_semaphore_fast_no_concurrency(self):
        self._concurrency_core(None, 0.0)

    def test_semaphore_fast_single_concurrency(self):
        self._concurrency_core(1, 0.0)

    def test_semaphore_fast_multiple_concurrency(self):
        self._concurrency_core(5, 0.0)
