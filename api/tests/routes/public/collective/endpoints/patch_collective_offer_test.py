from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest

from pcapi import settings
import pcapi.core.categories.subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils

import tests
from tests.routes import image_data


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
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
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        venue2 = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        national_program = educational_factories.NationalProgramFactory()

        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet",
            imageId="123456789",
            venue=venue,
            provider=venue_provider.provider,
            nationalProgramId=None,
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {
            "name": "Un nom en français ævœc des diàcrtîtïqués",
            "description": "une description d'offre",
            "formats": [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE.value],
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
            "isActive": False,
            "imageCredit": "a great artist",
            "nationalProgramId": national_program.id,
            # stock part
            "beginningDatetime": stock.beginningDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
            "totalPrice": 96.25,
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
        assert offer.formats == [subcategories.EacFormat.PROJECTION_AUDIOVISUELLE]
        assert offer.bookingEmails == payload["bookingEmails"]
        assert offer.contactEmail == payload["contactEmail"]
        assert offer.contactPhone == "+33100992798"
        assert offer.domains == [domain]
        assert offer.durationMinutes == 183
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.offerVenue == {
            "venueId": None,
            "addressType": "school",
            "otherAddress": "",
        }
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.visualDisabilityCompliant is True
        assert offer.isActive is False
        assert offer.hasImage is True
        assert offer.imageCredit == "a great artist"
        assert offer.nationalProgramId == national_program.id

        assert offer.collectiveStock.beginningDatetime == datetime.fromisoformat(payload["beginningDatetime"])
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(payload["bookingLimitDatetime"])
        assert offer.collectiveStock.price == Decimal(payload["totalPrice"])
        assert offer.collectiveStock.priceDetail == payload["educationalPriceDetail"]

        assert offer.institutionId == educational_institution.id
        assert educational_institution.isActive is True

    def test_patch_offer_price_should_be_lower(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory()
        offerer = stock.collectiveOffer.venue.managingOfferer
        offerers_factories.ApiKeyFactory(offerer=offerer)

        payload = {
            "totalPrice": 1196.25,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 403

    def test_change_venue(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        venue2 = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

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
            "venueId": venue2.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }

    def test_partial_patch_offer(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

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
        assert educational_institution.isActive is True

    def test_patch_private_api_offer(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        api_key = offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(
            validation=OfferValidationStatus.PENDING, name="old_name", venue=venue, provider=api_key.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {
            "name": "new_name",
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 422

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.name == "old_name"

    def test_partial_patch_offer_uai(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        educational_institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")

        payload = {
            "educationalInstitution": "UAI123",
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
        assert educational_institution.isActive is True

    def test_should_update_endDatetime_and_startDatetime(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        next_month = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(days=30)
        next_month_minus_one_day = next_month - timedelta(days=1)

        stringified_next_month = date_utils.utc_datetime_to_department_timezone(next_month, None).isoformat()
        stringified_next_month_minus_one_day = date_utils.utc_datetime_to_department_timezone(
            next_month_minus_one_day, None
        ).isoformat()

        payload = {
            "startDatetime": stringified_next_month_minus_one_day,
            "endDatetime": stringified_next_month,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()

        assert offer.collectiveStock.startDatetime == next_month_minus_one_day
        assert offer.collectiveStock.endDatetime == next_month

    def test_should_raise_400_because_endDatetime_is_before_startDatetime(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        next_month = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(days=30)
        next_month_minus_one_day = next_month - timedelta(days=1)

        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(next_month, None).isoformat(),
            "endDatetime": date_utils.utc_datetime_to_department_timezone(next_month_minus_one_day, None).isoformat(),
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    def test_patch_offer_uai_and_institution_id(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        educational_institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {
            "educationalInstitution": "UAI123",
            "educationalInstitutionId": educational_institution.id,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId is None

    def test_patch_offer_invalid_domain(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

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
            # stock part
            "beginningDatetime": stock.beginningDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
            "totalPrice": 21,
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
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

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
            # stock part
            "beginningDatetime": stock.beginningDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
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
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=provider_factories.ProviderFactory())
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

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
            # stock part
            "beginningDatetime": stock.beginningDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
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
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

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

    def test_patch_offer_institution_not_active(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        venue2 = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory(isActive=False)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
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
            "isActive": False,
            # stock part
            "beginningDatetime": "2022-09-25T11:00",
            "bookingLimitDatetime": "2022-09-15T11:00",
            "totalPrice": 216.25,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
        }
        # when
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # then
        assert response.status_code == 400

    def test_add_valid_image(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_add_invalid_image_size(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_SIZE}

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_add_invalid_image_type(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_TYPE}

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_delete_image(self, client):
        # SETUP
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )
        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        # END SETUP
        # actual test
        payload = {"imageFile": None}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )
        assert response.status_code == 200
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_patch_offer_invalid_domains(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet",
            imageId="123456789",
            venue=venue,
            provider=venue_provider.provider,
            domains=[domain],
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {
            "domains": [0],
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 404
        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.domains[0].id == domain.id

    def test_patch_offer_bad_institution(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            imageId="123456789",
            imageCredit="pouet",
            provider=venue_provider.provider,
            institution=educational_institution,
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {
            "educationalInstitutionId": 0,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 404

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId == educational_institution.id

    def test_patch_offer_invalid_subcategory(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet",
            imageId="123456789",
            venue=venue,
            provider=venue_provider.provider,
            subcategoryId="OLD_SUBCATEGORY",
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
        )

        payload = {
            "subcategoryId": "BAD_SUBCATEGORY",
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 404

        offer = educational_models.CollectiveOffer.query.filter_by(id=stock.collectiveOffer.id).one()

        assert offer.subcategoryId == "OLD_SUBCATEGORY"

    def test_unknown_national_program(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        venue2 = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        domain = educational_factories.EducationalDomainFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet",
            imageId="123456789",
            venue=venue,
            provider=venue_provider.provider,
            nationalProgramId=None,
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
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
            "isActive": False,
            "imageCredit": "a great artist",
            # stock part
            "beginningDatetime": stock.beginningDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
            "totalPrice": 96.25,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
            "nationalProgramId": 0,
        }

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        # Then
        assert response.status_code == 400
        assert "nationalProgramId" in response.json
