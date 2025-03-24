import pytest

from pcapi.utils import lock as lock_utils


class LockTest:
    def test_lock(self):
        step = 0
        with lock_utils.lock("test_lock", ttl=5, timeout=0):
            step += 1
        with lock_utils.lock("test_lock", ttl=5, timeout=0):
            step += 1
        assert step == 2

    def test_lock_already_acquired(self):
        with lock_utils.lock("test_lock_already_acquired", ttl=5, timeout=0):
            with pytest.raises(lock_utils.LockError) as error:
                with lock_utils.lock("test_lock_already_acquired", ttl=5, timeout=0):
                    pass
        assert str(error.value) == "Failed to acquire lock: test_lock_already_acquired"

    def test_lock_timeout(self):
        with lock_utils.lock("test_lock_timeout", ttl=1, timeout=2):
            with lock_utils.lock("test_lock_timeout", ttl=5, timeout=3):
                pass
