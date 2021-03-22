from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200:
    def test_access_by_beneficiary(self, app):
        # Given
        beneficiary = users_factories.UserFactory()
        offer = offers_factories.ThingOfferFactory()

        # When
        client = TestClient(app.test_client()).with_auth(email=beneficiary.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        response_json = response.json
        assert response.status_code == 200
        assert "iban" in response_json["venue"]
        assert "bic" in response_json["venue"]
        assert "iban" in response_json["venue"]["managingOfferer"]
        assert "bic" in response_json["venue"]["managingOfferer"]
        assert "validationToken" not in response_json["venue"]["managingOfferer"]
        assert "thumbUrl" in response_json

    def test_access_even_if_offerer_has_no_siren(self, app):
        # Given
        beneficiary = users_factories.UserFactory()
        offer = offers_factories.ThingOfferFactory(
            venue__managingOfferer__siren=None,
        )

        # When
        client = TestClient(app.test_client()).with_auth(email=beneficiary.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200

    def test_returns_an_active_mediation(self, app):
        # Given
        beneficiary = users_factories.UserFactory()
        offer = offers_factories.ThingOfferFactory()
        mediation = offers_factories.MediationFactory(offer=offer)

        # When
        client = TestClient(app.test_client()).with_auth(email=beneficiary.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        assert response.json["activeMediation"]["id"] == humanize(mediation.id)

    @freeze_time("2020-10-15 00:00:00")
    def test_returns_an_event_stock(self, app):
        # Given
        now = datetime.utcnow()
        beneficiary = users_factories.UserFactory()
        stock = offers_factories.EventStockFactory(
            dateCreated=now,
            dateModified=now,
            dateModifiedAtLastProvider=now,
            beginningDatetime=now + timedelta(hours=1),
            bookingLimitDatetime=now,
            offer__dateCreated=now,
            offer__dateModifiedAtLastProvider=now,
            offer__bookingEmail="offer.booking.email@example.com",
            offer__name="Derrick",
            offer__description="Tatort, but slower",
            offer__durationMinutes=60,
            offer__mentalDisabilityCompliant=True,
            offer__externalTicketOfficeUrl="http://example.net",
            offer__product__name="Derrick",
            offer__product__description="Tatort, but slower",
            offer__product__durationMinutes=60,
            offer__product__dateModifiedAtLastProvider=now,
            offer__venue__siret="12345678912345",
            offer__venue__name="La petite librairie",
            offer__venue__dateCreated=now,
            offer__venue__dateModifiedAtLastProvider=now,
            offer__venue__bookingEmail="test@test.com",
            offer__venue__managingOfferer__dateCreated=now,
            offer__venue__managingOfferer__dateModifiedAtLastProvider=now,
            offer__venue__managingOfferer__siren="123456789",
            offer__venue__managingOfferer__name="Test Offerer",
        )
        offer = stock.offer
        venue = offer.venue
        offerer = venue.managingOfferer
        offers_factories.BankInformationFactory(venue=venue)

        # When
        client = TestClient(app.test_client()).with_auth(email=beneficiary.email)
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
            "idAtProviders": None,
            "isActive": True,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "isBookable": True,
            "isDigital": False,
            "isDuo": False,
            "isEditable": True,
            "isEvent": True,
            "isNational": False,
            "isThing": False,
            "lastProvider": None,
            "lastProviderId": None,
            "mediaUrls": [],
            "mediations": [],
            "name": "Derrick",
            "offerType": {
                "appLabel": "Cinéma",
                "canExpire": None,
                "conditionalFields": ["author", "visa", "stageDirector"],
                "description": "Action, science-fiction, documentaire ou "
                "comédie sentimentale ? En salle, en plein air "
                "ou bien au chaud chez soi ? Et si c’était "
                "plutôt cette exposition qui allait faire son "
                "cinéma ?",
                "isActive": True,
                "offlineOnly": True,
                "onlineOnly": False,
                "proLabel": "Cinéma - projections et autres évènements",
                "sublabel": "Regarder",
                "type": "Event",
                "value": "EventType.CINEMA",
            },
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
            "validation": "APPROVED",
            "stocks": [
                {
                    "beginningDatetime": "2020-10-15T01:00:00Z",
                    "bookingLimitDatetime": "2020-10-15T00:00:00Z",
                    "bookingsQuantity": 0,
                    "cancellationLimitDate": "2020-10-15T00:00:00Z",
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModified": "2020-10-15T00:00:00Z",
                    "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                    "fieldsUpdated": [],
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
            "thumbUrl": None,
            "type": "EventType.CINEMA",
            "url": None,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "bic": None,
                "bookingEmail": None,
                "city": "Paris",
                "comment": None,
                "dateCreated": "2020-10-15T00:00:00Z",
                "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                "departementCode": "75",
                "fieldsUpdated": [],
                "iban": None,
                "id": humanize(venue.id),
                "idAtProviders": None,
                "isValidated": True,
                "isVirtual": False,
                "lastProviderId": None,
                "latitude": 48.87004,
                "longitude": 2.37850,
                "managingOfferer": {
                    "address": None,
                    "bic": None,
                    "city": "Paris",
                    "dateCreated": "2020-10-15T00:00:00Z",
                    "dateModifiedAtLastProvider": "2020-10-15T00:00:00Z",
                    "fieldsUpdated": [],
                    "iban": None,
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
                "name": "La petite librairie",
                "postalCode": "75000",
                "publicName": "La petite librairie",
                "siret": "12345678912345",
                "thumbCount": 0,
                "venueLabelId": None,
                "venueTypeId": None,
            },
            "venueId": humanize(venue.id),
            "withdrawalDetails": None,
        }

    @freeze_time("2019-10-15 00:00:00")
    def test_returns_a_thing_stock(self, app):
        # Given
        beneficiary = users_factories.UserFactory()
        stock = offers_factories.ThingStockFactory()
        offer = stock.offer

        # When
        client = TestClient(app.test_client()).with_auth(email=beneficiary.email)
        response = client.get(f"/offers/{humanize(offer.id)}")

        # Then
        assert response.status_code == 200
        data = response.json
        assert data["stocks"][0]["cancellationLimitDate"] is None
        assert data["offerType"]["canExpire"] is True
