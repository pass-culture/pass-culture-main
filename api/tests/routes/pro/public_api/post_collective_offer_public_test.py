from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicPostOfferTest:
    def test_post_offers(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective-offers/", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == educational_institution.id
        assert offer.interventionArea == ["44"]
        assert offer.offerVenue == {
            "venueId": humanize(venue.id),
            "addressType": "offererVenue",
            "otherAddress": "",
        }

    def test_invalid_api_key(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective-offers/", json=payload
            )

        # Then
        assert response.status_code == 401

    def test_user_cannot_create_collective_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
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
        with patch(
            "pcapi.core.offerers.api.can_offerer_create_educational_offer",
            side_effect=educational_exceptions.CulturalPartnerNotFoundException,
        ):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective-offers/", json=payload
            )

        # Then
        assert response.status_code == 403

    def test_bad_educational_institution(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "interventionArea": ["44"],
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "priceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": -1,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective-offers/", json=payload
            )

        # Then
        assert response.status_code == 404

    def test_bad_intervention_area(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "interventionArea": ["44", "158"],
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective-offers/", json=payload
            )

        # Then
        assert response.status_code == 404

    def test_bad_venue_id(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        payload = {
            "venueId": -1,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmail": "offerer-email@example.com",
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.name],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.value],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": 0,
                "addressType": "offererVenue",
                "otherAddress": "",
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective-offers/", json=payload
            )

        # Then
        assert response.status_code == 404
