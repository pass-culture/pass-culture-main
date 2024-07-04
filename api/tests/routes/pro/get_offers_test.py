import datetime
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories
from pcapi.models.offer_mixin import OfferStatus


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    # session
    # user
    # search
    number_of_queries = 3

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
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            venue=requested_venue,
            extraData={"ean": "123456789"},
            name="My Offer",
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
                    "id": offer_on_requested_venue.id,
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
                            "id": stock.id,
                            "remainingQuantity": 1000,
                            "beginningDatetime": None,
                            "bookingQuantity": 0,
                        }
                    ],
                    "thumbUrl": None,
                    "subcategoryId": "SUPPORT_PHYSIQUE_FILM",
                    "venue": {
                        "departementCode": departement_code,
                        "id": requested_venue.id,
                        "isVirtual": False,
                        "name": "My Venue",
                        "offererName": "My Offerer",
                        "publicName": "My public name",
                    },
                    "isShowcase": False,
                    "address": {
                        "banId": "75102_7560_00001",
                        "city": "Paris",
                        "id": requested_venue.offererAddress.address.id,
                        "inseeCode": "75102",
                        "isEditable": False,
                        "label": "My public name",  # considering the venue.common_name
                        "latitude": 48.87004,
                        "longitude": 2.3785,
                        "postalCode": "12000",
                        "street": "1 boulevard Poissonnière",
                    },
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
        requested_venue_id = requested_venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?venueId={requested_venue_id}")

            # then
            offers = response.json
            assert response.status_code == 200
            assert len(offers) == 1

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def should_filter_offers_by_given_venue_id(self, mocked_get_capped_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        # when
        venue_id = venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?venueId={venue_id}")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=None,
                offers_limit=501,
                venue_id=venue.id,
                category_id=None,
                name_keywords_or_ean=None,
                period_beginning_date=None,
                period_ending_date=None,
                status=None,
                creation_mode=None,
                offerer_address_id=None,
            )

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def should_filter_offers_by_given_status(self, mocked_get_capped_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        authenticated_client = client.with_session_auth(email=pro.email)
        # -1 due to mocking
        with assert_num_queries(self.number_of_queries - 1):
            response = authenticated_client.get("/offers?status=ACTIVE")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=None,
                offers_limit=501,
                venue_id=None,
                category_id=None,
                name_keywords_or_ean=None,
                period_beginning_date=None,
                period_ending_date=None,
                status=OfferStatus.ACTIVE,
                creation_mode=None,
                offerer_address_id=None,
            )

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def should_filter_offers_by_given_offerer_id(self, mocked_get_capped_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        # when
        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        # -1 due to mocking
        with assert_num_queries(self.number_of_queries - 1):
            response = authenticated_client.get(f"/offers?offererId={offerer_id}")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=offerer_id,
                offers_limit=501,
                venue_id=None,
                category_id=None,
                name_keywords_or_ean=None,
                period_beginning_date=None,
                period_ending_date=None,
                status=None,
                creation_mode=None,
                offerer_address_id=None,
            )

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def should_filter_offers_by_given_creation_mode(self, mocked_get_capped_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        authenticated_client = client.with_session_auth(email=pro.email)
        # -1 due to mocking
        with assert_num_queries(self.number_of_queries - 1):
            response = authenticated_client.get("/offers?creationMode=imported")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=None,
                offers_limit=501,
                venue_id=None,
                category_id=None,
                name_keywords_or_ean=None,
                period_beginning_date=None,
                period_ending_date=None,
                status=None,
                creation_mode="imported",
                offerer_address_id=None,
            )

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def test_results_are_filtered_by_given_period_beginning_date(self, mocked_get_capped_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        authenticated_client = client.with_session_auth(email=pro.email)
        # -1 due to mocking
        with assert_num_queries(self.number_of_queries - 1):
            response = authenticated_client.get("/offers?periodBeginningDate=2020-10-11")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=None,
                offers_limit=501,
                venue_id=None,
                category_id=None,
                name_keywords_or_ean=None,
                period_beginning_date=datetime.date(2020, 10, 11),
                period_ending_date=None,
                status=None,
                creation_mode=None,
                offerer_address_id=None,
            )

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def test_results_are_filtered_by_given_period_ending_date(self, mocked_get_capped_offers, client):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        authenticated_client = client.with_session_auth(email=pro.email)
        # -1 due to mocking
        with assert_num_queries(self.number_of_queries - 1):
            response = authenticated_client.get("/offers?periodEndingDate=2020-10-11")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=None,
                offers_limit=501,
                venue_id=None,
                category_id=None,
                name_keywords_or_ean=None,
                period_beginning_date=None,
                period_ending_date=datetime.date(2020, 10, 11),
                status=None,
                creation_mode=None,
                offerer_address_id=None,
            )

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def should_filter_offers_by_given_category_id(self, mocked_get_capped_offers, client, db_session):
        # given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        # when
        authenticated_client = client.with_session_auth(email=pro.email)
        # -1 due to mocking
        with assert_num_queries(self.number_of_queries - 1):
            response = authenticated_client.get("/offers?categoryId=LIVRE")

            # then
            assert response.status_code == 200
            mocked_get_capped_offers.assert_called_once_with(
                user_id=pro.id,
                user_is_admin=pro.has_admin_role,
                offerer_id=None,
                offers_limit=501,
                venue_id=None,
                category_id="LIVRE",
                name_keywords_or_ean=None,
                period_beginning_date=None,
                period_ending_date=None,
                status=None,
                creation_mode=None,
                offerer_address_id=None,
            )

    def should_return_event_correctly_serialized(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        offerer_address1 = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="8 Boulevard de Bercy",
            address__banId="75112_0877_00008",
        )
        event_offer = offers_factories.EventOfferFactory(venue=venue, offererAddress=offerer_address1)
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer, beginningDatetime=datetime.datetime(2022, 9, 21, 13, 19)
        )
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get("/offers")

            assert response.status_code == 200
            assert response.json == [
                {
                    "hasBookingLimitDatetimesPassed": True,
                    "id": event_offer.id,
                    "isActive": True,
                    "isEditable": True,
                    "isEvent": True,
                    "isThing": False,
                    "isEducational": False,
                    "name": event_offer.name,
                    "stocks": [
                        {
                            "id": event_stock.id,
                            "hasBookingLimitDatetimePassed": True,
                            "remainingQuantity": 1000,
                            "beginningDatetime": "2022-09-21T13:19:00Z",
                            "bookingQuantity": 0,
                        }
                    ],
                    "thumbUrl": None,
                    "productIsbn": None,
                    "subcategoryId": "SEANCE_CINE",
                    "venue": {
                        "id": venue.id,
                        "isVirtual": False,
                        "name": venue.name,
                        "offererName": venue.managingOfferer.name,
                        "publicName": venue.publicName,
                        "departementCode": "75",
                    },
                    "status": "EXPIRED",
                    "isShowcase": False,
                    "address": {
                        "banId": "75112_0877_00008",
                        "city": "Paris",
                        "id": offerer_address1.address.id,
                        "inseeCode": "75112",
                        "isEditable": True,
                        "label": "Accor Arena",
                        "latitude": 48.87055,
                        "longitude": 2.34765,
                        "postalCode": "75002",
                        "street": "8 Boulevard de Bercy",
                    },
                }
            ]

    def should_not_return_soft_deleted_stocks(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        event_offer = offers_factories.EventOfferFactory(venue=venue)

        offers_factories.EventStockFactory(
            offer=event_offer, beginningDatetime=datetime.datetime(2022, 9, 21, 13, 19), isSoftDeleted=True
        )
        offers_factories.EventStockFactory(
            offer=event_offer, beginningDatetime=datetime.datetime(2022, 9, 22, 13, 19), isSoftDeleted=True
        )
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get("/offers")

            assert response.status_code == 200
            assert response.json == [
                {
                    "hasBookingLimitDatetimesPassed": False,
                    "id": event_offer.id,
                    "isActive": True,
                    "isEditable": True,
                    "isEvent": True,
                    "isThing": False,
                    "isEducational": False,
                    "name": event_offer.name,
                    "stocks": [],
                    "thumbUrl": None,
                    "productIsbn": None,
                    "subcategoryId": "SEANCE_CINE",
                    "venue": {
                        "id": venue.id,
                        "isVirtual": False,
                        "name": venue.name,
                        "offererName": venue.managingOfferer.name,
                        "publicName": venue.publicName,
                        "departementCode": "75",
                    },
                    "status": "SOLD_OUT",
                    "isShowcase": False,
                    "address": {
                        "banId": "75102_7560_00001",
                        "city": "Paris",
                        "id": venue.offererAddress.address.id,
                        "inseeCode": "75102",
                        "isEditable": False,
                        "label": venue.publicName,
                        "latitude": 48.87004,
                        "longitude": 2.3785,
                        "postalCode": "75000",
                        "street": "1 boulevard Poissonnière",
                    },
                }
            ]

    def should_return_offers_filtered_by_offerer_address(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerer_address1 = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="8 Boulevard de Bercy",
            address__banId="75112_0877_00008",
        )

        event_offer1 = offers_factories.EventOfferFactory(
            name="The Weeknd", subcategoryId=subcategories.CONCERT.id, venue=venue, offererAddress=offerer_address1
        )
        event_offer2 = offers_factories.EventOfferFactory(
            name="Taylor Swift", subcategoryId=subcategories.CONCERT.id, venue=venue, offererAddress=offerer_address1
        )

        offerer_address2 = offerers_factories.OffererAddressFactory(
            label="La Cigale",
            offerer=offerer,
            address__street="120 Boulevard Marguerite de Rochechouart",
            address__banId="75118_8288_00120",
        )

        event_offer3 = offers_factories.EventOfferFactory(
            name="Philippine Lavrey",
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            offererAddress=offerer_address2,
        )
        offers_factories.EventStockFactory(offer=event_offer3)
        offerer_address1_id = offerer_address1.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?offererAddressId={offerer_address1_id}")

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer2.id,
                "isActive": True,
                "isEditable": True,
                "isEducational": False,
                "isEvent": True,
                "isShowcase": False,
                "isThing": False,
                "name": event_offer2.name,
                "productIsbn": None,
                "status": "SOLD_OUT",
                "stocks": [],
                "subcategoryId": "CONCERT",
                "thumbUrl": None,
                "venue": {
                    "id": venue.id,
                    "isVirtual": False,
                    "name": venue.name,
                    "offererName": venue.managingOfferer.name,
                    "publicName": venue.publicName,
                    "departementCode": "75",
                },
                "address": {
                    "id": offerer_address1.address.id,
                    "banId": "75112_0877_00008",
                    "inseeCode": "75112",
                    "label": "Accor Arena",
                    "street": "8 Boulevard de Bercy",
                    "postalCode": "75002",
                    "city": "Paris",
                    "isEditable": True,
                    "latitude": 48.87055,
                    "longitude": 2.34765,
                },
            },
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer1.id,
                "isActive": True,
                "isEditable": True,
                "isEducational": False,
                "isEvent": True,
                "isShowcase": False,
                "isThing": False,
                "name": event_offer1.name,
                "productIsbn": None,
                "status": "SOLD_OUT",
                "stocks": [],
                "subcategoryId": "CONCERT",
                "thumbUrl": None,
                "venue": {
                    "id": venue.id,
                    "isVirtual": False,
                    "name": venue.name,
                    "offererName": venue.managingOfferer.name,
                    "publicName": venue.publicName,
                    "departementCode": "75",
                },
                "address": {
                    "id": offerer_address1.address.id,
                    "banId": "75112_0877_00008",
                    "inseeCode": "75112",
                    "label": "Accor Arena",
                    "street": "8 Boulevard de Bercy",
                    "postalCode": "75002",
                    "city": "Paris",
                    "isEditable": True,
                    "latitude": 48.87055,
                    "longitude": 2.34765,
                },
            },
        ]

    def should_return_offer_with_address_of_oa(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offerer_address1 = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="8 Boulevard de Bercy",
            address__banId="75112_0877_00008",
        )

        event_offer1 = offers_factories.EventOfferFactory(
            name="The Weeknd", subcategoryId=subcategories.CONCERT.id, venue=venue, offererAddress=offerer_address1
        )

        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?offererId={offerer_id}")
            assert response.status_code == 200
            assert response.json == [
                {
                    "hasBookingLimitDatetimesPassed": False,
                    "id": event_offer1.id,
                    "isActive": True,
                    "isEditable": True,
                    "isEvent": True,
                    "isThing": False,
                    "isEducational": False,
                    "name": "The Weeknd",
                    "stocks": [],
                    "thumbUrl": None,
                    "productIsbn": None,
                    "subcategoryId": "CONCERT",
                    "venue": {
                        "id": venue.id,
                        "isVirtual": False,
                        "name": venue.name,
                        "offererName": venue.managingOfferer.name,
                        "publicName": venue.publicName,
                        "departementCode": "75",
                    },
                    "status": "SOLD_OUT",
                    "isShowcase": False,
                    "address": {
                        "id": offerer_address1.address.id,
                        "banId": "75112_0877_00008",
                        "inseeCode": "75112",
                        "label": "Accor Arena",
                        "street": "8 Boulevard de Bercy",
                        "postalCode": "75002",
                        "city": "Paris",
                        "isEditable": True,
                        "latitude": 48.87055,
                        "longitude": 2.34765,
                    },
                }
            ]

    def should_return_offer_with_address_of_venue(self, client, db_session):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerer_address1 = offerers_factories.OffererAddressFactory(
            label="Accor Arena 1",
            offerer=offerer,
            address__street="4 Boulevard de Bercy",
            address__banId="75112_0877_00001",
            address__postalCode="75001",
            address__longitude=1.34765,
            address__latitude=4.34765,
        )
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress=offerer_address1)

        event_offer1 = offers_factories.EventOfferFactory(
            name="The Weeknd", subcategoryId=subcategories.CONCERT.id, venue=venue, offererAddress=None
        )
        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?offererId={offerer_id}")
            assert response.status_code == 200
            assert response.json == [
                {
                    "hasBookingLimitDatetimesPassed": False,
                    "id": event_offer1.id,
                    "isActive": True,
                    "isEditable": True,
                    "isEvent": True,
                    "isThing": False,
                    "isEducational": False,
                    "name": "The Weeknd",
                    "stocks": [],
                    "thumbUrl": None,
                    "productIsbn": None,
                    "subcategoryId": "CONCERT",
                    "venue": {
                        "id": venue.id,
                        "isVirtual": False,
                        "name": venue.name,
                        "offererName": venue.managingOfferer.name,
                        "publicName": venue.publicName,
                        "departementCode": "75",
                    },
                    "status": "SOLD_OUT",
                    "isShowcase": False,
                    "address": {
                        "id": offerer_address1.address.id,
                        "banId": "75112_0877_00001",
                        "inseeCode": "75112",
                        "label": "Accor Arena 1",
                        "street": "4 Boulevard de Bercy",
                        "postalCode": "75001",
                        "city": "Paris",
                        "isEditable": False,
                        "latitude": 4.34765,
                        "longitude": 1.34765,
                    },
                }
            ]


