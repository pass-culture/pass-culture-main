import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational.models import CollectiveOfferDisplayedStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/collective/home/bookable-offers"


def create_collective_offer(
    venue, status: CollectiveOfferDisplayedStatus, booking_limit_days_from_now: int, start_datetime_days_from_now: int
):
    now = date_utils.get_naive_utc_now()
    offer = factories.create_collective_offer_by_status(status, venue=venue)
    if offer.collectiveStock is not None:
        offer.collectiveStock.bookingLimitDatetime = now + datetime.timedelta(days=booking_limit_days_from_now)
        offer.collectiveStock.startDatetime = now + datetime.timedelta(days=start_datetime_days_from_now)
    return offer


class Returns200Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # collective_offer limit 3
    expected_num_queries += 1  # collective_offer exists

    def test_one_collective_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.BookedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")
            assert response.status_code == 200

        stock = offer.collectiveStock
        assert response.json == {
            "hasOffers": True,
            "offers": [
                {
                    "id": offer.id,
                    "allowedActions": ["CAN_EDIT_DISCOUNT", "CAN_DUPLICATE", "CAN_CANCEL"],
                    "name": offer.name,
                    "imageUrl": None,
                    "displayedStatus": "BOOKED",
                    "collectiveStock": {
                        "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat() + "Z",
                        "endDatetime": stock.endDatetime.isoformat() + "Z",
                        "numberOfTickets": 25,
                        "startDatetime": stock.startDatetime.isoformat() + "Z",
                    },
                }
            ],
        }

    def test_no_offers(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")
            assert response.status_code == 200

        assert response.json == {"hasOffers": False, "offers": []}

    def test_user_has_no_access(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        factories.PublishedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user.email)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")
            assert response.status_code == 200

        assert response.json == {"hasOffers": False, "offers": []}

    def test_with_multiple_status_filters(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        booked_offer = factories.BookedCollectiveOfferFactory(venue=venue)
        prebooked_offer = factories.PrebookedCollectiveOfferFactory(venue=venue)
        factories.CancelledDueToExpirationCollectiveOfferFactory(venue=venue)
        factories.ArchivedCollectiveOfferFactory(venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")
            assert response.status_code == 200

        response_json = response.json
        assert {offer["id"] for offer in response_json["offers"]} == {booked_offer.id, prebooked_offer.id}

    def test_status_filtering(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        offers_by_status = {}
        for status in CollectiveOfferDisplayedStatus:
            if status in [CollectiveOfferDisplayedStatus.UNDER_REVIEW, CollectiveOfferDisplayedStatus.PUBLISHED]:
                continue
            offers_by_status[status] = factories.create_collective_offer_by_status(status, venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")
            assert response.status_code == 200

        response_json = response.json
        assert {offer["id"] for offer in response_json["offers"]} == {
            offers_by_status[CollectiveOfferDisplayedStatus.PREBOOKED].id,
            offers_by_status[CollectiveOfferDisplayedStatus.BOOKED].id,
        }

    @pytest.mark.parametrize(
        "offer_1, offer_2, offer_3, offer_4, expected_order",
        # Sorting logic:
        # 1. Offers with PREBOOKED or PUBLISHED status and booking limit < 7 days are prioritized by urgency
        # 2. When same urgency, sorted by CollectiveStock.startDatetime (most recent first)
        [
            (
                # displayedStatus, bookingLimitDaysFromNow, startDatetimeDaysFromNow
                (CollectiveOfferDisplayedStatus.PREBOOKED, 10, 11),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 4, 11),
                (CollectiveOfferDisplayedStatus.PREBOOKED, 1, 11),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 1, 3),
                [4, 3, 2],
            ),
            (
                # displayedStatus, bookingLimitDaysFromNow, startDatetimeDaysFromNow
                (CollectiveOfferDisplayedStatus.PUBLISHED, 1, 12),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 8, 8),
                (CollectiveOfferDisplayedStatus.PREBOOKED, 5, 11),
                (CollectiveOfferDisplayedStatus.PREBOOKED, 10, 11),
                [1, 3, 2],
            ),
            (
                # displayedStatus, bookingLimitDaysFromNow, startDatetimeDaysFromNow
                (CollectiveOfferDisplayedStatus.BOOKED, 1, 12),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 8, 8),
                (CollectiveOfferDisplayedStatus.PREBOOKED, 5, 11),
                (CollectiveOfferDisplayedStatus.PREBOOKED, 10, 11),
                [3, 2, 4],
            ),
            (
                # displayedStatus, bookingLimitDaysFromNow, startDatetimeDaysFromNow
                (CollectiveOfferDisplayedStatus.PUBLISHED, 10, 12),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 10, 11),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 10, 10),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 10, 30),
                [3, 2, 1],
            ),
            (
                # displayedStatus, bookingLimitDaysFromNow, startDatetimeDaysFromNow
                (CollectiveOfferDisplayedStatus.UNDER_REVIEW, 10, 12),
                (CollectiveOfferDisplayedStatus.BOOKED, 10, 11),
                (CollectiveOfferDisplayedStatus.EXPIRED, -1, 10),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 10, 30),
                [2, 1, 4],
            ),
            (
                # displayedStatus, bookingLimitDaysFromNow, startDatetimeDaysFromNow
                (CollectiveOfferDisplayedStatus.UNDER_REVIEW, 10, 12),
                (CollectiveOfferDisplayedStatus.BOOKED, 10, 11),
                (CollectiveOfferDisplayedStatus.PREBOOKED, 1, 20),
                (CollectiveOfferDisplayedStatus.PUBLISHED, 10, 30),
                [3, 2, 1],
            ),
        ],
    )
    def test_collective_offers_sorting(self, client, offer_1, offer_2, offer_3, offer_4, expected_order):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        offers = {
            1: create_collective_offer(venue, *offer_1),
            2: create_collective_offer(venue, *offer_2),
            3: create_collective_offer(venue, *offer_3),
            4: create_collective_offer(venue, *offer_4),
        }

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue.id}")
            assert response.status_code == 200

        ids = [offer["id"] for offer in response.json["offers"]]
        assert len(ids) == len(expected_order)

        assert ids == [offers[offer_type].id for offer_type in expected_order]


class Return400Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # rollback

    def test_return_error_when_no_venue_given(self, client):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(URL)
            assert response.status_code == 400

        assert response.json == {"venueId": ["Ce champ est obligatoire"]}
