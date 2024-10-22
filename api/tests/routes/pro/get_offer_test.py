from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

from pcapi.core import testing
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    # get user_session
    # get user
    # get offer
    # check user_offerer exists
    num_queries = 4

    def test_access_by_beneficiary(self, client):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory()

        auth_client = client.with_session_auth(email=beneficiary.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory()

        auth_client = client.with_session_auth(email=pro_user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    # session
    # user
    # payload (joined query)
    # user offerer
    # stocks of offer (a backref)
    num_queries = 5

    def test_access_by_pro_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer)
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None,
            venue__longitude=None,
            venue__offererAddress=offerer_address,
            venue__managingOfferer=user_offerer.offerer,
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        response_json = response.json
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert "thumbUrl" in response_json
        assert response_json["id"] == offer.id

    def test_access_even_if_offerer_has_no_siren(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            venue__managingOfferer__siren=None,
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

    def test_returns_an_active_mediation(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        mediation = offers_factories.MediationFactory(offer=offer)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert f"/thumbs/mediations/{humanize(mediation.id)}" in response.json["activeMediation"]["thumbUrl"]

    @time_machine.travel("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, client):
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=now,
            offerer__siren="123456789",
            offerer__name="Test Offerer",
        )
        offer = offers_factories.EventOfferFactory(
            dateCreated=now,
            dateModifiedAtLastProvider=now,
            bookingEmail="offer.booking.email@example.com",
            name="Derrick",
            description="Tatort, but slower",
            durationMinutes=60,
            extraData=None,
            mentalDisabilityCompliant=True,
            externalTicketOfficeUrl="http://example.net",
            withdrawalDetails="Veuillez chercher votre billet au guichet",
            withdrawalType=WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
            venue__siret="12345678912345",
            venue__name="La petite librairie",
            venue__dateCreated=now,
            venue__bookingEmail="test@test.com",
            venue__managingOfferer=user_offerer.offerer,
            offererAddress=None,
        )

        stock = offers_factories.EventStockFactory(
            offer=offer,
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now + timedelta(hours=1),
            bookingLimitDatetime=now + timedelta(hours=1),
            priceCategory__priceCategoryLabel__label="Au pied du mur",
        )
        venue = offer.venue
        offerer = venue.managingOfferer
        finance_factories.BankInformationFactory(venue=venue)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json == {
            "activeMediation": None,
            "bookingContact": None,
            "bookingsCount": 0,
            "bookingEmail": "offer.booking.email@example.com",
            "dateCreated": "2020-10-15T00:00:00Z",
            "productId": None,
            "publicationDate": None,
            "description": "Tatort, but slower",
            "durationMinutes": 60,
            "extraData": None,
            "externalTicketOfficeUrl": "http://example.net",
            "hasBookingLimitDatetimesPassed": False,
            "hasPendingBookings": False,
            "hasStocks": True,
            "isActive": True,
            "isActivable": True,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "isDigital": False,
            "isDuo": False,
            "isEditable": True,
            "isEvent": True,
            "isNational": False,
            "isThing": False,
            "lastProvider": None,
            "name": "Derrick",
            "id": stock.offer.id,
            "status": "ACTIVE",
            "isNonFreeOffer": None,
            "priceCategories": [{"label": "Au pied du mur", "price": 10.1, "id": stock.priceCategoryId}],
            "subcategoryId": "SEANCE_CINE",
            "thumbUrl": None,
            "url": None,
            "address": {
                "label": venue.common_name,
                "id": venue.offererAddress.address.id,
                "id_oa": venue.offererAddress.id,
                "banId": venue.offererAddress.address.banId,
                "departmentCode": venue.offererAddress.address.departmentCode,
                "inseeCode": venue.offererAddress.address.inseeCode,
                "city": venue.offererAddress.address.city,
                "latitude": float(venue.offererAddress.address.latitude),
                "longitude": float(venue.offererAddress.address.longitude),
                "postalCode": venue.offererAddress.address.postalCode,
                "street": venue.offererAddress.address.street,
                "isLinkedToVenue": venue.offererAddress.isLinkedToVenue,
                "isManualEdition": venue.offererAddress.address.isManualEdition,
            },
            "venue": {
                "street": "1 boulevard Poissonnière",
                "audioDisabilityCompliant": False,
                "bookingEmail": "test@test.com",
                "city": "Paris",
                "departementCode": "75",
                "id": venue.id,
                "isVirtual": False,
                "managingOfferer": {
                    "id": offerer.id,
                    "name": "Test Offerer",
                    "allowedOnAdage": offerer.allowedOnAdage,
                },
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "name": "La petite librairie",
                "postalCode": "75002",
                "publicName": "La petite librairie",
                "visualDisabilityCompliant": False,
            },
            "withdrawalDetails": "Veuillez chercher votre billet au guichet",
            "withdrawalType": "on_site",
            "withdrawalDelay": 60 * 30,
        }

    @time_machine.travel("2019-10-15 00:00:00")
    def test_returns_a_thing_stock(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(
            product=product, venue__managingOfferer=user_offerer.offerer, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer)
        offer_id = offer.id

        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert data["subcategoryId"] == "LIVRE_PAPIER"

    def test_returns_a_movie_with_product(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=120)
        offer = offers_factories.OfferFactory(product=product, venue__managingOfferer=user_offerer.offerer)
        offers_factories.EventStockFactory(offer=offer)
        offer_id = offer.id

        client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert data["subcategoryId"] == subcategories.SEANCE_CINE.id

    @time_machine.travel("2019-10-15 00:00:00")
    def test_returns_a_thing_with_activation_code_stock(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            stocks=[offers_factories.StockWithActivationCodesFactory()],
            subcategoryId=subcategories.ABO_PLATEFORME_MUSIQUE.id,
            url="fake-url",
            venue__managingOfferer=user_offerer.offerer,
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        data = response.json
        assert data["subcategoryId"] == "ABO_PLATEFORME_MUSIQUE"
        assert data["hasStocks"] == True

    @time_machine.travel("2020-10-15 00:00:00")
    def test_should_not_return_soft_deleted_stock(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = deleted_stock.offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["hasStocks"] == False

    def test_returns_positive_booking_count(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(offer=offer)
        bookings_factories.BookingFactory.create_batch(2, stock=stock)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["bookingsCount"] == 2
        assert response.json["hasStocks"] == True

    @pytest.mark.parametrize("offer_oa_label", ["label", None, ""])
    def test_return_offer_offerer_address(self, offer_oa_label, client):
        """If offer has an offererAddress, it should be used"""
        user_offerer = offerers_factories.UserOffererFactory()
        venue_offerer_address = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer)
        offer_offerer_address = offerers_factories.OffererAddressFactory(
            offerer=user_offerer.offerer, label=offer_oa_label
        )
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            venue__offererAddress=venue_offerer_address,
            offererAddress=offer_offerer_address,
        )
        assert offer.venue.offererAddress != offer.offererAddress

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["address"] == {
            "label": offer_offerer_address.label,
            "id": offer_offerer_address.address.id,
            "id_oa": offer_offerer_address.id,
            "banId": offer_offerer_address.address.banId,
            "departmentCode": offer_offerer_address.address.departmentCode,
            "inseeCode": offer_offerer_address.address.inseeCode,
            "city": offer_offerer_address.address.city,
            "latitude": float(offer_offerer_address.address.latitude),
            "longitude": float(offer_offerer_address.address.longitude),
            "postalCode": offer_offerer_address.address.postalCode,
            "street": offer_offerer_address.address.street,
            "isLinkedToVenue": offer_offerer_address.isLinkedToVenue,
            "isManualEdition": offer_offerer_address.address.isManualEdition,
        }

    def test_return_venue_offerer_address(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=user_offerer.offerer)
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            venue__offererAddress=offerer_address,
            offererAddress=None,
        )
        assert offer.offererAddress is None

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["address"] == {
            "label": offer.venue.common_name,
            "id": offerer_address.address.id,
            "id_oa": offerer_address.id,
            "banId": offerer_address.address.banId,
            "departmentCode": offerer_address.address.departmentCode,
            "inseeCode": offerer_address.address.inseeCode,
            "city": offerer_address.address.city,
            "latitude": float(offerer_address.address.latitude),
            "longitude": float(offerer_address.address.longitude),
            "postalCode": offerer_address.address.postalCode,
            "street": offerer_address.address.street,
            "isLinkedToVenue": offerer_address.isLinkedToVenue,
            "isManualEdition": offerer_address.address.isManualEdition,
        }

    @time_machine.travel("2020-10-15 00:00:00")
    def test_future_offer(self, client):
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=now,
            offerer__siren="123456789",
            offerer__name="Test Offerer",
        )
        publication_date = now.replace(minute=0, second=0, microsecond=0) + timedelta(days=30)
        offer = offers_factories.EventOfferFactory(
            dateCreated=now,
            dateModifiedAtLastProvider=now,
            bookingEmail="offer.booking.email@example.com",
            name="Derrick",
            description="Tatort, but slower",
            durationMinutes=60,
            extraData=None,
            mentalDisabilityCompliant=True,
            externalTicketOfficeUrl="http://example.net",
            withdrawalDetails="Veuillez chercher votre billet au guichet",
            withdrawalType=WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
            venue__siret="12345678912345",
            venue__name="La petite librairie",
            venue__dateCreated=now,
            venue__bookingEmail="test@test.com",
            venue__managingOfferer=user_offerer.offerer,
            offererAddress=None,
        )
        offer_id = offer.id
        offers_factories.FutureOfferFactory(
            offerId=offer_id,
            publicationDate=publication_date,
        )

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["publicationDate"] == publication_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    @pytest.mark.parametrize("has_pending_bookings", [True, False])
    def test_pending_booking(self, client, has_pending_bookings):
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(offer=offer)
        if has_pending_bookings:
            bookings_factories.BookingFactory(stock=stock)

        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
            assert response.status_code == 200

        assert response.json["hasPendingBookings"] == has_pending_bookings
