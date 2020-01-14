import os
from unittest.mock import patch, MagicMock

import redis

from connectors.redis import add_to_redis, get_offer_ids, delete_offer_ids


class RedisTest:
    @staticmethod
    def test_api_writes_value_in_redis():
        # Given
        key_to_insert = 'foo'
        value_to_insert = 'bar'
        redis_url = os.environ.get('REDIS_URL')
        redis_connection = redis.from_url(redis_url)

        # When
        redis_connection.set(key_to_insert, value_to_insert)

        # Then
        assert str(redis_connection.get(key_to_insert), 'utf-8') == value_to_insert


class AddToRedisTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_add_offer_id_to_redis_set_when_feature_flipping_is_enable(self, mock_redis, mock_redis_list, mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_to_redis(client=client, offer_id=1)

        # Then
        client.rpush.assert_called_once_with(mock_redis_list, 1)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_not_add_offer_id_to_redis_set_when_feature_flipping_is_disable(self, mock_redis, mock_redis_list, mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_to_redis(client=client, offer_id=1)

        # Then
        client.rpush.assert_not_called()


@patch('connectors.redis.REDIS_LRANGE_END', return_value=500)
@patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
@patch('connectors.redis.redis')
def test_should_return_offer_ids_from_redis(mock_redis, mock_redis_list, mock_redis_lrange_end):
    # Given
    client = MagicMock()
    client.lrange = MagicMock()

    # When
    get_offer_ids(client=client)

    # Then
    client.lrange.assert_called_once_with(mock_redis_list, 0, mock_redis_lrange_end)


@patch('connectors.redis.REDIS_LRANGE_END', return_value=500)
@patch('connectors.redis.REDIS_LIST_OFFER_IDS', return_value='fake_list_offer_ids')
@patch('connectors.redis.redis')
def test_should_delete_given_range_of_offer_ids_from_redis_list(mock_redis, mock_redis_list, mock_redis_lrange_end):
    # Given
    client = MagicMock()
    client.ltrim = MagicMock()

    # When
    delete_offer_ids(client=client)

    # Then
    client.ltrim.assert_called_once_with(mock_redis_list, mock_redis_lrange_end, -1)