class Returns404Test:
    # session
    # user
    # query
    number_of_queries = 3

    def should_return_no_offers_when_user_has_no_rights_on_requested_venue(self, client, db_session):
        # TODO : maybe move this test to another class due to status code
        # Given
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        # when
        venue_id = venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?venueId={venue_id}")

            # then
            assert response.status_code == 200
            assert response.json == []

    def should_return_no_offers_when_user_offerer_is_not_validated(self, client, db_session):
        # TODO : maybe move this test to another class due to status code
        # Given

        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.NotValidatedUserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.ThingOfferFactory(venue=venue)

        # when
        venue_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?venueId={venue_id}")

            # then
            assert response.status_code == 200
            assert response.json == []


class Returns400Test:
    # session
    # user
    number_of_queries = 2

    def should_return_error_if_status_is_not_valid(self, client, db_session):

        # Given
        pro = users_factories.ProFactory()

        # when
        authenticated_client = client.with_session_auth(email=pro.email)
        with assert_num_queries(self.number_of_queries):
            response = authenticated_client.get("/offers?status=NOPENOPENOPE")
            assert response.status_code == 400
            # then
            msg = response.json["status"][0]
            assert msg.startswith("value is not a valid enumeration member")

            for value in OfferStatus:
                assert value.name in msg
