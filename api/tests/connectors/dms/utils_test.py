import time

from pcapi.connectors.dms.utils import lock_ds_application


class LockTest:
    def test_lock_ds_application(self):
        step = 0
        start_time = time.time()
        with lock_ds_application(123):
            step += 1
        with lock_ds_application(123):
            step += 1
        end_time = time.time()
        assert step == 2
        assert end_time - start_time < 10
