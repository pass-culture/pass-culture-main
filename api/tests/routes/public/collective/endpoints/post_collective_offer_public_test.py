from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import override_features

import tests
from tests.routes import image_data


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicPostOfferTest:
    def teardown_method(self, *args):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / educational_models.CollectiveOffer.__name__.lower()
        if storage_folder.exists():
            for child in storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()

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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": "pouet",
            "imageFile": image_data.GOOD_IMAGE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == educational_institution.id
        assert offer.interventionArea == []
        assert offer.offerVenue == {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }
        assert offer.isPublicApi is True
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    @override_features(WIP_ADD_CLG_6_5_COLLECTIVE_OFFER=True)
    def test_post_offers_6_5_only(self, client):
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [
                educational_models.StudentLevels.COLLEGE6.name,
                educational_models.StudentLevels.COLLEGE5.name,
            ],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 403

    def test_post_offers_with_uai(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitution": "UAI123",
            "imageCredit": "pouet",
            "imageFile": image_data.GOOD_IMAGE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == educational_institution.id
        assert offer.interventionArea == []
        assert offer.offerVenue == {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }
        assert offer.isPublicApi is True
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_post_offers_with_uai_and_institution_id(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitution": "UAI123",
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": "pouet",
            "imageFile": image_data.GOOD_IMAGE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 400

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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
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
        with patch(
            "pcapi.core.offerers.api.can_offerer_create_educational_offer",
            side_effect=educational_exceptions.CulturalPartnerNotFoundException,
        ):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": -1,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": 0,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
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
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 404

    def test_invalid_image_size(self, client):
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": "pouet",
            "imageFile": image_data.WRONG_IMAGE_SIZE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 400

    def test_invalid_image_type(self, client):
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": "pouet",
            "imageFile": image_data.WRONG_IMAGE_TYPE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 400

    def test_post_offers_institution_not_active(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory(isActive=False)

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": "pouet",
            "imageFile": image_data.GOOD_IMAGE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 403

    def test_post_offers_invalid_domain(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        educational_institution = educational_factories.EducationalInstitutionFactory()

        payload = {
            "venueId": venue.id,
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [0],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": "pouet",
            "imageFile": image_data.GOOD_IMAGE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 404

    def test_post_offers_bad_institution(self, client):
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
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": 0,
            "imageCredit": "pouet",
            "imageFile": image_data.GOOD_IMAGE,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 404

    def test_post_offers_invalid_subcategory(self, client):
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
            "subcategoryId": "BAD_SUBCATEGORY",
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "+33100992798",
            "domains": [domain.id],
            "durationMinutes": 183,
            "students": [educational_models.StudentLevels.COLLEGE4.name],
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            "isActive": True,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 35621,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "imageCredit": None,
            "imageFile": None,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
                "/v2/collective/offers/", json=payload
            )

        # Then
        assert response.status_code == 404
