import os
from unittest.mock import patch, MagicMock

import redis

from connectors.redis import add_to_redis, get_offer_ids, delete_offer_ids


class RedisTest:
    def test_api_writes_value_in_redis(self):
        # Given
        key_to_insert = 'foo'
        value_to_insert = 'bar'
        redis_url = os.environ.get('REDIS_URL')
        redis_connection = redis.from_url(redis_url)

        # When
        redis_connection.set(key_to_insert, value_to_insert)

        # Then
        assert str(redis_connection.get(key_to_insert), 'utf-8') == value_to_insert


@patch('connectors.redis.REDIS_HOST', return_value='fake_redis_host')
@patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
@patch('connectors.redis.redis')
def test_should_add_offer_id_to_redis_set(mock_redis, mock_redis_list, mock_redis_host):
    # Given
    client = MagicMock()
    mock_redis.Redis = MagicMock(return_value=client)
    client.rpush = MagicMock()

    # When
    add_to_redis(1)

    # Then
    mock_redis.Redis.assert_called_once_with(host=mock_redis_host)
    client.rpush.assert_called_once_with(mock_redis_list, 1)


@patch('connectors.redis.REDIS_HOST', return_value='fake_redis_host')
@patch('connectors.redis.REDIS_LRANGE_END', return_value=500)
@patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
@patch('connectors.redis.redis')
def test_should_return_offer_ids_from_redis(mock_redis, mock_redis_list, mock_redis_lrange_end, mock_redis_host):
    # Given
    client = MagicMock()
    mock_redis.Redis = MagicMock(return_value=client)
    client.lrange = MagicMock()

    # When
    get_offer_ids()

    # Then
    mock_redis.Redis.assert_called_once_with(host=mock_redis_host, decode_responses=True)
    client.lrange.assert_called_once_with(mock_redis_list, 0, mock_redis_lrange_end)


@patch('connectors.redis.REDIS_HOST', return_value='fake_redis_host')
@patch('connectors.redis.REDIS_LRANGE_END', return_value=500)
@patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
@patch('connectors.redis.redis')
def test_should_delete_given_range_of_offer_ids_from_redis_list(mock_redis, mock_redis_list, mock_redis_lrange_end,
                                                                mock_redis_host):
    # Given
    client = MagicMock()
    mock_redis.Redis = MagicMock(return_value=client)
    client.ltrim = MagicMock()

    # When
    delete_offer_ids()

    # Then
    mock_redis.Redis.assert_called_once_with(host=mock_redis_host)
    client.ltrim.assert_called_once_with(mock_redis_list, mock_redis_lrange_end, -1)

