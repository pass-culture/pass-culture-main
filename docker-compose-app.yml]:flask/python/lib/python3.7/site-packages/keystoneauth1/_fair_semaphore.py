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

import threading
import time


from six.moves import queue


class FairSemaphore(object):
    """Semaphore class that notifies in order of request.

    We cannot use a normal Semaphore because it doesn't give any ordering,
    which could lead to a request starving. Instead, handle them in the
    order we receive them.

    :param int concurrency:
        How many concurrent threads can have the semaphore at once.
    :param float rate_delay:
        How long to wait between the start of each thread receiving the
        semaphore.
    """

    def __init__(self, concurrency, rate_delay):
        self._lock = threading.Lock()
        self._concurrency = concurrency
        if concurrency:
            self._count = 0
            self._queue = queue.Queue()

        self._rate_delay = rate_delay
        self._rate_last_ts = time.time()

    def __enter__(self):
        """Aquire a semaphore."""
        # If concurrency is None, everyone is free to immediately execute.
        if not self._concurrency:
            # NOTE: Rate limiting still applies.This will ultimately impact
            # concurrency a bit due to the mutex.
            with self._lock:
                execution_time = self._advance_timer()
        else:
            execution_time = self._get_ticket()
        return self._wait_for_execution(execution_time)

    def _wait_for_execution(self, execution_time):
        """Wait until the pre-calculated time to run."""
        wait_time = execution_time - time.time()
        if wait_time > 0:
            time.sleep(wait_time)

    def _get_ticket(self):
        ticket = threading.Event()
        with self._lock:
            if self._count <= self._concurrency:
                # We can execute, no need to wait. Take a ticket and
                # move on.
                self._count += 1
                return self._advance_timer()
            else:
                # We need to wait for a ticket before we can execute.
                # Put ourselves in the ticket queue to be woken up
                # when available.
                self._queue.put(ticket)
        ticket.wait()
        with self._lock:
            return self._advance_timer()

    def _advance_timer(self):
        """Calculate the time when it's ok to run a command again.

        This runs inside of the mutex, serializing the calculation
        of when it's ok to run again and setting _rate_last_ts to that
        new time so that the next thread to calculate when it's safe to
        run starts from the time that the current thread calculated.
        """
        self._rate_last_ts = self._rate_last_ts + self._rate_delay
        return self._rate_last_ts

    def __exit__(self, exc_type, exc_value, traceback):
        """Release the semaphore."""
        # If concurrency is None, everyone is free to immediately execute
        if not self._concurrency:
            return
        with self._lock:
            # If waiters, wake up the next item in the queue (note
            # we're under the queue lock so the queue won't change
            # under us).
            if self._queue.qsize() > 0:
                ticket = self._queue.get()
                ticket.set()
            else:
                # Nothing else to do, give our ticket back
                self._count -= 1
