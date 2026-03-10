import datetime

import pytest

from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import AUTHENTICATION_QUERIES
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import db as db_utils

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/collective/home/offers-template"


class Returns200Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # select collective_offer_template
    expected_num_queries += 1  # exists

    def test_one_collective_offer_template(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = factories.create_collective_offer_template_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, venue=venue
        )

        client = client.with_session_auth(user_offerer.user.email)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")

        assert response.status_code == 200
        assert response.json == {
            "hasOffers": True,
            "offers": [
                {
                    "id": offer.id,
                    "allowedActions": [
                        "CAN_EDIT_DETAILS",
                        "CAN_ARCHIVE",
                        "CAN_CREATE_BOOKABLE_OFFER",
                        "CAN_HIDE",
                        "CAN_SHARE",
                    ],
                    "dates": {
                        "start": offer.start.isoformat() + "Z",
                        "end": offer.end.isoformat() + "Z",
                    },
                    "name": offer.name,
                    "imageUrl": None,
                    "displayedStatus": "PUBLISHED",
                }
            ],
        }

    def test_collective_offer_template_user_has_no_access(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.create_collective_offer_template_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, venue=venue
        )
        other_user = users_factories.UserFactory()

        client = client.with_session_auth(other_user.email)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")

        assert response.status_code == 200
        assert response.json == {"hasOffers": False, "offers": []}

    def test_offers_status(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # create an offer for each status, to check that the route returns published and under review offers only
        offer_by_status = {}
        for status in models.COLLECTIVE_OFFER_TEMPLATE_STATUSES:
            offer_by_status[status] = factories.create_collective_offer_template_by_status(status, venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")

        assert response.status_code == 200
        assert response.json["hasOffers"] is True
        assert {offer["id"] for offer in response.json["offers"]} == {
            offer_by_status[models.CollectiveOfferDisplayedStatus.PUBLISHED].id,
            offer_by_status[models.CollectiveOfferDisplayedStatus.UNDER_REVIEW].id,
        }

    def test_offers_sort(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        now = datetime.datetime.now()

        offer_1 = factories.create_collective_offer_template_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED, dateRange=None, venue=venue
        )
        offer_2 = factories.create_collective_offer_template_by_status(
            models.CollectiveOfferDisplayedStatus.PUBLISHED,
            dateRange=db_utils.make_timerange(now - datetime.timedelta(days=2), now + datetime.timedelta(days=30)),
            venue=venue,
        )
        offer_3 = factories.create_collective_offer_template_by_status(
            models.CollectiveOfferDisplayedStatus.UNDER_REVIEW,
            dateRange=db_utils.make_timerange(now + datetime.timedelta(days=3), now + datetime.timedelta(days=10)),
            venue=venue,
        )

        client = client.with_session_auth(user_offerer.user.email)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")

        assert response.status_code == 200
        assert response.json["hasOffers"] is True
        # offer withtout dates is last, the rest is ordered by start date
        assert [offer["id"] for offer in response.json["offers"]] == [offer_2.id, offer_3.id, offer_1.id]

    def test_offers_limit(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        factories.CollectiveOfferTemplateFactory.create_batch(5, venue=venue)

        client = client.with_session_auth(user_offerer.user.email)
        venue_id = venue.id
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId={venue_id}")

        assert response.status_code == 200
        assert response.json["hasOffers"] is True
        assert len(response.json["offers"]) == 3


class Return400Test:
    expected_num_queries = AUTHENTICATION_QUERIES
    expected_num_queries += 1  # rollback

    def test_return_error_when_venue_id_is_invalid(self, client: TestClient):
        user_offerer = offerers_factories.UserOffererFactory()

        client = client.with_session_auth(email=user_offerer.user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"{URL}?venueId=NOT_VALID")

        assert response.status_code == 400
        assert response.json == {"venueId": ["Saisissez un entier valide"]}
