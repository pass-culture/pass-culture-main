from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.offers import repository as offers_repository
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.serialization import offers_serialize


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.features(WIP_INDIVIDUAL_OFFERS_LIST_V2=True),
]


def _create_pro_with_venue():
    pro = users_factories.ProFactory()
    venue = offerers_factories.VenueFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)
    return pro, venue


class Returns200Test:
    number_of_queries = testing.AUTHENTICATION_QUERIES
    number_of_queries += 1  # check user access to venue
    number_of_queries += 1  # count offers
    number_of_queries += 1  # select page offer ids
    number_of_queries += 1  # select offers with product
    number_of_queries += 1  # select mediations
    number_of_queries += 1  # select stocks
    number_of_queries += 1  # select current headline offer

    def test_returns_thing_offers_of_the_venue(self, client):
        pro, venue = _create_pro_with_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue, name="Le Petit Prince")
        offers_factories.ThingStockFactory(offer=offer, quantity=10, dnBookedQuantity=3)
        offers_factories.ThingStockFactory(offer=offer, quantity=5, dnBookedQuantity=1)
        offers_factories.ThingStockFactory(offer=offer, dnBookedQuantity=2, isSoftDeleted=True)
        offers_factories.EventOfferFactory(venue=venue)
        offers_factories.ThingOfferFactory()

        venue_id = venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/thing-offers?venueId={venue_id}&status=ACTIVE")
            assert response.status_code == 200

        assert response.json == {
            "offers": [
                {
                    "id": offer.id,
                    "name": "Le Petit Prince",
                    "thumbUrl": None,
                    "isHeadlineOffer": False,
                    "remainingQuantity": 11,
                    "bookingsCount": 6,
                }
            ],
            "nextCursor": None,
            "total": 1,
            "totalIsCapped": False,
        }

    def test_remaining_quantity_is_unlimited_if_a_stock_is_unlimited(self, client):
        pro, venue = _create_pro_with_venue()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.ThingStockFactory(offer=offer, quantity=10)
        offers_factories.ThingStockFactory(offer=offer, quantity=None)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 200
        assert response.json["offers"][0]["remainingQuantity"] == "unlimited"

    def test_keeps_the_order_of_the_page(self, client):
        pro, venue = _create_pro_with_venue()
        batman = offers_factories.ThingOfferFactory(venue=venue, name="Batman")
        asterix = offers_factories.ThingOfferFactory(venue=venue, name="Astérix le Gaulois")
        candide = offers_factories.ThingOfferFactory(venue=venue, name="Candide")

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=SOLD_OUT")

        assert response.status_code == 200
        assert [offer["id"] for offer in response.json["offers"]] == [asterix.id, batman.id, candide.id]

    def test_paginates_with_cursor(self, client):
        pro, venue = _create_pro_with_venue()
        first, second, third = [
            offers_factories.ThingOfferFactory(venue=venue, name=name) for name in ("Astérix", "Batman", "Candide")
        ]
        authenticated_client = client.with_session_auth(email=pro.email)

        first_page = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=SOLD_OUT&limit=2")
        second_page = authenticated_client.get(
            f"/thing-offers?venueId={venue.id}&status=SOLD_OUT&limit=2&cursor={first_page.json['nextCursor']}"
        )

        assert [offer["id"] for offer in first_page.json["offers"]] == [first.id, second.id]
        assert first_page.json["nextCursor"] is not None
        assert [offer["id"] for offer in second_page.json["offers"]] == [third.id]
        assert second_page.json["nextCursor"] is None
        assert first_page.json["total"] == second_page.json["total"] == 3

    @patch("pcapi.core.offers.constants.OFFERS_LIST_TOTAL_MAX", 2)
    def test_total_is_capped(self, client):
        pro, venue = _create_pro_with_venue()
        offers_factories.ThingOfferFactory.create_batch(5, venue=venue)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=SOLD_OUT")

        assert response.status_code == 200
        assert response.json["total"] == 2
        assert response.json["totalIsCapped"] is True

    @patch("pcapi.routes.pro.offers.offers_repository.get_thing_offers_by_ids", return_value=[])
    @patch(
        "pcapi.routes.pro.offers.offers_repository.get_paginated_thing_offer_ids",
        return_value=offers_repository.PaginatedOfferIds(offer_ids=[], next_cursor=None, total=0),
    )
    def test_passes_the_filters_to_the_repository(self, mocked_get_paginated_thing_offer_ids, _mocked, client):
        pro, venue = _create_pro_with_venue()
        cursor = offers_repository.ThingOffersCursor(name="Batman", id=12)
        encoded_cursor = offers_serialize.encode_offers_cursor(cursor)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(
            f"/thing-offers?venueId={venue.id}&cursor={encoded_cursor}&status=ACTIVE&nameOrEan=potter&creationMode=manual"
            "&isDigital=true&orderByDesc=true&limit=5"
        )

        assert response.status_code == 200
        mocked_get_paginated_thing_offer_ids.assert_called_once_with(
            venue_id=venue.id,
            per_page=5,
            cursor=cursor,
            status=OfferStatus.ACTIVE,
            name_keywords_or_ean="potter",
            creation_mode="manual",
            is_digital=True,
            order_by_desc=True,
        )

    def test_returns_whether_the_offer_is_the_headline_offer(self, client):
        pro, venue = _create_pro_with_venue()
        headline_offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.ThingStockFactory(offer=headline_offer)
        offers_factories.HeadlineOfferFactory(offer=headline_offer, venue=venue)
        other_offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.ThingStockFactory(offer=other_offer)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 200
        assert {offer["id"]: offer["isHeadlineOffer"] for offer in response.json["offers"]} == {
            headline_offer.id: True,
            other_offer.id: False,
        }


