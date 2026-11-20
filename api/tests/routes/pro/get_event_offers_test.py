import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.offers import repository as offers_repository
from pcapi.models.offer_mixin import OfferStatus
from pcapi.routes.serialization import offers_serialize
from pcapi.utils import date as date_utils


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
    number_of_queries += 1  # select offers with venue, location and product
    number_of_queries += 1  # select stocks
    number_of_queries += 1  # select mediations
    number_of_queries += 1  # select current headline offer

    def test_returns_event_offers_of_the_venue(self, client):
        pro, venue = _create_pro_with_venue()
        offer = offers_factories.EventOfferFactory(venue=venue, name="Le Mariage de Figaro")
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime(2030, 1, 16, 20), quantity=10, dnBookedQuantity=3
        )
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime(2030, 1, 15, 20), quantity=5, dnBookedQuantity=1
        )
        offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=datetime.datetime(2030, 1, 1, 20), dnBookedQuantity=2, isSoftDeleted=True
        )
        offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.EventOfferFactory()

        venue_id = venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/event-offers?venueId={venue_id}&status=ACTIVE")
            assert response.status_code == 200

        assert response.json == {
            "offers": [
                {
                    "id": offer.id,
                    "name": "Le Mariage de Figaro",
                    "thumbUrl": None,
                    "isHeadlineOffer": False,
                    "location": {
                        "id": venue.offererAddress.addressId,
                        "label": None,
                        "isManualEdition": False,
                        "isVenueLocation": True,
                        "banId": venue.offererAddress.address.banId,
                        "inseeCode": venue.offererAddress.address.inseeCode,
                        "postalCode": venue.offererAddress.address.postalCode,
                        "street": venue.offererAddress.address.street,
                        "city": venue.offererAddress.address.city,
                        "latitude": float(venue.offererAddress.address.latitude),
                        "longitude": float(venue.offererAddress.address.longitude),
                        "departmentCode": venue.offererAddress.address.departmentCode,
                    },
                    "firstBeginningDate": "2030-01-15",
                    "lastBeginningDate": "2030-01-16",
                    "remainingQuantity": 11,
                    "bookingsCount": 6,
                }
            ],
            "nextCursor": None,
            "total": 1,
            "totalIsCapped": False,
        }

    def test_dates_are_none_without_stock(self, client):
        pro, venue = _create_pro_with_venue()
        offers_factories.EventOfferFactory(venue=venue)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=SOLD_OUT")

        assert response.status_code == 200
        assert response.json["offers"][0]["firstBeginningDate"] is None
        assert response.json["offers"][0]["lastBeginningDate"] is None
        assert response.json["offers"][0]["remainingQuantity"] == 0

    def test_keeps_the_order_of_the_page(self, client):
        pro, venue = _create_pro_with_venue()
        now = date_utils.get_naive_utc_now().replace(microsecond=0)
        offers = []
        for days in (3, 1, 2):
            offer = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.EventStockFactory(offer=offer, beginningDatetime=now + datetime.timedelta(days=days))
            offers.append(offer)
        in_3_days, tomorrow, in_2_days = offers

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 200
        assert [offer["id"] for offer in response.json["offers"]] == [in_3_days.id, in_2_days.id, tomorrow.id]

    def test_paginates_with_cursor(self, client):
        pro, venue = _create_pro_with_venue()
        now = date_utils.get_naive_utc_now().replace(microsecond=0)
        dated_offers = []
        for days in (1, 2):
            offer = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.EventStockFactory(
                offer=offer, beginningDatetime=now + datetime.timedelta(days=days), quantity=0
            )
            dated_offers.append(offer)

        without_stock = offers_factories.EventOfferFactory(venue=venue)
        authenticated_client = client.with_session_auth(email=pro.email)

        first_page = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=SOLD_OUT&limit=2")
        second_page = authenticated_client.get(
            f"/event-offers?venueId={venue.id}&status=SOLD_OUT&limit=2&cursor={first_page.json['nextCursor']}"
        )

        assert [offer["id"] for offer in first_page.json["offers"]] == [offer.id for offer in reversed(dated_offers)]
        assert first_page.json["nextCursor"] is not None
        assert [offer["id"] for offer in second_page.json["offers"]] == [without_stock.id]
        assert second_page.json["nextCursor"] is None
        assert first_page.json["total"] == second_page.json["total"] == 3

    @patch("pcapi.core.offers.constants.OFFERS_LIST_TOTAL_MAX", 2)
    def test_total_is_capped(self, client):
        pro, venue = _create_pro_with_venue()
        offers_factories.EventOfferFactory.create_batch(5, venue=venue)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=SOLD_OUT")

        assert response.status_code == 200
        assert response.json["total"] == 2
        assert response.json["totalIsCapped"] is True

    @patch("pcapi.routes.pro.offers.offers_repository.get_event_offers_by_ids", return_value=[])
    @patch(
        "pcapi.routes.pro.offers.offers_repository.get_paginated_event_offer_ids",
        return_value=offers_repository.PaginatedOfferIds(offer_ids=[], next_cursor=None, total=0),
    )
    def test_passes_the_filters_to_the_repository(self, mocked_get_paginated_event_offer_ids, _mocked, client):
        pro, venue = _create_pro_with_venue()
        cursor = offers_repository.EventOffersCursor(first_beginning_datetime=datetime.datetime(2030, 1, 15, 20), id=12)
        encoded_cursor = offers_serialize.encode_offers_cursor(cursor)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(
            f"/event-offers?venueId={venue.id}&cursor={encoded_cursor}&status=ACTIVE&nameOrEan=figaro"
            "&creationMode=manual&isDigital=false&orderByDesc=false&periodBeginningDate=2030-01-01&periodEndingDate=2030-01-31"
            "&limit=5"
        )

        assert response.status_code == 200
        mocked_get_paginated_event_offer_ids.assert_called_once_with(
            venue_id=venue.id,
            per_page=5,
            cursor=cursor,
            status=OfferStatus.ACTIVE,
            name_keywords_or_ean="figaro",
            creation_mode="manual",
            is_digital=False,
            order_by_desc=False,
            period_beginning_date=datetime.date(2030, 1, 1),
            period_ending_date=datetime.date(2030, 1, 31),
        )

    def test_returns_whether_the_offer_is_the_headline_offer(self, client):
        pro, venue = _create_pro_with_venue()
        headline_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=headline_offer)
        offers_factories.HeadlineOfferFactory(offer=headline_offer, venue=venue)
        other_offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=other_offer)

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 200
        assert {offer["id"]: offer["isHeadlineOffer"] for offer in response.json["offers"]} == {
            headline_offer.id: True,
            other_offer.id: False,
        }

    def test_last_beginning_date_is_none_if_all_dates_are_on_the_same_day(self, client):
        pro, venue = _create_pro_with_venue()
        offer = offers_factories.EventOfferFactory(venue=venue)
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.datetime(2030, 1, 15, 10))
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.datetime(2030, 1, 15, 20))

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 200
        assert response.json["offers"][0]["firstBeginningDate"] == "2030-01-15"
        assert response.json["offers"][0]["lastBeginningDate"] is None

    def test_dates_are_in_the_timezone_of_the_offer(self, client):
        pro, venue = _create_pro_with_venue()
        offer = offers_factories.EventOfferFactory(venue=venue)
        # same day in UTC, but 21:00 on the 15th and 00:30 on the 16th in Paris
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.datetime(2030, 1, 15, 20))
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.datetime(2030, 1, 15, 23, 30))

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 200
        assert response.json["offers"][0]["firstBeginningDate"] == "2030-01-15"
        assert response.json["offers"][0]["lastBeginningDate"] == "2030-01-16"


