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
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_beneficiary(self, client):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        response = client.with_session_auth(email=beneficiary.email).get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, client):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        response = client.with_session_auth(email=pro_user.email).get(f"/offers/{offer.id}")

        # Then
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
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None, venue__longitude=None, venue__managingOfferer=user_offerer.offerer
        )

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")
        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationStatus" not in response_json["venue"]["managingOfferer"]
        assert "thumbUrl" in response_json
        assert response_json["id"] == offer.id

    def test_performance(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.EventStockFactory.create_batch(5, offer=offer)

        # When
        client.with_session_auth(email=user_offerer.user.email)

        with testing.assert_no_duplicated_queries():
            client.get(f"/offers/{offer.id}")

    def test_access_even_if_offerer_has_no_siren(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            venue__managingOfferer__siren=None,
        )

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")

        # Then
        assert response.status_code == 200

    def test_returns_an_active_mediation(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        mediation = offers_factories.MediationFactory(offer=offer)

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        assert f"/thumbs/mediations/{humanize(mediation.id)}" in response.json["activeMediation"]["thumbUrl"]

    @time_machine.travel("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, client):
        # Given
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
        offer = stock.offer
        venue = offer.venue
        offerer = venue.managingOfferer
        finance_factories.BankInformationFactory(venue=venue)

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "activeMediation": None,
            "bookingContact": None,
            "bookingsCount": 0,
            "bookingEmail": "offer.booking.email@example.com",
            "dateCreated": "2020-10-15T00:00:00Z",
            "description": "Tatort, but slower",
            "durationMinutes": 60,
            "extraData": None,
            "externalTicketOfficeUrl": "http://example.net",
            "hasBookingLimitDatetimesPassed": False,
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
                "postalCode": "75000",
                "publicName": "La petite librairie",
                "visualDisabilityCompliant": False,
            },
            "withdrawalDetails": "Veuillez chercher votre billet au guichet",
            "withdrawalType": "on_site",
            "withdrawalDelay": 60 * 30,
        }

    @time_machine.travel("2019-10-15 00:00:00")
    def test_returns_a_thing_stock(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        stock = offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        offer = stock.offer
        offer.subcategoryId = subcategories.LIVRE_PAPIER.id
        repository.save(offer)

        # When
        response = client.with_session_auth(email=user_offerer.user.email).get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["subcategoryId"] == "LIVRE_PAPIER"

    @time_machine.travel("2019-10-15 00:00:00")
    def test_returns_a_thing_with_activation_code_stock(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            stocks=[offers_factories.StockWithActivationCodesFactory()],
            subcategoryId=subcategories.ABO_PLATEFORME_MUSIQUE.id,
            url="fake-url",
            venue__managingOfferer=user_offerer.offerer,
        )

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["subcategoryId"] == "ABO_PLATEFORME_MUSIQUE"
        assert data["hasStocks"] == True

    @time_machine.travel("2020-10-15 00:00:00")
    def test_should_not_return_soft_deleted_stock(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = deleted_stock.offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json["hasStocks"] == False

    def test_returns_positive_booking_count(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        stock = offers_factories.EventStockFactory(offer=offer)
        bookings_factories.BookingFactory.create_batch(2, stock=stock)

        # When
        auth_client = client.with_session_auth(email=user_offerer.user.email)
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = auth_client.get(f"/offers/{offer_id}")

        # Then
        assert response.status_code == 200
        assert response.json["bookingsCount"] == 2
        assert response.json["hasStocks"] == True
