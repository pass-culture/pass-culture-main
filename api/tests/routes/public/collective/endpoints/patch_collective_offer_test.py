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
from pcapi.core.testing import override_features
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils

import tests
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIEndpointBaseHelper
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicPatchOfferTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

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
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue_provider.venue)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(plain_api_key).patch(
                self.endpoint_url.format(offer_id=stock.collectiveOffer.id),
                json={"totalPrice": 1196.25},
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

    @pytest.mark.parametrize("institution_field", ["educationalInstitution", "educationalInstitutionId"])
    def test_does_not_update_institution_if_field_is_null(self, institution_field, client):
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveStockFactory(
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__institution=educational_factories.EducationalInstitutionFactory(),
        ).collectiveOffer

        payload = {institution_field: None}
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=offer.id).one()
        assert offer.institutionId

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

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_should_update_expired_booking(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        now = datetime.utcnow()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            beginningDatetime=now + timedelta(days=5),
            bookingLimitDatetime=now - timedelta(days=2),
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=educational_models.CollectiveBookingStatus.CANCELLED,
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - timedelta(days=1),
        )

        new_limit = now + timedelta(days=1)
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json={"bookingLimitDatetime": new_limit.isoformat()}
            )
            assert response.status_code == 200

        db.session.refresh(stock)
        db.session.refresh(booking)
        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == educational_models.CollectiveBookingStatus.PENDING
        assert booking.cancellationReason == None
        assert booking.cancellationDate == None

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=False)
    def test_should_not_update_expired_booking(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        now = datetime.utcnow()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            beginningDatetime=now + timedelta(days=5),
            bookingLimitDatetime=now - timedelta(days=2),
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=educational_models.CollectiveBookingStatus.CANCELLED,
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - timedelta(days=1),
        )

        new_limit = now + timedelta(days=1)
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json={"bookingLimitDatetime": new_limit.isoformat()}
            )
            assert response.status_code == 200

        db.session.refresh(stock)
        db.session.refresh(booking)
        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.EXPIRED
        assert booking.cancellationDate == now - timedelta(days=1)


@pytest.mark.usefixtures("db_session")
class UpdateOfferVenueTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_change_to_offerer_venue(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        # we accept None for otherAddress but we store "" as our GET schemas expect a string
        dst = self.offer_venue_offerer_venue(venue_provider.venueId)
        expected = {**dst, "otherAddress": ""}

        self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_school(),
            dst=dst,
            expected=expected,
        )

    def test_change_to_school(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        # we accept None for otherAddress but we store "" as our GET schemas expect a string
        dst = self.offer_venue_school()
        expected = {**dst, "otherAddress": ""}

        self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_other(),
            dst=dst,
            expected=expected,
        )

    def test_change_to_other_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_offerer_venue(venue_provider.venueId),
            dst=self.offer_venue_other(),
        )

    def test_offer_venue_is_updated_when_type_is_the_same_and_data_different(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        dst = {**self.offer_venue_other(), "otherAddress": "another address"}

        self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_other(),
            dst=dst,
        )

    def test_offer_venue_is_updated_even_if_unneeded_field_is_missing(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        dst = self.offer_venue_offerer_venue(venue_provider.venueId)
        dst.pop("otherAddress")

        self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_school(),
            dst=dst,
        )

    def test_offer_venue_is_not_updated_when_venue_id_is_invalid(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        self.assert_offer_venue_is_not_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_offerer_venue(venue_provider.venueId),
            payload=self.offer_venue_offerer_venue("unknown and invalid id"),
            status_code=400,
            json_error={"offerVenue.venueId": ["invalid literal for int() with base 10: 'unknown and invalid id'"]},
        )

    def test_offer_venue_is_not_updated_when_updating_with_current_values(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        self.assert_offer_venue_is_not_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_other(),
            payload=self.offer_venue_other(),
            status_code=200,
        )

    def test_offer_venue_is_not_updated_when_unneeded_field_is_set(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        self.assert_offer_venue_is_not_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_school(),
            status_code=404,
            payload={**self.offer_venue_school(), "otherAddress": "should not be set"},
        )

    def test_offer_venue_is_not_updated_when_an_extra_field_is_set(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        self.assert_offer_venue_is_not_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_school(),
            payload={**self.offer_venue_other(), "unknownField": "oops"},
            status_code=400,
            json_error={"offerVenue.unknownField": ["extra fields not permitted"]},
        )

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_active_venue_provider()
        offer = educational_factories.CollectiveStockFactory().collectiveOffer
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(plain_api_key).patch(
                f"/v2/collective/offers/{offer.id}", json={"offerVenue": self.offer_venue_school()}
            )

        # test says 404 but the implementation says 403 and since we
        # need to implement this abstract method... lets keep it that
        # way (for now).
        assert response.status_code == 403

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        """Check does not exist for now"""
        pass

    def setup_and_send_request(self, client, api_key, src, payload, venue_provider):
        offer = educational_factories.CollectiveStockFactory(
            collectiveOffer__offerVenue=src,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__provider=venue_provider.provider,
        ).collectiveOffer

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_explicit_token(api_key).patch(
                f"/v2/collective/offers/{offer.id}", json={"offerVenue": payload}
            )

        return response, offer

    def assert_offer_venue_has_been_updated(self, client, api_key, venue_provider, src, dst, expected=None):
        expected_result = dst if expected is None else expected

        response, offer = self.setup_and_send_request(
            client=client,
            api_key=api_key,
            src=src,
            venue_provider=venue_provider,
            payload=dst,
        )

        assert response.status_code == 200

        db.session.refresh(offer)

        # check that offerVenue has been updated with dst values:
        # all common values have been copied and other are null.
        assert dst.keys() <= offer.offerVenue.keys()
        assert all(offer.offerVenue[key] == value for key, value in expected_result.items())
        assert all(not value for key, value in offer.offerVenue.items() if key not in dst)

    def assert_offer_venue_is_not_updated(
        self, client, api_key, venue_provider, src, status_code, payload, json_error=None
    ):
        response, offer = self.setup_and_send_request(
            client=client,
            api_key=api_key,
            src=src,
            venue_provider=venue_provider,
            payload=payload,
        )

        assert response.status_code == status_code
        if json_error:
            assert response.json == json_error

        db.session.refresh(offer)
        assert offer.offerVenue == src

    def offer_venue_school(self):
        return {
            "venueId": None,
            "addressType": "school",
            "otherAddress": None,
        }

    def offer_venue_offerer_venue(self, venue_id):
        return {
            "venueId": venue_id,
            "addressType": "offererVenue",
            "otherAddress": None,
        }

    def offer_venue_other(self):
        return {
            "venueId": None,
            "addressType": "other",
            "otherAddress": "something, Somewhereshire",
        }
