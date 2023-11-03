from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.users.factories as users_factories
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_access_by_beneficiary(self, app):
        # Given
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=beneficiary.email)
        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, app):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=pro_user.email)
        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 403


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_access_by_pro_user(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__latitude=None, venue__longitude=None, venue__managingOfferer=user_offerer.offerer
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{offer.id}")

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

    def test_access_even_if_offerer_has_no_siren(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            venue__managingOfferer__siren=None,
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 200

    def test_returns_an_active_mediation(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        mediation = offers_factories.MediationFactory(offer=offer)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 200
        assert f"/thumbs/mediations/{humanize(mediation.id)}" in response.json["activeMediation"]["thumbUrl"]

    @freeze_time("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, app):
        # Given
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=now,
            offerer__siren="123456789",
            offerer__name="Test Offerer",
        )
        stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now + timedelta(hours=1),
            bookingLimitDatetime=now + timedelta(hours=1),
            offer__dateCreated=now,
            offer__dateModifiedAtLastProvider=now,
            offer__bookingEmail="offer.booking.email@example.com",
            offer__name="Derrick",
            offer__description="Tatort, but slower",
            offer__durationMinutes=60,
            offer__mentalDisabilityCompliant=True,
            offer__externalTicketOfficeUrl="http://example.net",
            offer__withdrawalDetails="Veuillez chercher votre billet au guichet",
            offer__withdrawalType=WithdrawalTypeEnum.ON_SITE,
            offer__withdrawalDelay=60 * 30,
            offer__product__name="Derrick",
            offer__product__description="Tatort, but slower",
            offer__product__durationMinutes=60,
            offer__product__dateModifiedAtLastProvider=now,
            offer__venue__siret="12345678912345",
            offer__venue__name="La petite librairie",
            offer__venue__dateCreated=now,
            offer__venue__dateModifiedAtLastProvider=now,
            offer__venue__bookingEmail="test@test.com",
            offer__venue__managingOfferer=user_offerer.offerer,
            priceCategory__priceCategoryLabel__label="Au pied du mur",
        )
        offer = stock.offer
        venue = offer.venue
        offerer = venue.managingOfferer
        finance_factories.BankInformationFactory(venue=venue)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "activeMediation": None,
            "bookingContact": None,
            "bookingEmail": "offer.booking.email@example.com",
            "dateCreated": "2020-10-15T00:00:00Z",
            "description": "Tatort, but slower",
            "durationMinutes": 60,
            "extraData": None,
            "externalTicketOfficeUrl": "http://example.net",
            "hasBookingLimitDatetimesPassed": False,
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
            "stocks": [
                {
                    "activationCodesExpirationDatetime": None,
                    "beginningDatetime": "2020-10-15T01:00:00Z",
                    "bookingLimitDatetime": "2020-10-15T01:00:00Z",
                    "bookingsQuantity": 0,
                    "hasActivationCode": False,
                    "priceCategoryId": stock.priceCategoryId,
                    "id": stock.id,
                    "isEventDeletable": True,
                    "price": 10.1,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                }
            ],
            "priceCategories": [{"label": "Au pied du mur", "price": 10.1, "id": stock.priceCategoryId}],
            "subcategoryId": "SEANCE_CINE",
            "thumbUrl": None,
            "url": None,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "audioDisabilityCompliant": False,
                "bookingEmail": "test@test.com",
                "city": "Paris",
                "departementCode": "75",
                "id": venue.id,
                "isVirtual": False,
                "managingOfferer": {
                    "id": offerer.id,
                    "name": "Test Offerer",
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

    @freeze_time("2019-10-15 00:00:00")
    def test_returns_a_thing_stock(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        stock = offers_factories.ThingStockFactory(offer__venue__managingOfferer=user_offerer.offerer)
        offer = stock.offer
        offer.subcategoryId = subcategories.LIVRE_PAPIER.id
        repository.save(offer)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["subcategoryId"] == "LIVRE_PAPIER"

    @freeze_time("2019-10-15 00:00:00")
    def test_returns_a_thing_with_activation_code_stock(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.OfferFactory(
            stocks=[offers_factories.StockWithActivationCodesFactory()],
            subcategoryId=subcategories.ABO_PLATEFORME_MUSIQUE.id,
            url="fake-url",
            venue__managingOfferer=user_offerer.offerer,
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)

        response = client.get(f"/offers/{offer.id}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["subcategoryId"] == "ABO_PLATEFORME_MUSIQUE"
        assert data["stocks"][0]["hasActivationCode"] is True

    @freeze_time("2020-10-15 00:00:00")
    def test_should_not_return_soft_deleted_stock(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{deleted_stock.offer.id}")

        # Then
        assert response.status_code == 200
        assert len(response.json["stocks"]) == 0
