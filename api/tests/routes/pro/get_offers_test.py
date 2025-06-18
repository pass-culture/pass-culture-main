import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models.offer_mixin import OfferStatus


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    number_of_queries = testing.AUTHENTICATION_QUERIES
    number_of_queries += 1  # search offers
    number_of_queries += 1  # FF WIP_REFACTO_FUTURE_OFFER

    def should_filter_by_venue_when_user_is_not_admin_and_request_specific_venue_with_rights_on_it(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        requested_venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="12345678912345")
        other_venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="54321987654321")
        offers_factories.ThingOfferFactory(venue=requested_venue)
        offers_factories.ThingOfferFactory(venue=other_venue)

        requested_venue_id = requested_venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?venueId={requested_venue_id}")
            assert response.status_code == 200

        offers = response.json
        assert len(offers) == 1

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def should_filter_offers_by_given_venue_id(self, mocked_get_capped_offers, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        venue_id = venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get(f"/offers?venueId={venue_id}")
            assert response.status_code == 200
        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            offers_limit=101,
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
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get("/offers?status=ACTIVE")
            assert response.status_code == 200

        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            offers_limit=101,
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
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)

        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get(f"/offers?offererId={offerer_id}")
            assert response.status_code == 200

        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=offerer_id,
            offers_limit=101,
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
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get("/offers?creationMode=imported")
            assert response.status_code == 200

        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            offers_limit=101,
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
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get("/offers?periodBeginningDate=2020-10-11")
            assert response.status_code == 200

        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            offers_limit=101,
            venue_id=None,
            category_id=None,
            name_keywords_or_ean=None,
            period_beginning_date=datetime.date(2020, 10, 11),
            period_ending_date=None,
            status=None,
            creation_mode=None,
            offerer_address_id=None,
        )

    @pytest.mark.parametrize("dp", ["974", "971"])
    def should_consider_the_offer_oa_timezone_for_begining_period(self, dp, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="75")
        oa = offerers_factories.OffererAddressFactory(address__departmentCode=dp)

        offer = offers_factories.ThingOfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id, venue=venue, offererAddress=oa
        )

        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.datetime(2024, 10, 10, 00, 00))
        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)

        response = authenticated_client.get(f"/offers?offererId={offerer_id}&periodBeginningDate=2024-10-10")

        if dp == "974":
            assert response.json[0]["stocks"][0]["beginningDatetime"] == "2024-10-10T00:00:00Z"
        else:
            assert response.json == []

    @pytest.mark.parametrize("dp", ["974", "971"])
    def should_consider_the_offer_oa_timezone_for_ending_period(self, dp, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="75")
        oa = offerers_factories.OffererAddressFactory(address__departmentCode=dp)

        offer = offers_factories.ThingOfferFactory(
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id, venue=venue, offererAddress=oa
        )

        offers_factories.EventStockFactory(offer=offer, beginningDatetime=datetime.datetime(2024, 10, 10, 00, 00))
        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)

        response = authenticated_client.get(f"/offers?offererId={offerer_id}&periodEndingDate=2024-10-9")

        if dp == "971":
            assert response.json[0]["stocks"][0]["beginningDatetime"] == "2024-10-10T00:00:00Z"
        else:
            assert response.json == []

    @patch("pcapi.routes.pro.offers.offers_repository.get_capped_offers_for_filters")
    def test_results_are_filtered_by_given_period_ending_date(self, mocked_get_capped_offers, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get("/offers?periodEndingDate=2020-10-11")
            assert response.status_code == 200

        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            offers_limit=101,
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
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        authenticated_client = client.with_session_auth(email=pro.email)
        # -2 due to mocking
        with testing.assert_num_queries(self.number_of_queries - 2):
            response = authenticated_client.get("/offers?categoryId=LIVRE")
            assert response.status_code == 200

        mocked_get_capped_offers.assert_called_once_with(
            user_id=pro.id,
            user_is_admin=pro.has_admin_role,
            offerer_id=None,
            offers_limit=101,
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
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            offererAddress=offerer_address1,
            publicationDatetime=datetime.datetime(2022, 10, 21, 13, 19),
            bookingAllowedDatetime=datetime.datetime(2022, 11, 21, 13, 19),
        )
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer,
            beginningDatetime=datetime.datetime(2022, 9, 21, 13, 19),
            dnBookedQuantity=50,
        )
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get("/offers")
            assert response.status_code == 200

        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": True,
                "id": event_offer.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isHeadlineOffer": False,
                "isEvent": True,
                "isThing": False,
                "isEducational": False,
                "name": event_offer.name,
                "stocks": [
                    {
                        "id": event_stock.id,
                        "hasBookingLimitDatetimePassed": True,
                        "remainingQuantity": 950,
                        "beginningDatetime": "2022-09-21T13:19:00Z",
                        "bookingQuantity": 50,
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
                    "departmentCode": "75",
                    "id": offerer_address1.address.id,
                    "id_oa": offerer_address1.id,
                    "inseeCode": "75112",
                    "isLinkedToVenue": False,
                    "isManualEdition": False,
                    "label": offerer_address1.label,
                    "latitude": 48.87055,
                    "longitude": 2.34765,
                    "postalCode": "75002",
                    "street": "8 Boulevard de Bercy",
                },
                "publicationDatetime": "2022-10-21T13:19:00Z",
                "bookingAllowedDatetime": "2022-11-21T13:19:00Z",
                "bookingsCount": 50,
            }
        ]

    def test_list_draft_offers_should_not_blindly_return_venue_offerer_address(self, client):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)

        offerer_address1 = offerers_factories.OffererAddressFactory(
            label="Accor Arena",
            offerer=offerer,
            address__street="8 Boulevard de Bercy",
            address__banId="75112_0877_00008",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, offererAddress=offerer_address1)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue, offererAddress=None, validation=OfferValidationStatus.DRAFT
        )
        event_stock = offers_factories.EventStockFactory(
            offer=event_offer, beginningDatetime=datetime.datetime(2022, 9, 21, 13, 19)
        )
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries - 1):  # FF WIP_REFACTO_FUTURE_OFFER
            response = authenticated_client.get("/offers")
            assert response.status_code == 200

        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": True,
                "id": event_offer.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isHeadlineOffer": False,
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
                "status": "DRAFT",
                "isShowcase": False,
                "address": None,
                "publicationDatetime": None,
                "bookingAllowedDatetime": None,
                "bookingsCount": 0,
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
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get("/offers")
            assert response.status_code == 200

        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isEvent": True,
                "isHeadlineOffer": False,
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
                    "departmentCode": "75",
                    "id": venue.offererAddress.address.id,
                    "id_oa": venue.offererAddress.id,
                    "inseeCode": "75102",
                    "isLinkedToVenue": True,
                    "isManualEdition": False,
                    "label": venue.common_name,
                    "latitude": 48.87004,
                    "longitude": 2.3785,
                    "postalCode": "75002",
                    "street": "1 boulevard Poissonnière",
                },
                "publicationDatetime": None,
                "bookingAllowedDatetime": None,
                "bookingsCount": 0,
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
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?offererAddressId={offerer_address1_id}")
            assert response.status_code == 200

        assert len(response.json) == 2
        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer2.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isEducational": False,
                "isEvent": True,
                "isHeadlineOffer": False,
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
                    "id_oa": offerer_address1.id,
                    "banId": "75112_0877_00008",
                    "inseeCode": "75112",
                    "label": "Accor Arena",
                    "street": "8 Boulevard de Bercy",
                    "postalCode": "75002",
                    "city": "Paris",
                    "departmentCode": "75",
                    "isLinkedToVenue": False,
                    "isManualEdition": False,
                    "latitude": 48.87055,
                    "longitude": 2.34765,
                },
                "publicationDatetime": None,
                "bookingAllowedDatetime": None,
                "bookingsCount": 0,
            },
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer1.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isEducational": False,
                "isHeadlineOffer": False,
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
                    "id_oa": offerer_address1.id,
                    "banId": "75112_0877_00008",
                    "inseeCode": "75112",
                    "label": "Accor Arena",
                    "street": "8 Boulevard de Bercy",
                    "postalCode": "75002",
                    "city": "Paris",
                    "departmentCode": "75",
                    "isLinkedToVenue": False,
                    "isManualEdition": False,
                    "latitude": 48.87055,
                    "longitude": 2.34765,
                },
                "publicationDatetime": None,
                "bookingAllowedDatetime": None,
                "bookingsCount": 0,
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
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?offererId={offerer_id}")
            assert response.status_code == 200

        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer1.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isEvent": True,
                "isHeadlineOffer": False,
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
                    "id_oa": offerer_address1.id,
                    "banId": "75112_0877_00008",
                    "inseeCode": "75112",
                    "label": offerer_address1.label,
                    "street": "8 Boulevard de Bercy",
                    "postalCode": "75002",
                    "city": "Paris",
                    "departmentCode": "75",
                    "isLinkedToVenue": False,
                    "isManualEdition": False,
                    "latitude": 48.87055,
                    "longitude": 2.34765,
                },
                "publicationDatetime": None,
                "bookingAllowedDatetime": None,
                "bookingsCount": 0,
            }
        ]

    def should_return_offer_with_address_of_venue(self, client, db_session):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerer_address1 = offerers_factories.OffererAddressOfVenueFactory(
            offerer=offerer,
            address__street="4 Boulevard de Bercy",
            address__banId="75112_0877_00001",
            address__postalCode="75001",
            address__longitude=1.34765,
            address__latitude=4.34765,
        )
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, offererAddress=offerer_address1, name="Best Place to be"
        )

        event_offer1 = offers_factories.EventOfferFactory(
            name="The Weeknd", subcategoryId=subcategories.CONCERT.id, venue=venue, offererAddress=None
        )
        offerer_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get(f"/offers?offererId={offerer_id}")
            assert response.status_code == 200
        assert response.json == [
            {
                "hasBookingLimitDatetimesPassed": False,
                "id": event_offer1.id,
                "isActive": True,
                "isDigital": False,
                "isEditable": True,
                "isEvent": True,
                "isHeadlineOffer": False,
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
                    "id_oa": offerer_address1.id,
                    "banId": "75112_0877_00001",
                    "inseeCode": "75112",
                    "label": venue.common_name,
                    "street": "4 Boulevard de Bercy",
                    "postalCode": "75001",
                    "city": "Paris",
                    "departmentCode": "75",
                    "isLinkedToVenue": True,
                    "isManualEdition": False,
                    "latitude": 4.34765,
                    "longitude": 1.34765,
                },
                "publicationDatetime": None,
                "bookingAllowedDatetime": None,
                "bookingsCount": 0,
            }
        ]

    def should_return_no_offers_when_user_has_no_rights_on_requested_venue(self, client, db_session):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        venue_id = venue.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries - 1):  # -1 sur FF WIP_REFACTO_FUTURE_OFFER
            response = authenticated_client.get(f"/offers?venueId={venue_id}")
            assert response.status_code == 200

        assert response.json == []

    def should_return_no_offers_when_user_offerer_is_not_validated(self, client, db_session):
        pro = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.NewUserOffererFactory(user=pro, offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offers_factories.ThingOfferFactory(venue=venue)

        venue_id = offerer.id
        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries - 1):  # -1 sur FF WIP_REFACTO_FUTURE_OFFER
            response = authenticated_client.get(f"/offers?venueId={venue_id}")
            assert response.status_code == 200

        assert response.json == []


class Returns400Test:
    number_of_queries = testing.AUTHENTICATION_QUERIES

    def should_return_error_if_status_is_not_valid(self, client, db_session):
        pro = users_factories.ProFactory()

        authenticated_client = client.with_session_auth(email=pro.email)
        with testing.assert_num_queries(self.number_of_queries):
            response = authenticated_client.get("/offers?status=NOPENOPENOPE")
            assert response.status_code == 400

        msg = response.json["status"][0]
        assert msg.startswith("value is not a valid enumeration member")

        for value in OfferStatus:
            assert value.name in msg
