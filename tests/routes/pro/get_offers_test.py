import secrets
from unittest.mock import patch

from pcapi.core import testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Returns200Test:
    def should_filter_by_venue_when_user_is_admin_and_request_specific_venue_with_no_rights_on_it(
        self, app, db_session, assert_num_queries
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offers_factories.OffererFactory(name="My Offerer")
        departement_code = "12"
        requested_venue = offers_factories.VenueFactory(
            managingOfferer=offerer,
            siret="12345678912345",
            postalCode=departement_code + "000",
            name="My Venue",
            publicName="My public name",
        )
        other_venue = offers_factories.VenueFactory(managingOfferer=offerer, siret="54321987654321")
        offer_on_requested_venue = offers_factories.ThingOfferFactory(
            venue=requested_venue, extraData={"isbn": "123456789"}, name="My Offer"
        )
        offers_factories.ThingOfferFactory(venue=other_venue)
        stock = offers_factories.StockFactory(offer=offer_on_requested_venue)
        client = TestClient(app.test_client()).with_auth(email=admin.email)
        path = f"/offers?venueId={humanize(requested_venue.id)}"
        select_offers_nb_queries = 1

        # when
        with assert_num_queries(testing.AUTHENTICATION_QUERIES + select_offers_nb_queries):
            response = client.get(path)

        # then
        assert response.status_code == 200
        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": humanize(offer_on_requested_venue.id),
                "isActive": True,
                "isEditable": True,
                "isEvent": False,
                "isThing": True,
                "productIsbn": "123456789",
                "name": "My Offer",
                "status": "ACTIVE",
                "stocks": [
                    {
                        "id": humanize(stock.id),
                        "offerId": humanize(offer_on_requested_venue.id),
                        "hasBookingLimitDatetimePassed": False,
                        "remainingQuantity": 1000,
                        "beginningDatetime": None,
                    }
                ],
                "thumbUrl": None,
                "type": "ThingType.AUDIOVISUEL",
                "subcategoryId": "SUPPORT_PHYSIQUE_FILM",
                "venue": {
                    "departementCode": departement_code,
                    "id": humanize(requested_venue.id),
                    "isVirtual": False,
                    "managingOffererId": humanize(offerer.id),
                    "name": "My Venue",
                    "offererName": "My Offerer",
                    "publicName": "My public name",
                },
                "venueId": humanize(requested_venue.id),
            }
        ]

    def should_filter_by_venue_when_user_is_not_admin_and_request_specific_venue_with_rights_on_it(
        self, app, db_session
    ):
        # Given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)
        requested_venue = offers_factories.VenueFactory(managingOfferer=offerer, siret="12345678912345")
        other_venue = offers_factories.VenueFactory(managingOfferer=offerer, siret="54321987654321")
        offers_factories.ThingOfferFactory(venue=requested_venue)
        offers_factories.ThingOfferFactory(venue=other_venue)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=pro.email)
            .get(f"/offers?venueId={humanize(requested_venue.id)}")
        )

        # then
        offers = response.json
        assert response.status_code == 200
        assert len(offers) == 1

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_venue_id(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = TestClient(app.test_client()).with_auth(email=pro.email).get("/offers?venueId=" + humanize(venue.id))

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            offerer_id=None,
            venue_id=venue.id,
            type_id=None,
            name_keywords_or_isbn=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_status(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = TestClient(app.test_client()).with_auth(email=pro.email).get("/offers?status=active")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            offerer_id=None,
            venue_id=None,
            type_id=None,
            name_keywords_or_isbn=None,
            period_beginning_date=None,
            period_ending_date=None,
            status="active",
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_offerer_id(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = (
            TestClient(app.test_client()).with_auth(email=pro.email).get("/offers?offererId=" + humanize(offerer.id))
        )

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            offerer_id=offerer.id,
            venue_id=None,
            type_id=None,
            name_keywords_or_isbn=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def should_filter_offers_by_given_creation_mode(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = TestClient(app.test_client()).with_auth(email=pro.email).get("/offers?creationMode=imported")

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            offerer_id=None,
            venue_id=None,
            type_id=None,
            name_keywords_or_isbn=None,
            period_beginning_date=None,
            period_ending_date=None,
            status=None,
            creation_mode="imported",
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_period_beginning_date(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=pro.email)
            .get("/offers?periodBeginningDate=2020-10-11T00:00:00Z")
        )

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            offerer_id=None,
            venue_id=None,
            type_id=None,
            name_keywords_or_isbn=None,
            period_beginning_date="2020-10-11T00:00:00Z",
            period_ending_date=None,
            status=None,
            creation_mode=None,
        )

    @patch("pcapi.routes.pro.offers.offers_api.list_offers_for_pro_user")
    def test_results_are_filtered_by_given_period_ending_date(self, mocked_list_offers, app, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        response = (
            TestClient(app.test_client())
            .with_auth(email=pro.email)
            .get("/offers?periodEndingDate=2020-10-11T23:59:59Z")
        )

        # then
        assert response.status_code == 200
        mocked_list_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.isAdmin,
            offerer_id=None,
            venue_id=None,
            type_id=None,
            name_keywords_or_isbn=None,
            period_beginning_date=None,
            period_ending_date="2020-10-11T23:59:59Z",
            status=None,
            creation_mode=None,
        )


class Returns404Test:
    def when_requested_venue_does_not_exist(self, app, db_session):
        # Given
        pro = users_factories.ProFactory()

        # when
        response = TestClient(app.test_client()).with_auth(email=pro.email).get("/offers?venueId=ABC")

        # then
        assert response.status_code == 404
        assert response.json == {"global": ["La page que vous recherchez n'existe pas"]}

    def should_return_no_offers_when_user_has_no_rights_on_requested_venue(self, app, db_session):
        # Given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        venue = offers_factories.VenueFactory(managingOfferer=offerer)

        # when
        response = TestClient(app.test_client()).with_auth(email=pro.email).get(f"/offers?venueId={humanize(venue.id)}")

        # then
        assert response.status_code == 200
        assert response.json == []

    def should_return_no_offers_when_user_offerer_is_not_validated(self, app, db_session):
        # Given
        pro = users_factories.ProFactory()
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro, offerer=offerer, validationToken=secrets.token_urlsafe(20))
        venue = offers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.ThingOfferFactory(venue=venue)

        # when
        response = TestClient(app.test_client()).with_auth(email=pro.email).get(f"/offers?venueId={humanize(venue.id)}")

        # then
        assert response.status_code == 200
        assert response.json == []
