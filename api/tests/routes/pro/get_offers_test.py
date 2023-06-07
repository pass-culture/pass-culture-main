from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_no_duplicated_queries
import pcapi.core.users.factories as users_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    def should_filter_by_venue_when_user_is_admin_and_request_specific_venue_with_no_rights_on_it(self, client):
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.OffererFactory(name="My Offerer")
        departement_code = "12"
        requested_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            siret="12345678912345",
            postalCode=departement_code + "000",
            name="My Venue",
            publicName="My public name",
        )
        other_venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="54321987654321")
        offer_on_requested_venue = offers_factories.ThingOfferFactory(
            venue=requested_venue, extraData={"ean": "123456789"}, name="My Offer"
        )
        offers_factories.ThingOfferFactory(venue=other_venue)
        stock = offers_factories.StockFactory(offer=offer_on_requested_venue)

        client = client.with_session_auth(email=admin.email)
        with assert_no_duplicated_queries():
            response = client.get(f"/offers?venueId={requested_venue.id}")

        assert response.status_code == 200
        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "nonHumanizedId": offer_on_requested_venue.id,
                "isActive": True,
                "isEditable": True,
                "isEvent": False,
                "isThing": True,
                "isEducational": False,
                "productIsbn": "123456789",
                "name": "My Offer",
                "status": "ACTIVE",
                "stocks": [
                    {
                        "hasBookingLimitDatetimePassed": False,
                        "nonHumanizedId": stock.id,
                        "remainingQuantity": 1000,
                        "beginningDatetime": None,
                        "bookingQuantity": 0,
                    }
                ],
                "thumbUrl": None,
                "subcategoryId": "SUPPORT_PHYSIQUE_FILM",
                "venue": {
                    "departementCode": departement_code,
                    "nonHumanizedId": requested_venue.id,
                    "isVirtual": False,
                    "name": "My Venue",
                    "offererName": "My Offerer",
                    "publicName": "My public name",
                },
                "isShowcase": False,
            }
        ]

    def should_filter_by_venue_when_user_is_not_admin_and_request_specific_venue_with_rights_on_it(self, client):
        # Given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        requested_venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678912345")
        other_venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="54321987654321")
        offers_factories.ThingOfferFactory(venue=requested_venue)
        offers_factories.ThingOfferFactory(venue=other_venue)

        # when
        response = client.with_session_auth(email=pro.email).get(f"/offers?venueId={requested_venue.id}")

        # then
        offers = response.json
        assert response.status_code == 200
        assert len(offers) == 1

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_venue_id(self, mocked_list_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = client.with_session_auth(email=pro.email).get(f"/offers?venueId={venue.id}")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            venue_id=venue.id,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_status(self, mocked_list_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = client.with_session_auth(email=pro.email).get("/offers?status=active")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            venue_id=None,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date=None,
            period_ending_date=None,
            status="active",
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_offerer_id(self, mocked_list_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = client.with_session_auth(email=pro.email).get(f"/offers?offererId={offerer.id}")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=offerer.id,
            venue_id=None,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_creation_mode(self, mocked_list_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = client.with_session_auth(email=pro.email).get("/offers?creationMode=imported")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            venue_id=None,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode="imported",
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_period_beginning_date(self, mocked_list_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = client.with_session_auth(email=pro.email).get("/offers?periodBeginningDate=2020-10-11T00:00:00Z")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            venue_id=None,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date="2020-10-11T00:00:00Z",
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_period_ending_date(self, mocked_list_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = client.with_session_auth(email=pro.email).get("/offers?periodEndingDate=2020-10-11T23:59:59Z")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            venue_id=None,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date=None,
            period_ending_date="2020-10-11T23:59:59Z",
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_category_id(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = TestClient(app.test_client()).with_session_auth(email=pro.email).get("/offers?categoryId=LIVRE")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            venue_id=None,
            category_id="LIVRE",
            name_keywords_or_ean=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )


class Returns404Test:
    def should_return_no_offers_when_user_has_no_rights_on_requested_venue(self, app, db_session):
        # Given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = TestClient(app.test_client()).with_session_auth(email=pro.email).get(f"/offers?venueId={venue.id}")

        # then
        assert response.status_code == 200
        assert response.json == []

    def should_return_no_offers_when_user_offerer_is_not_validated(self, app, db_session):
        # Given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.NotValidatedUserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.ThingOfferFactory(venue=venue)

        # when
        response = TestClient(app.test_client()).with_session_auth(email=pro.email).get(f"/offers?venueId={venue.id}")

        # then
        assert response.status_code == 200
        assert response.json == []
