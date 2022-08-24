from datetime import datetime
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
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
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
            "priceDetail": "Justification du prix",
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
        assert offer.subcategoryId == payload["subcategoryId"]
        assert offer.bookingEmail == payload["bookingEmail"]
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

        assert offer.collectiveStock.beginningDatetime == datetime.fromisoformat(payload["beginningDatetime"])
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(payload["bookingLimitDatetime"])
        assert offer.collectiveStock.price == payload["totalPrice"]
        assert offer.collectiveStock.priceDetail == payload["priceDetail"]

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
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": ["invalid_domain"],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
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
            "priceDetail": "Justification du prix",
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
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": ["invalid_domain"],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
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
            "priceDetail": "Justification du prix",
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
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory()

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": ["invalid_domain"],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
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
            "priceDetail": "Justification du prix",
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
