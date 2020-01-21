import os
from unittest.mock import patch, MagicMock

import redis

from connectors.redis import add_offer_id, get_offer_ids, delete_offer_ids, add_venue_id, \
    get_venue_ids, delete_venue_ids, add_venue_provider, get_venue_providers, \
    delete_venue_providers
from models import PcObject
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_provider, create_venue, create_user, create_offerer, \
    create_user_offerer, create_provider


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


class HandleOfferIdsTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', return_value='fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_add_offer_id_to_redis_when_algolia_feature_is_enabled(self,
                                                                           mock_redis,
                                                                           mock_redis_list,
                                                                           mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_offer_id(client=client, offer_id=1)

        # Then
        client.rpush.assert_called_once_with(mock_redis_list, 1)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', return_value='fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_not_add_offer_id_to_redis_when_algolia_feature_is_disabled(self,
                                                                                mock_redis,
                                                                                mock_redis_list,
                                                                                mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_offer_id(client=client, offer_id=1)

        # Then
        client.rpush.assert_not_called()

    @patch('connectors.redis.REDIS_OFFER_IDS_CHUNK_SIZE', return_value=1000)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', return_value='fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_return_offer_ids_from_redis(self, mock_redis, mock_redis_list, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()

        # When
        get_offer_ids(client=client)

        # Then
        client.lrange.assert_called_once_with(mock_redis_list, 0, mock_redis_lrange_end)

    @patch('connectors.redis.REDIS_OFFER_IDS_CHUNK_SIZE', return_value=500)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', return_value='fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_delete_given_range_of_offer_ids_from_redis(self,
                                                                    mock_redis,
                                                                    mock_redis_list,
                                                                    mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_offer_ids(client=client)

        # Then
        client.ltrim.assert_called_once_with(mock_redis_list, mock_redis_lrange_end, -1)


class HandleVenueIdsTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', return_value='fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_add_venue_id_to_redis_when_algolia_feature_is_enabled(self,
                                                                           mock_redis,
                                                                           mock_redis_list,
                                                                           mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_venue_id(client=client, venue_id=1)

        # Then
        client.rpush.assert_called_once_with(mock_redis_list, 1)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', return_value='fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_not_add_venue_id_to_redis_when_algolia_feature_is_disabled(self,
                                                                                    mock_redis,
                                                                                    mock_redis_list,
                                                                                    mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_venue_id(client=client, venue_id=1)

        # Then
        client.rpush.assert_not_called()

    @patch('connectors.redis.REDIS_VENUE_IDS_CHUNK_SIZE', return_value=1000)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', return_value='fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_return_venue_ids_from_redis(self, mock_redis, mock_redis_list, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()

        # When
        get_venue_ids(client=client)

        # Then
        client.lrange.assert_called_once_with(mock_redis_list, 0, mock_redis_lrange_end)

    @patch('connectors.redis.REDIS_VENUE_IDS_CHUNK_SIZE', return_value=1000)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', return_value='fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_delete_given_range_of_venue_ids_from_redis(self, mock_redis, mock_redis_list,
                                                                    mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_venue_ids(client=client)

        # Then
        client.ltrim.assert_called_once_with(mock_redis_list, mock_redis_lrange_end, -1)


class HandleVenueProvidersTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', return_value='fake_list_venue_providers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_add_venue_provider_to_redis_when_algolia_feature_is_enabled(self,
                                                                                mock_redis,
                                                                                mock_redis_list,
                                                                                mock_feature_active,
                                                                                app):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()
        provider = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=user, offerer=offerer)
        venue = create_venue(idx=1, offerer=offerer)
        venue_provider = create_venue_provider(idx=1, provider=provider, venue=venue)
        PcObject.save(user_offerer, venue_provider)

        # When
        add_venue_provider(client=client, venue_provider=venue_provider)

        # Then
        client.rpush.assert_called_once_with(mock_redis_list, '{"id": 1, "lastProviderId": null, "venueId": 1}')

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', return_value='fake_list_venue_providers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_not_add_venue_provider_to_redis_when_algolia_feature_is_disabled(self,
                                                                                     mock_redis,
                                                                                     mock_redis_list,
                                                                                     mock_feature_active,
                                                                                     app):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()
        provider = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=user, offerer=offerer)
        venue = create_venue(idx=1, offerer=offerer)
        venue_provider = create_venue_provider(idx=1, provider=provider, venue=venue)
        PcObject.save(user_offerer, venue_provider)

        # When
        add_venue_provider(client=client, venue_provider=venue_provider)

        # Then
        client.rpush.assert_not_called()

    @patch('connectors.redis.REDIS_VENUE_PROVIDERS_CHUNK_SIZE', return_value=2)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', return_value='fake_list_venue_providers')
    @patch('connectors.redis.redis')
    def test_should_return_venue_providers_from_redis(self, mock_redis, mock_redis_list, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()
        client.lrange.return_value = [
            '{"id": 1, "lastProviderId": 2, "venueId": 3}',
            '{"id": 2, "lastProviderId": 7, "venueId": 9}'
        ]

        # When
        result = get_venue_providers(client=client)

        # Then
        client.lrange.assert_called_once_with(mock_redis_list, 0, mock_redis_lrange_end)
        assert result == [
            {'id': 1, 'lastProviderId': 2, 'venueId': 3},
            {'id': 2, 'lastProviderId': 7, 'venueId': 9}
        ]

    @patch('connectors.redis.REDIS_VENUE_PROVIDERS_CHUNK_SIZE', return_value=2)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', return_value='fake_list_venue_providers')
    @patch('connectors.redis.redis')
    def test_should_delete_venue_providers_from_redis(self, mock_redis, mock_redis_list, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_venue_providers(client=client)

        # Then
        client.ltrim.assert_called_once_with(mock_redis_list, mock_redis_lrange_end, -1)
