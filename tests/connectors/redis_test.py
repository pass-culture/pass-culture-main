from unittest.mock import MagicMock

import pytest
import redis

from pcapi import settings
from pcapi.connectors.redis import add_offer_id
from pcapi.connectors.redis import add_offer_ids_in_error
from pcapi.connectors.redis import add_to_indexed_offers
from pcapi.connectors.redis import add_venue_id
from pcapi.connectors.redis import check_offer_exists
from pcapi.connectors.redis import delete_all_indexed_offers
from pcapi.connectors.redis import delete_indexed_offers
from pcapi.connectors.redis import delete_offer_ids_in_error
from pcapi.connectors.redis import delete_venue_ids
from pcapi.connectors.redis import get_offer_details
from pcapi.connectors.redis import get_offer_ids_in_error
from pcapi.connectors.redis import get_venue_ids


class RedisTest:
    @staticmethod
    def test_api_writes_value_in_redis():
        # Given
        key_to_insert = "foo"
        value_to_insert = "bar"
        redis_connection = redis.from_url(settings.REDIS_URL)

        # When
        redis_connection.set(key_to_insert, value_to_insert)

        # Then
        assert str(redis_connection.get(key_to_insert), "utf-8") == value_to_insert


class AddOfferIdTest:
    def test_should_add_offer_id(self):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_offer_id(client=client, offer_id=1)

        # Then
        client.rpush.assert_called_once_with("offer_ids", 1)


class AddVenueIdTest:
    def test_should_add_venue_id_when_algolia_feature_is_enabled(self):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_venue_id(client=client, venue_id=1)

        # Then
        client.rpush.assert_called_once_with("venue_ids", 1)


class GetVenueIdsTest:
    def test_should_return_venue_ids(self):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()

        # When
        get_venue_ids(client=client)

        # Then
        client.lrange.assert_called_once_with("venue_ids", 0, 1)

    def test_should_return_empty_array_when_exception(self):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()
        client.lrange.side_effect = redis.exceptions.RedisError

        # When
        result = get_venue_ids(client=client)

        # Then
        assert result == []


class DeleteVenueIdsTest:
    def test_should_delete_given_venue_ids_from_list(self):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_venue_ids(client=client)

        # Then
        client.ltrim.assert_called_once_with("venue_ids", 1, -1)


class AddToIndexedOffersTest:
    def test_should_add_to_indexed_offers(self, app):
        # Given
        client = MagicMock()
        client.hset = MagicMock()

        # When
        add_to_indexed_offers(
            pipeline=client,
            offer_id=1,
            offer_details={"dateRange": ["2020-01-01 10:00:00", "2020-01-06 12:00:00"], "name": "super offre"},
        )

        # Then
        client.hset.assert_called_once_with(
            "indexed_offers", 1, '{"dateRange": ["2020-01-01 10:00:00", "2020-01-06 12:00:00"], "name": "super offre"}'
        )


class DeleteIndexedOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_delete_indexed_offers(self, app):
        # Given
        client = MagicMock()
        client.hdel = MagicMock()
        offer_ids = [1, 2, 3]

        # When
        delete_indexed_offers(client=client, offer_ids=offer_ids)

        # Then
        client.hdel.assert_called_once_with("indexed_offers", *offer_ids)


class CheckOfferExistsTest:
    def test_should_return_true_when_offer_exists(self):
        # Given
        client = MagicMock()
        client.hexists = MagicMock()
        client.hexists.return_value = True

        # When
        result = check_offer_exists(client=client, offer_id=1)

        # Then
        client.hexists.assert_called_once_with("indexed_offers", 1)
        assert result

    def test_should_return_false_when_offer_not_exists(self):
        # Given
        client = MagicMock()
        client.hexists = MagicMock()
        client.hexists.return_value = False

        # When
        result = check_offer_exists(client=client, offer_id=1)

        # Then
        client.hexists.assert_called_once_with("indexed_offers", 1)
        assert result is False

    def test_should_return_false_when_exception(self):
        # Given
        client = MagicMock()
        client.hexists = MagicMock()
        client.hexists.side_effect = redis.exceptions.RedisError

        # When
        result = check_offer_exists(client=client, offer_id=1)

        # Then
        assert result is False


class GetOfferDetailsTest:
    def test_should_return_offer_details_when_offer_exists(self):
        # Given
        client = MagicMock()
        client.hget = MagicMock()
        client.hget.return_value = (
            '{"dateRange": ["2020-01-01 10:00:00", "2020-01-06 12:00:00"], "name": "super offre"}'
        )

        # When
        result = get_offer_details(client=client, offer_id=1)

        # Then
        client.hget.assert_called_once_with("indexed_offers", 1)
        assert result == {"dateRange": ["2020-01-01 10:00:00", "2020-01-06 12:00:00"], "name": "super offre"}

    def test_should_return_empty_dict_when_offer_does_exists(self):
        # Given
        client = MagicMock()
        client.hget = MagicMock()
        client.hget.return_value = None

        # When
        result = get_offer_details(client=client, offer_id=1)

        # Then
        client.hget.assert_called_once_with("indexed_offers", 1)
        assert result == {}

    def test_should_return_empty_dict_when_exception(self):
        # Given
        client = MagicMock()
        client.hget = MagicMock()
        client.hget.side_effect = redis.exceptions.RedisError

        # When
        result = get_offer_details(client=client, offer_id=1)

        # Then
        assert result == {}


class DeleteAllIndexedOffersTest:
    def test_should_delete_all_indexed_offers(self):
        # Given
        client = MagicMock()
        client.delete = MagicMock()

        # When
        delete_all_indexed_offers(client=client)

        # Then
        client.delete.assert_called_once_with("indexed_offers")


class AddOfferIdInErrorTest:
    def test_should_add_offer_id_in_error(self):
        # Given
        client = MagicMock()
        client.rpush = MagicMock()

        # When
        add_offer_ids_in_error(client=client, offer_ids=[1, 2])

        # Then
        client.rpush.assert_called_once_with("offer_ids_in_error", 1, 2)


class GetOfferIdsInErrorTest:
    def test_should_get_offer_ids_in_error(self):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()

        # When
        get_offer_ids_in_error(client=client)

        # Then
        client.lrange.assert_called_once_with("offer_ids_in_error", 0, 10000)

    def test_should_return_empty_array_when_exception(self):
        # Given
        client = MagicMock()
        client.lrange = MagicMock()
        client.lrange.side_effect = redis.exceptions.RedisError

        # When
        offer_ids = get_offer_ids_in_error(client=client)

        # Then
        assert offer_ids == []


class DeleteOfferIdsInErrorTest:
    def test_should_delete_given_range_of_offer_ids_in_error(self):
        # Given
        client = MagicMock()
        client.ltrim = MagicMock()

        # When
        delete_offer_ids_in_error(client=client)

        # Then
        client.ltrim.assert_called_once_with("offer_ids_in_error", 10000, -1)