class Returns400Test:
    @pytest.mark.parametrize("limit", [0, 100, "abc"])
    def test_invalid_limit(self, client, limit):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE&limit={limit}")

        assert response.status_code == 400
        assert "limit" in response.json

    @pytest.mark.parametrize(
        "cursor",
        [
            "not-base64!",
            "bm90LWpzb24=",  # not-json
            "WzEsIDJd",  # [1, 2]
            "WyJub3QtYS1kYXRlIiwgMV0=",  # ["not-a-date", 1]
            "W251bGwsIHRydWVd",  # [null, true]
            "eyJhIjogMX0=",  # {"a": 1}
        ],
    )
    def test_invalid_cursor(self, client, cursor):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE&cursor={cursor}")

        assert response.status_code == 400
        assert "cursor" in response.json

    def test_invalid_period(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(
            f"/event-offers?venueId={venue.id}&status=ACTIVE&periodBeginningDate=not-a-date"
        )

        assert response.status_code == 400
        assert "periodBeginningDate" in response.json

    def test_invalid_status(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=NOPE")

        assert response.status_code == 400
        assert "status" in response.json

    def test_missing_status(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}")

        assert response.status_code == 400
        assert "status" in response.json

    def test_invalid_creation_mode(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE&creationMode=NOPE")

        assert response.status_code == 400
        assert "creationMode" in response.json


class Returns401Test:
    def test_user_is_not_logged_in(self, client):
        venue = offerers_factories.VenueFactory()

        response = client.get(f"/event-offers?venueId={venue.id}")

        assert response.status_code == 401


class Returns404Test:
    def test_user_has_no_access_to_the_venue(self, client):
        pro = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 404

    @pytest.mark.features(WIP_INDIVIDUAL_OFFERS_LIST_V2=False)
    def test_feature_flag_is_disabled(self, client):
        pro, venue = _create_pro_with_venue()

        authenticated_client = client.with_session_auth(email=pro.email)
        response = authenticated_client.get(f"/event-offers?venueId={venue.id}&status=ACTIVE")

        assert response.status_code == 404


@pytest.mark.parametrize("first_beginning_datetime", [datetime.datetime(2030, 1, 15, 20, 30, 15), None])
def test_cursor_encoding_round_trip(first_beginning_datetime):
    cursor = offers_repository.EventOffersCursor(first_beginning_datetime=first_beginning_datetime, id=123)

    encoded_cursor = offers_serialize.encode_offers_cursor(cursor)

    assert offers_serialize.decode_event_offers_cursor(encoded_cursor) == cursor
