import secrets
from unittest.mock import patch

from pcapi.core import testing
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_domain_converter import (
    to_domain,
)
from pcapi.model_creators.generic_creators import (
    create_offerer,
    create_user,
    create_user_offerer,
    create_venue,
    create_stock,
)
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.repository import repository
from tests.conftest import TestClient
from pcapi.utils.human_ids import humanize


class Returns200:
    def should_filter_by_venue_when_user_is_admin_and_request_specific_venue_with_no_rights_on_it(
        self, app, db_session, assert_num_queries
    ):
        # Given
        admin = create_user(is_admin=True, can_book_free_offers=False)
        offerer = create_offerer()
        requested_venue = create_venue(offerer, siret="12345678912345")
        other_venue = create_venue(offerer, siret="54321987654321")
        offer_on_requested_venue = create_offer_with_thing_product(requested_venue)
        offer_on_other_venue = create_offer_with_thing_product(other_venue)
        stock = create_stock(offer=offer_on_requested_venue)
        repository.save(admin, stock, offer_on_other_venue)

        # when
        client = TestClient(app.test_client()).with_auth(email=admin.email)
        path = f"/offers?venueId={humanize(requested_venue.id)}"
        n_queries = testing.AUTHENTICATION_QUERIES
        n_queries += 1  # select offers
        n_queries += 1  # count offers
        n_queries += 5  # serializer: select stock, mediation, product, venue, offerer
        with assert_num_queries(n_queries):
            response = client.get(path)

        # then
        assert response.status_code == 200
        assert response.json == {
            "offers": [
                {
                    "hasBookingLimitDatetimesPassed": False,
                    "id": humanize(offer_on_requested_venue.id),
                    "isActive": True,
                    "isEditable": True,
                    "isEvent": False,
                    "isThing": True,
                    "name": "Test Book",
                    "stocks": [
                        {
                            "id": humanize(stock.id),
                            "offerId": humanize(offer_on_requested_venue.id),
                            "remainingQuantity": "unlimited",
                        }
                    ],
                    "thumbUrl": None,
                    "type": "ThingType.AUDIOVISUEL",
                    "venue": {
                        "id": humanize(requested_venue.id),
                        "isVirtual": False,
                        "managingOffererId": humanize(offerer.id),
                        "name": "La petite librairie",
                        "offererName": "Test Offerer",
                        "publicName": None,
                    },
                    "venueId": humanize(requested_venue.id),
                }
            ],
            "page": 1,
            "page_count": 1,
            "total_count": 1,
        }

    def should_filter_by_venue_when_user_is_not_admin_and_request_specific_venue_with_rights_on_it(
        self, app, db_session
    ):
        # Given
        pro = create_user(is_admin=False, can_book_free_offers=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro, offerer)
        requested_venue = create_venue(offerer, siret="12345678912345")
        other_venue = create_venue(offerer, siret="54321987654321")
        offer_on_requested_venue = create_offer_with_thing_product(requested_venue)
        offer_on_other_venue = create_offer_with_thing_product(other_venue)
        repository.save(
            pro, user_offerer, offer_on_requested_venue, offer_on_other_venue
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=pro.email)
            .get(f"/offers?venueId={humanize(requested_venue.id)}")
        )

        # then
        offers = response.json["offers"]
        assert response.status_code == 200
        assert len(offers) == 1

    @patch("pcapi.routes.offers.list_offers_for_pro_user")
    def test_results_are_paginated_with_pagination_details_in_body(
        self, list_offers_mock, app, db_session
    ):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)
        list_offers_mock.return_value = to_domain(
            offer_sql_entities=[offer1], current_page=1, total_pages=1, total_offers=2
        )

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=user.email)
            .get("/offers?paginate=1")
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "offers": [
                {
                    "hasBookingLimitDatetimesPassed": False,
                    "id": humanize(offer1.id),
                    "isActive": True,
                    "isEditable": True,
                    "isEvent": False,
                    "isThing": True,
                    "name": "Test Book",
                    "stocks": [],
                    "thumbUrl": None,
                    "type": "ThingType.AUDIOVISUEL",
                    "venue": {
                        "id": humanize(venue.id),
                        "isVirtual": False,
                        "managingOffererId": humanize(offerer.id),
                        "name": "La petite librairie",
                        "offererName": "Test Offerer",
                        "publicName": None,
                    },
                    "venueId": humanize(venue.id),
                }
            ],
            "page": 1,
            "page_count": 1,
            "total_count": 2,
        }

    @patch("pcapi.routes.offers.list_offers_for_pro_user")
    def test_does_not_show_result_to_user_offerer_when_not_validated(
        self, list_offers_mock, app, db_session
    ):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(
            user, offerer, validation_token=secrets.token_urlsafe(20)
        )
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer)
        list_offers_mock.return_value = to_domain(
            offer_sql_entities=[], current_page=0, total_pages=0, total_offers=0
        )

        # when
        response = (
            TestClient(app.test_client()).with_auth(email=user.email).get("/offers")
        )

        # then
        assert response.status_code == 200
        assert response.json == {
            "offers": [],
            "page": 0,
            "page_count": 0,
            "total_count": 0,
        }

    @patch("pcapi.routes.offers.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_venue_id(
        self, list_offers_mock, app, db_session
    ):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        repository.save(user_offerer, venue)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=user.email)
            .get("/offers?venueId=" + humanize(venue.id))
        )

        # then
        assert response.status_code == 200
        list_offers_mock.assert_called_once_with(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offerer_id=None,
            venue=venue,
            type_id=None,
            offers_per_page=None,
            name_keywords=None,
            page=None,
            exclude_active=False,
            exclude_inactive=False,
        )

    @patch("pcapi.routes.offers.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_status(
        self, list_offers_mock, app, db_session
    ):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=user.email)
            .get("/offers?active=false&inactive=false")
        )

        # then
        assert response.status_code == 200
        list_offers_mock.assert_called_once_with(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offerer_id=None,
            venue=None,
            type_id=None,
            offers_per_page=None,
            name_keywords=None,
            page=None,
            exclude_active=True,
            exclude_inactive=True,
        )

    @patch("pcapi.routes.offers.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_offerer_id(
        self, list_offers_mock, app, db_session
    ):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        repository.save(user_offerer, venue)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=user.email)
            .get("/offers?offererId=" + humanize(offerer.id))
        )

        # then
        assert response.status_code == 200
        list_offers_mock.assert_called_once_with(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offerer_id=offerer.id,
            venue=None,
            type_id=None,
            offers_per_page=None,
            name_keywords=None,
            page=None,
            exclude_active=False,
            exclude_inactive=False,
        )


class Returns404:
    def when_requested_venue_does_not_exist(self, app, db_session):
        # Given
        user = create_user(email="user@test.com")
        repository.save(user)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=user.email)
            .get("/offers?venueId=ABC")
        )

        # then
        assert response.status_code == 404
        assert response.json == {"global": ["La page que vous recherchez n'existe pas"]}


class Returns403:
    def when_user_has_no_rights_on_requested_venue(self, app, db_session):
        # Given
        user = create_user(email="user@test.com")
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(user, venue)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=user.email)
            .get(f"/offers?venueId={humanize(venue.id)}")
        )

        # then
        assert response.status_code == 403
        assert response.json == {
            "global": [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
            ]
        }
