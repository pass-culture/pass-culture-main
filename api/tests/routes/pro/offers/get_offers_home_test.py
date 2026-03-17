import datetime
from operator import itemgetter

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import offer_mixin

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/offers/home"


class Returns200Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # select on user_offerer for venue access
    expected_num_queries += 1  # select on offers
    expected_num_queries += 1  # select on stocks (selectinload)

    def test_home_offers(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer_event = factories.EventOfferFactory(venue=venue)
        stock = factories.EventStockFactory(offer=offer_event, dnBookedQuantity=30)
        offer_thing = factories.ThingOfferFactory(venue=venue)
        factories.ThingStockFactory(offer=offer_thing, dnBookedQuantity=40)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert response.json == [
            {
                "id": offer_event.id,
                "name": offer_event.name,
                "status": "ACTIVE",
                "isEvent": True,
                "thumbUrl": None,
                "bookingsCount": 30,
                "stocks": [{"beginningDatetime": stock.beginningDatetime.isoformat() + "Z"}],
            },
            {
                "id": offer_thing.id,
                "name": offer_thing.name,
                "status": "ACTIVE",
                "isEvent": False,
                "thumbUrl": None,
                "bookingsCount": 40,
                "stocks": [{"beginningDatetime": None}],
            },
        ]

    def test_home_offer_stocks(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.EventOfferFactory(venue=venue)
        stock_1 = factories.EventStockFactory(offer=offer, dnBookedQuantity=20)
        stock_2 = factories.EventStockFactory(offer=offer, dnBookedQuantity=30)
        # soft-deleted stock does not appear in stocks list but booking count is added to the total
        factories.EventStockFactory(offer=offer, dnBookedQuantity=10, isSoftDeleted=True)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert response.json[0]["bookingsCount"] == 30 + 20 + 10
        expected = [
            {"beginningDatetime": stock_1.beginningDatetime.isoformat() + "Z"},
            {"beginningDatetime": stock_2.beginningDatetime.isoformat() + "Z"},
        ]
        result = response.json[0]["stocks"]
        assert sorted(result, key=itemgetter("beginningDatetime")) == sorted(
            expected, key=itemgetter("beginningDatetime")
        )

    def test_no_offers(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        num_queries = self.expected_num_queries - 1  # no select on stock
        with assert_num_queries(num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert response.json == []

    def test_status_filter(self, client: TestClient):
        now = datetime.datetime.now()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # pending, published -> in the result
        pending_offer = factories.EventOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.PENDING,
            publicationDatetime=now - datetime.timedelta(days=1),
        )
        assert pending_offer.status == offer_mixin.OfferStatus.PENDING
        published_offer = factories.EventOfferFactory(
            venue=venue, bookingAllowedDatetime=now + datetime.timedelta(days=10)
        )
        assert published_offer.status == offer_mixin.OfferStatus.PUBLISHED

        # draft, rejected, expired, inactive -> not in the result
        draft_offer = factories.DraftOfferFactory(venue=venue)
        assert draft_offer.status == offer_mixin.OfferStatus.DRAFT
        rejected_offer = factories.OfferFactory(venue=venue, validation=offer_mixin.OfferValidationStatus.REJECTED)
        assert rejected_offer.status == offer_mixin.OfferStatus.REJECTED
        inactive_offer = factories.OfferFactory(venue=venue, publicationDatetime=None)
        assert inactive_offer.status == offer_mixin.OfferStatus.INACTIVE
        expired_offer = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=expired_offer, bookingLimitDatetime=now - datetime.timedelta(days=1))
        assert expired_offer.status == offer_mixin.OfferStatus.EXPIRED

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [result["id"] for result in response.json] == [pending_offer.id, published_offer.id]

    def test_publication_filter(self, client: TestClient):
        now = datetime.datetime.now()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # only offers with publicationDatetime in the last 90 days are received
        old_publication_offer = factories.EventOfferFactory(
            venue=venue, publicationDatetime=now - datetime.timedelta(days=100)
        )
        factories.EventStockFactory(offer=old_publication_offer)
        assert old_publication_offer.status == offer_mixin.OfferStatus.ACTIVE
        offer = factories.EventOfferFactory(venue=venue, publicationDatetime=now - datetime.timedelta(days=10))
        factories.EventStockFactory(offer=offer)
        assert offer.status == offer_mixin.OfferStatus.ACTIVE
        scheduled_offer = factories.EventOfferFactory(
            venue=venue, publicationDatetime=now + datetime.timedelta(days=10)
        )
        assert scheduled_offer.status == offer_mixin.OfferStatus.SCHEDULED

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [result["id"] for result in response.json] == [offer.id, scheduled_offer.id]

    def test_sort_events(self, client: TestClient):
        now = datetime.datetime.now()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        active_offer = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=active_offer)
        pending_offer = factories.EventOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.PENDING,
            publicationDatetime=now - datetime.timedelta(days=1),
        )
        sold_out_offer = factories.EventOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [(result["id"], result["status"]) for result in response.json] == [
            (pending_offer.id, "PENDING"),
            (sold_out_offer.id, "SOLD_OUT"),
            (active_offer.id, "ACTIVE"),
        ]

    def test_sort_things(self, client: TestClient):
        now = datetime.datetime.now()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        active_offer = factories.ThingOfferFactory(venue=venue)
        factories.ThingStockFactory(offer=active_offer)
        pending_offer = factories.ThingOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.PENDING,
            publicationDatetime=now - datetime.timedelta(days=1),
        )
        sold_out_offer = factories.ThingOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [(result["id"], result["status"]) for result in response.json] == [
            (pending_offer.id, "PENDING"),
            (sold_out_offer.id, "SOLD_OUT"),
            (active_offer.id, "ACTIVE"),
        ]

    def test_sort_event_and_things(self, client: TestClient):
        now = datetime.datetime.now()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        sold_out_event = factories.EventOfferFactory(venue=venue)
        pending_event = factories.EventOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.PENDING,
            publicationDatetime=now - datetime.timedelta(days=1),
        )
        pending_thing = factories.ThingOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.PENDING,
            publicationDatetime=now - datetime.timedelta(days=1),
        )

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [(result["id"], result["status"]) for result in response.json] == [
            (pending_event.id, "PENDING"),
            (pending_thing.id, "PENDING"),
            (sold_out_event.id, "SOLD_OUT"),
        ]

    def test_sort_event_and_things_other_status(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        sold_out_thing = factories.ThingOfferFactory(venue=venue)
        active_event = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=active_event)
        active_thing = factories.ThingOfferFactory(venue=venue)
        factories.EventStockFactory(offer=active_thing)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [(result["id"], result["status"]) for result in response.json] == [
            (sold_out_thing.id, "SOLD_OUT"),
            (active_event.id, "ACTIVE"),
            (active_thing.id, "ACTIVE"),
        ]

    def test_sort_event_dates(self, client: TestClient):
        now = datetime.datetime.now()
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # one stock, first date J+5
        offer_1 = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer_1, beginningDatetime=now + datetime.timedelta(days=5))

        # two stocks, first date is J+2
        offer_2 = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer_1, beginningDatetime=now + datetime.timedelta(days=10))
        factories.EventStockFactory(offer=offer_2, beginningDatetime=now + datetime.timedelta(days=2))

        # two stocks, one is passed, first date is J+7
        offer_3 = factories.EventOfferFactory(venue=venue)
        factories.EventStockFactory(offer=offer_3, beginningDatetime=now + datetime.timedelta(days=7))
        factories.EventStockFactory(offer=offer_3, beginningDatetime=now - datetime.timedelta(days=1))

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")

        assert response.status_code == 200
        assert [(result["id"], result["status"]) for result in response.json] == [
            (offer_2.id, "ACTIVE"),
            (offer_1.id, "ACTIVE"),
            (offer_3.id, "ACTIVE"),
        ]


class Return400Test:
    def test_user_has_no_access(self, client: TestClient):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        factories.EventOfferFactory(venue=venue)

        client = client.with_session_auth(user.email)
        venue_id = venue.id
        num_queries = AUTHENTICATION_QUERIES
        num_queries += 1  # select on user_offerer for venue access
        num_queries += 1  # rollback
        num_queries += 1  # rollback
        with assert_num_queries(num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")

        assert response.status_code == 403

    def test_return_error_when_no_venue_given(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        num_queries = AUTHENTICATION_QUERIES
        num_queries += 1  # rollback
        with assert_num_queries(num_queries):
            response = client.get(URL)

        assert response.status_code == 400
        assert response.json == {"venueId": ["Ce champ est obligatoire"]}
