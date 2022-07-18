from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories
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
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 403

    def test_access_by_unauthorized_pro_user(self, app):
        # Given
        pro_user = users_factories.ProFactory()
        offer = offers_factories.ThingOfferFactory(venue__latitude=None, venue__longitude=None)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=pro_user.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

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
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" not in response_json["venue"]
        assert "bic" not in response_json["venue"]
        assert "iban" not in response_json["venue"]["managingOfferer"]
        assert "bic" not in response_json["venue"]["managingOfferer"]
        assert "validationToken" not in response_json["venue"]["managingOfferer"]
        assert "thumbUrl" in response_json
        assert response_json["nonHumanizedId"] == offer.id

    def test_performance(self, client):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)
        offers_factories.EventStockFactory.create_batch(5, offer=offer)

        # When
        client.with_session_auth(email=user_offerer.user.email)
        humanized_offer_id = humanize(offer.id)

        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # check user access to offerer
        num_queries += 1  # Get offer by id

        with testing.assert_num_queries(num_queries):
            client.get(f"/offers/{humanized_offer_id}")

    def test_access_even_if_offerer_has_no_siren(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer=user_offerer.offerer,
            venue__managingOfferer__siren=None,
        )

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200

    def test_returns_an_active_mediation(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.ThingOfferFactory(venue__managingOfferer=user_offerer.offerer)

        mediation = offers_factories.MediationFactory(offer=offer)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        assert response.json["activeMediation"]["id"] == humanize(mediation.id)

    @freeze_time("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, app):
        # Given
        now = datetime.utcnow()
        user_offerer = offerers_factories.UserOffererFactory(
            offerer__dateCreated=now,
            offerer__dateModifiedAtLastProvider=now,
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
        )
        offer = stock.offer
        venue = offer.venue
        offerer = venue.managingOfferer
        finance_factories.BankInformationFactory(venue=venue)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        assert response.json == {
            "activeMediation": None,
            "ageMax": None,
            "ageMin": None,
            "bookingEmail": "offer.booking.email@example.com",
            "conditions": None,
            "dateCreated": "2020-10-15T00:00:00Z",
            "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
            "dateRange": ["2020-10-15T01:00:00Z", "2020-10-15T01:00:00Z"],
            "description": "Tatort, but slower",
            "durationMinutes": 60,
            "extraData": None,
            "externalTicketOfficeUrl": "http://example.net",
            "fieldsUpdated": [],
            "hasBookingLimitDatetimesPassed": False,
            "id": humanize(stock.offer.id),
            "isActive": True,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "isBookable": True,
            "isDigital": False,
            "isDuo": False,
            "isEducational": False,
            "isEditable": True,
            "isEvent": True,
            "isNational": False,
            "isThing": False,
            "lastProvider": None,
            "lastProviderId": None,
            "mediaUrls": [],
            "mediations": [],
            "name": "Derrick",
            "nonHumanizedId": stock.offer.id,
            "product": {
                "ageMax": None,
                "ageMin": None,
                "conditions": None,
                "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                "description": "Tatort, but slower",
                "durationMinutes": 60,
                "extraData": None,
                "fieldsUpdated": [],
                "id": humanize(stock.offer.product.id),
                "idAtProviders": None,
                "isGcuCompatible": True,
                "isNational": False,
                "lastProviderId": None,
                "mediaUrls": [],
                "name": "Derrick",
                "owningOffererId": None,
                "thumbCount": 0,
                "url": None,
            },
            "productId": humanize(stock.offer.product.id),
            "status": "ACTIVE",
            "stocks": [
                {
                    "beginningDatetime": "2020-10-15T01:00:00Z",
                    "bookingLimitDatetime": "2020-10-15T01:00:00Z",
                    "bookingsQuantity": 0,
                    "cancellationLimitDate": "2020-10-15T00:00:00Z",
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModified": "2020-10-15T00:00:00Z",
                    "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                    "fieldsUpdated": [],
                    "hasActivationCode": False,
                    "id": humanize(stock.id),
                    "idAtProviders": None,
                    "isBookable": True,
                    "isEventDeletable": True,
                    "isEventExpired": False,
                    "isSoftDeleted": False,
                    "lastProviderId": None,
                    "offerId": humanize(stock.offer.id),
                    "price": 10.0,
                    "quantity": 1000,
                    "remainingQuantity": 1000,
                }
            ],
            "subcategoryId": "SEANCE_CINE",
            "thumbUrl": None,
            "url": None,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "audioDisabilityCompliant": False,
                "bookingEmail": "test@test.com",
                "city": "Paris",
                "comment": None,
                "dateCreated": "2020-10-15T00:00:00Z",
                "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                "departementCode": "75",
                "fieldsUpdated": [],
                "id": humanize(venue.id),
                "idAtProviders": None,
                "isValidated": True,
                "isVirtual": False,
                "lastProviderId": None,
                "latitude": 48.87004,
                "longitude": 2.37850,
                "managingOfferer": {
                    "address": "1 boulevard Poissonnière",
                    "city": "Paris",
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                    "fieldsUpdated": [],
                    "id": humanize(offerer.id),
                    "idAtProviders": None,
                    "isActive": True,
                    "isValidated": True,
                    "lastProviderId": None,
                    "name": "Test Offerer",
                    "postalCode": "75000",
                    "siren": "123456789",
                    "thumbCount": 0,
                },
                "managingOffererId": humanize(offerer.id),
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "name": "La petite librairie",
                "postalCode": "75000",
                "publicName": "La petite librairie",
                "siret": "12345678912345",
                "thumbCount": 0,
                "venueLabelId": None,
                "visualDisabilityCompliant": False,
            },
            "venueId": humanize(venue.id),
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
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["stocks"][0]["cancellationLimitDate"] is None
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

        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["stocks"][0]["cancellationLimitDate"] is None
        assert data["subcategoryId"] == "ABO_PLATEFORME_MUSIQUE"
        assert data["stocks"][0]["hasActivationCode"] is True

    @freeze_time("2020-10-15 00:00:00")
    def test_should_not_return_soft_deleted_stock(self, app):
        # Given
        user_offerer = offerers_factories.UserOffererFactory()
        offer = offers_factories.EducationalEventOfferFactory(venue__managingOfferer=user_offerer.offerer)
        deleted_stock = offers_factories.EducationalEventStockFactory(offer=offer, isSoftDeleted=True)

        # When
        client = TestClient(app.test_client()).with_session_auth(email=user_offerer.user.email)
        response = client.get(f"/offers/{humanize(deleted_stock.offer.id)}")

        # Then
        assert response.status_code == 200
        assert len(response.json["stocks"]) == 0
