import os
from unittest.mock import patch, MagicMock

import redis

from connectors.redis import add_offer_id, get_offer_ids, delete_offer_ids, add_venue_id, \
    get_venue_ids, delete_venue_ids, _add_venue_provider, get_venue_providers, \
    delete_venue_providers, send_venue_provider_data_to_redis, add_offer_ids_to_set, delete_offer_ids_from_set, \
    get_offer_ids_from_set
from repository import repository
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
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', 'fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_add_offer_id_to_redis_when_algolia_feature_is_enabled(self,
                                                                          mock_redis,
                                                                          mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_offer_id(client=client, offer_id=1)

        # Then
        client.rpush.assert_called_once_with('fake_list_offer_ids', 1)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', 'fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_not_add_offer_id_to_redis_when_algolia_feature_is_disabled(self,
                                                                               mock_redis,
                                                                               mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_offer_id(client=client, offer_id=1)

        # Then
        client.rpush.assert_not_called()

    @patch('connectors.redis.REDIS_OFFER_IDS_CHUNK_SIZE', return_value=1000)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', 'fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_return_offer_ids_from_redis(self, mock_redis, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()

        # When
        get_offer_ids(client=client)

        # Then
        client.lrange.assert_called_once_with('fake_list_offer_ids', 0, mock_redis_lrange_end)

    @patch('connectors.redis.REDIS_OFFER_IDS_CHUNK_SIZE', return_value=500)
    @patch('connectors.redis.REDIS_LIST_OFFER_IDS_NAME', 'fake_list_offer_ids')
    @patch('connectors.redis.redis')
    def test_should_delete_given_range_of_offer_ids_from_redis(self,
                                                               mock_redis,
                                                               mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_offer_ids(client=client)

        # Then
        client.ltrim.assert_called_once_with('fake_list_offer_ids', mock_redis_lrange_end, -1)


class HandleVenueIdsTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', 'fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_add_venue_id_to_redis_when_algolia_feature_is_enabled(self,
                                                                          mock_redis,
                                                                          mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_venue_id(client=client, venue_id=1)

        # Then
        client.rpush.assert_called_once_with('fake_list_venue_ids', 1)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', 'fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_not_add_venue_id_to_redis_when_algolia_feature_is_disabled(self,
                                                                               mock_redis,
                                                                               mock_feature_active):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_venue_id(client=client, venue_id=1)

        # Then
        client.rpush.assert_not_called()

    @patch('connectors.redis.REDIS_VENUE_IDS_CHUNK_SIZE', return_value=1000)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', 'fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_return_venue_ids_from_redis(self, mock_redis, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()

        # When
        get_venue_ids(client=client)

        # Then
        client.lrange.assert_called_once_with('fake_list_venue_ids', 0, mock_redis_lrange_end)

    @patch('connectors.redis.REDIS_VENUE_IDS_CHUNK_SIZE', return_value=1000)
    @patch('connectors.redis.REDIS_LIST_VENUE_IDS_NAME', 'fake_list_venue_ids')
    @patch('connectors.redis.redis')
    def test_should_delete_given_range_of_venue_ids_from_redis(self, mock_redis, mock_redis_lrange_end):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_venue_ids(client=client)

        # Then
        client.ltrim.assert_called_once_with('fake_list_venue_ids', mock_redis_lrange_end, -1)


class HandleVenueProvidersTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', 'fake_list_venue_providers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_add_venue_provider_to_redis_when_algolia_feature_is_enabled(self,
                                                                                mock_redis,
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
        repository.save(user_offerer, venue_provider)

        # When
        _add_venue_provider(client=client, venue_provider=venue_provider)

        # Then
        client.rpush.assert_called_once_with('fake_list_venue_providers',
                                             '{"id": 1, "providerId": 1, "venueId": 1}')

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', 'fake_list_venue_providers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_not_add_venue_provider_to_redis_when_algolia_feature_is_disabled(self,
                                                                                     mock_redis,
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
        repository.save(user_offerer, venue_provider)

        # When
        _add_venue_provider(client=client, venue_provider=venue_provider)

        # Then
        client.rpush.assert_not_called()

    @patch('connectors.redis._add_venue_provider')
    @patch('connectors.redis.redis')
    @clean_database
    def test_send_venue_provider_should_call_add_venue_provider_with_redis_client_and_venue_provider(self,
                                                                                                     mock_redis,
                                                                                                     mock_add_venue_provider,
                                                                                                     app):
        # Given
        mock_redis.from_url = MagicMock()
        mock_redis.from_url.return_value = MagicMock()
        provider = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(idx=1, offerer=offerer)
        venue_provider = create_venue_provider(idx=1, provider=provider, venue=venue)
        repository.save(venue_provider)

        # When
        send_venue_provider_data_to_redis(venue_provider=venue_provider)

        # Then
        mock_add_venue_provider.assert_called_once_with(client=mock_redis.from_url.return_value,
                                                        venue_provider=venue_provider)

    @patch('connectors.redis.REDIS_VENUE_PROVIDERS_CHUNK_SIZE', 2)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', 'fake_list_venue_providers')
    @patch('connectors.redis.redis')
    def test_should_return_venue_providers_from_redis(self, mock_redis):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()
        client.lrange.return_value = [
            '{"id": 1, "providerId": 2, "venueId": 3}',
            '{"id": 2, "providerId": 7, "venueId": 9}'
        ]

        # When
        result = get_venue_providers(client=client)

        # Then
        client.lrange.assert_called_once_with('fake_list_venue_providers', 0, 2)
        assert result == [
            {'id': 1, 'providerId': 2, 'venueId': 3},
            {'id': 2, 'providerId': 7, 'venueId': 9}
        ]

    @patch('connectors.redis.REDIS_VENUE_PROVIDERS_CHUNK_SIZE', 2)
    @patch('connectors.redis.REDIS_LIST_VENUE_PROVIDERS_NAME', 'fake_list_venue_providers')
    @patch('connectors.redis.redis')
    def test_should_delete_venue_providers_from_redis(self, mock_redis):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_venue_providers(client=client)

        # Then
        client.ltrim.assert_called_once_with('fake_list_venue_providers', 2, -1)


class AddOfferIdsToSetTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_SET_INDEXED_OFFER_IDS_NAME', 'fake_redis_set_indexed_offers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_add_offer_ids_to_redis_set_when_algolia_feature_is_enabled(self,
                                                                               mock_redis,
                                                                               mock_feature_active,
                                                                               app):
        # Given
        client = MagicMock()
        client.sadd = MagicMock()
        offer_ids = [1, 2, 3]

        # When
        add_offer_ids_to_set(client=client, offer_ids=offer_ids)

        # Then
        client.sadd.assert_called_once_with('fake_redis_set_indexed_offers', *offer_ids)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_SET_INDEXED_OFFER_IDS_NAME', 'fake_redis_set_indexed_offers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_not_add_offer_ids_to_redis_set_when_algolia_feature_is_disabled(self,
                                                                                    mock_redis,
                                                                                    mock_feature_active,
                                                                                    app):
        # Given
        client = MagicMock()
        client.sadd = MagicMock()
        offer_ids = [1, 2, 3]

        # When
        add_offer_ids_to_set(client=client, offer_ids=offer_ids)

        # Then
        client.sadd.assert_not_called()


class DeleteOfferIdsFromSetTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_SET_INDEXED_OFFER_IDS_NAME', 'fake_redis_set_indexed_offers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_delete_offer_ids_from_redis_set_when_algolia_feature_is_enabled(self,
                                                                                    mock_redis,
                                                                                    mock_feature_active,
                                                                                    app):
        # Given
        client = MagicMock()
        client.srem = MagicMock()
        offer_ids = [1, 2, 3]

        # When
        delete_offer_ids_from_set(client=client, offer_ids=offer_ids)

        # Then
        client.srem.assert_called_once_with('fake_redis_set_indexed_offers', *offer_ids)

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_SET_INDEXED_OFFER_IDS_NAME', 'fake_redis_set_indexed_offers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_not_delete_offer_ids_from_redis_set_when_algolia_feature_is_disabled(self,
                                                                                         mock_redis,
                                                                                         mock_feature_active,
                                                                                         app):
        # Given
        client = MagicMock()
        client.srem = MagicMock()
        offer_ids = [1, 2, 3]

        # When
        delete_offer_ids_from_set(client=client, offer_ids=offer_ids)

        # Then
        client.srem.assert_not_called()


class GetOfferIdsFromSetTest:
    @patch('connectors.redis.feature_queries.is_active', return_value=True)
    @patch('connectors.redis.REDIS_SET_INDEXED_OFFER_IDS_NAME', 'fake_redis_set_indexed_offers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_get_offer_ids_from_redis_set_when_algolia_feature_is_enabled(self,
                                                                                 mock_redis,
                                                                                 mock_feature_active,
                                                                                 app):
        # Given
        client = MagicMock()
        client.smembers = MagicMock()
        client.smembers.return_value = {'1', '2'}

        # When
        result = get_offer_ids_from_set(client=client)

        # Then
        client.smembers.assert_called_once_with('fake_redis_set_indexed_offers')
        assert result == {1, 2}

    @patch('connectors.redis.feature_queries.is_active', return_value=False)
    @patch('connectors.redis.REDIS_SET_INDEXED_OFFER_IDS_NAME', 'fake_redis_set_indexed_offers')
    @patch('connectors.redis.redis')
    @clean_database
    def test_should_not_get_offer_ids_from_redis_set_when_algolia_feature_is_disabled(self,
                                                                                      mock_redis,
                                                                                      mock_feature_active,
                                                                                      app):
        # Given
        client = MagicMock()
        client.smembers = MagicMock()

        # When
        get_offer_ids_from_set(client=client)

        # Then
        client.smembers.assert_not_called()