class Returns400Test:
    @pytest.mark.parametrize("limit", [0, 100, "abc"])
    def test_invalid_limit(self, client, limit):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE&limit={limit}")

        assert response.status_code == 400
        assert "limit" in response.json

    @pytest.mark.parametrize(
        "cursor",
        [
            "not-base64!",
            "bm90LWpzb24=",  # not-json
            "WzEsIDJd",  # [1, 2]
            "WyJBIiwgdHJ1ZV0=",  # ["A", true]
            "eyJhIjogMX0=",  # {"a": 1}
            "WyJBIiwgMSwgMl0=",  # ["A", 1, 2]
        ],
    )
    def test_invalid_cursor(self, client, cursor):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE&cursor={cursor}")

        assert response.status_code == 400
        assert "cursor" in response.json

    def test_invalid_status(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=NOPE")

        assert response.status_code == 400
        assert "status" in response.json

    def test_missing_status(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}")

        assert response.status_code == 400
        assert "status" in response.json

    def test_invalid_creation_mode(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE&creationMode=NOPE")

        assert response.status_code == 400
        assert "creationMode" in response.json


class Returns401Test:
    def test_user_is_not_logged_in(self, client):
        venue = offerers_factories.VenueFactory()

        response = client.get(f"/thing-offers?venueId={venue.id}")

        assert response.status_code == 401


class Returns404Test:
    def test_user_has_no_access_to_the_venue(self, client):
        pro = users_factories.ProFactory()
        offers_factories.ThingOfferFactory(venue__managingOfferer=offerers_factories.OffererFactory())
        venue = offerers_factories.VenueFactory()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 404

    @pytest.mark.features(WIP_INDIVIDUAL_OFFERS_LIST_V2=False)
    def test_feature_flag_is_disabled(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/thing-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 404


def test_cursor_encoding_round_trip():
    cursor = offers_repository.ThingOffersCursor(name="L'été à Noël & co ?/+", id=123)

    encoded_cursor = offers_serialize.encode_offers_cursor(cursor)

    assert offers_serialize.decode_thing_offers_cursor(encoded_cursor) == cursor
