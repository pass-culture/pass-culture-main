from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.human_ids import humanize

import tests

from . import image_data


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicPatchOfferTest:
    def teardown_method(self, *args):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / educational_models.CollectiveOffer.__name__.lower()
        if storage_folder.exists():
            for child in storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()

    def test_patch_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__imageCredit="pouet",
            collectiveOffer__imageCrop={"crop_data": 12},
            collectiveOffer__venue=venue,
        )

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "subcategoryId": "EVENEMENT_CINE",
            "venueId": venue2.id,
            "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
            "contactEmail": "offerer-contact@example.com",
            "contactPhone": "01 00 99 27.98",
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
            "isActive": False,
            "imageCredit": "a great artist",
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
        assert offer.contactPhone == "+33100992798"
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
        assert offer.isActive == False
        assert offer.hasImage == True
        assert offer.imageCredit == "a great artist"

        assert offer.collectiveStock.beginningDatetime == datetime.fromisoformat(payload["beginningDatetime"])
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(payload["bookingLimitDatetime"])
        assert offer.collectiveStock.price == Decimal(payload["totalPrice"])
        assert offer.collectiveStock.priceDetail == payload["educationalPriceDetail"]

        assert offer.institutionId == educational_institution.id

    def test_change_venue(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {
            "venueId": venue2.id,
            "offerVenue": {
                "venueId": venue2.id,
                "addressType": "offererVenue",
                "otherAddress": None,
            },
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()

        assert offer.venueId == venue2.id
        assert offer.offerVenue == {
            "venueId": humanize(venue2.id),
            "addressType": "offererVenue",
            "otherAddress": "",
        }

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

    def test_patch_offer_invalid_phone_number(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory()

        payload = {
            "contactPhone": "NOT A PHONE NUMBER",
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400

    def test_add_valid_image(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage == True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_add_invalid_image_size(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_SIZE}

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage == False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_add_invalid_image_type(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_TYPE}

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage == False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_delete_image(self, client):
        # SETUP
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.ApiKeyFactory(offerer=offerer)
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue)
        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage == True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        # END SETUP
        # actual test
        payload = {"imageFile": None}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )
        assert response.status_code == 200
        assert offer.hasImage == False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
