import pytest
from flask import current_app as app

from pcapi.celery_tasks.tasks import RateLimitedError
from pcapi.celery_tasks.tasks import get_key
from pcapi.celery_tasks.tasks import rate_limit
from pcapi.utils import date as date_utils


class GetKeyTest:
    @pytest.mark.parametrize("time_window_size", [60, 30])
    def test_generated_key(self, time_window_size):
        result = get_key("my_awesome_task", time_window_size)
        time_window_size_id = int(date_utils.get_naive_utc_now().timestamp()) // time_window_size

        assert result == f"pcapi:celery:bucket:my_awesome_task:{time_window_size}:{time_window_size_id}"


class RateLimitTest:
    @pytest.mark.parametrize("time_window_size,max_per_time_window", [(60, 5), (30, 12)])
    def test_rate_limit_no_key(self, time_window_size, max_per_time_window):
        name = "my_awesome_task"
        key = get_key(name, time_window_size)
        executed = False

        with rate_limit(name, time_window_size, max_per_time_window):
            executed = True

        assert executed
        assert int(app.redis_client.get(key)) == 1
        assert app.redis_client.ttl(key) == 2 * time_window_size

    def test_rate_limit_key_exists(self):
        name = "my_awesome_task"
        time_window_size = 60
        max_per_time_window = 1000
        key = get_key(name, time_window_size)
        app.redis_client.set(key, 42)
        app.redis_client.expire(key, 80)

        executed = False

        with rate_limit(name, time_window_size, max_per_time_window):
            executed = True

        assert executed
        assert int(app.redis_client.get(key)) == 43
        assert app.redis_client.ttl(key) == 80

    def test_rate_limit_above_limit(self):
        name = "my_awesome_task"
        time_window_size = 60
        max_per_time_window = 10
        key = get_key(name, time_window_size)
        app.redis_client.set(key, 42)
        app.redis_client.expire(key, 80)

        with pytest.raises(RateLimitedError):
            with rate_limit(name, time_window_size, max_per_time_window):
                assert False

        assert int(app.redis_client.get(key)) == 43
        assert app.redis_client.ttl(key) == 80
