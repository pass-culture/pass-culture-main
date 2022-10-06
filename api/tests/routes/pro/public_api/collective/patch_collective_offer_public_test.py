from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicPatchOfferTest:
    def test_patch_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "venueId": venue2.id,
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "offerVenue": {
                "venueId": None,
                "addressType": "school",
                "otherAddress": None,
            },
            "interventionArea": ["44"],
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 216.25,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()

        assert offer.name == payload["name"]
        assert offer.description == payload["description"]
        assert offer.venueId == venue2.id
        assert offer.subcategoryId == payload["subcategoryId"]
        assert offer.bookingEmails == payload["bookingEmails"]
        assert offer.contactEmail == payload["contactEmail"]
        assert offer.contactPhone == payload["contactPhone"]
        assert offer.domains == [domain]
        assert offer.durationMinutes == 183
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.offerVenue == {
            "venueId": "",
            "addressType": "school",
            "otherAddress": "",
        }
        assert offer.interventionArea == ["44"]
        assert offer.audioDisabilityCompliant == True
        assert offer.mentalDisabilityCompliant == True
        assert offer.motorDisabilityCompliant == True
        assert offer.visualDisabilityCompliant == True

        assert offer.collectiveStock.beginningDatetime == datetime.fromisoformat(payload["beginningDatetime"])
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(payload["bookingLimitDatetime"])
        assert offer.collectiveStock.price == Decimal(payload["totalPrice"])
        assert offer.collectiveStock.priceDetail == payload["educationalPriceDetail"]

        assert offer.institutionId == educational_institution.id

    def test_partial_patch_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "educationalInstitutionId": educational_institution.id,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId == educational_institution.id

    def test_patch_offer_invalid_domain(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [0],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "offerVenue": {
                "venueId": None,
                "addressType": "school",
                "otherAddress": None,
            },
            "interventionArea": ["44"],
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 404

    def test_patch_offer_invalid_api_key(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "offerVenue": {
                "venueId": None,
                "addressType": "school",
                "otherAddress": None,
            },
            "interventionArea": ["44"],
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 401

    def test_patch_offer_invalid_offerer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory()

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "offerVenue": {
                "venueId": None,
                "addressType": "school",
                "otherAddress": None,
            },
            "interventionArea": ["44"],
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 403
