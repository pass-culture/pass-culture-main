from datetime import datetime
from datetime import timedelta
from datetime import timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.providers import models as providers_models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.public.collective.endpoints.offers import PATCH_NON_NULLABLE_FIELDS
from pcapi.utils import date as date_utils

import tests
from tests.routes import image_data
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER

NON_REQUIRED_NON_NULLABLE_FIELDS_CUSTOM_ERROR = {
    "contactEmail": "Ce champ ne peut pas être vide",
    "contactPhone": "Ce numéro de telephone ne semble pas valide",
    "startDatetime": "La date de début de l'évènement ne peut pas être vide.",
    "endDatetime": "La date de fin de l'évènement ne peut pas être vide.",
    "totalPrice": "Le prix ne peut pas être nul.",
    "numberOfTickets": "Le nombre de places ne peut pas être nul.",
    "formats": "formats must have at least one value",
    "name": "name cannot be empty",
    "domains": "domains must have at least one value",
}
# the other fields have the same error message when null
NON_REQUIRED_NON_NULLABLE_FIELDS = (
    set(PATCH_NON_NULLABLE_FIELDS)
    - NON_REQUIRED_NON_NULLABLE_FIELDS_CUSTOM_ERROR.keys()
    - {"price"}  # this one is aliased as totalPrice
)

# there is not DRAFT offer in public API
# the HIDDEN status is for templates only once the WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API FF is ON
# the ARCHIVED status must be tested separately as we need the ArchivedPublishedCollectiveOfferFactory factory
STATUSES_NOT_IN_PUBLIC_API = {
    educational_models.CollectiveOfferDisplayedStatus.DRAFT,
    educational_models.CollectiveOfferDisplayedStatus.HIDDEN,
    educational_models.CollectiveOfferDisplayedStatus.ARCHIVED,
}

time_travel_str = "2021-10-01 15:00:00"


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicPatchOfferTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        pass

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass

    def teardown_method(self, *args):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / educational_models.CollectiveOffer.__name__.lower()
        if storage_folder.exists():
            for child in storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()

    @time_machine.travel(time_travel_str)
    def test_patch_offer(self, client):
        educational_factories.EducationalCurrentYearFactory()
        venue_provider = provider_factories.VenueProviderFactory()
        venue = venue_provider.venue
        other_venue_provider = provider_factories.VenueProviderFactory(
            provider=venue_provider.provider, venue__managingOfferer=venue.managingOfferer, venue__pricing_point=venue
        )
        other_venue = other_venue_provider.venue

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
            "formats": [EacFormat.PROJECTION_AUDIOVISUELLE.value],
            "venueId": other_venue.id,
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
            "interventionArea": ["33", "75"],
            "isActive": False,
            "imageCredit": "a great artist",
            "nationalProgramId": national_program.id,
            # stock part
            "startDatetime": stock.startDatetime.isoformat(timespec="seconds"),
            "endDatetime": stock.endDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
            "totalPrice": 96.25,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
            # link to educational institution
            "educationalInstitutionId": educational_institution.id,
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()

        assert offer.name == payload["name"]
        assert offer.description == payload["description"]
        assert offer.venueId == other_venue.id
        assert offer.formats == [EacFormat.PROJECTION_AUDIOVISUELLE]
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
        assert offer.interventionArea == ["33", "75"]
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.visualDisabilityCompliant is True
        assert offer.isActive is False
        assert offer.hasImage is True
        assert offer.imageCredit == "a great artist"
        assert offer.nationalProgramId == national_program.id

        assert offer.collectiveStock.startDatetime == datetime.fromisoformat(payload["startDatetime"])
        assert offer.collectiveStock.endDatetime == datetime.fromisoformat(payload["endDatetime"])
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(payload["bookingLimitDatetime"])
        assert offer.collectiveStock.price == Decimal(payload["totalPrice"])
        assert offer.collectiveStock.priceDetail == payload["educationalPriceDetail"]

        assert offer.institutionId == educational_institution.id
        assert educational_institution.isActive is True

    @pytest.mark.parametrize("field", NON_REQUIRED_NON_NULLABLE_FIELDS)
    def test_non_nullable_field(self, client, field):
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {field: None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {field: ["Ce champ peut ne pas être présent mais ne peut pas être null."]}

    @pytest.mark.parametrize("field,error", NON_REQUIRED_NON_NULLABLE_FIELDS_CUSTOM_ERROR.items())
    def test_non_nullable_field_custom_error(self, client, field, error):
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {field: None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {field: [error]}

    def test_change_venue(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = venue_provider.venue
        other_venue_provider = provider_factories.VenueProviderFactory(
            provider=venue_provider.provider, venue__managingOfferer=venue.managingOfferer, venue__pricing_point=venue
        )
        other_venue = other_venue_provider.venue

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, provider=venue_provider.provider)

        payload = {
            "venueId": other_venue.id,
            "offerVenue": {
                "venueId": other_venue.id,
                "addressType": "offererVenue",
                "otherAddress": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=offer.id).one()
        assert offer.venueId == other_venue.id
        assert offer.offerVenue == {
            "venueId": other_venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }

    def test_change_venue_error(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = venue_provider.venue
        # venue with different pricing point
        other_venue_provider = provider_factories.VenueProviderFactory(
            provider=venue_provider.provider, venue__managingOfferer=venue.managingOfferer
        )
        other_venue = other_venue_provider.venue

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, provider=venue_provider.provider)

        payload = {"venueId": other_venue.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"venueId": ["L'offre ne peut pas être déplacée sur ce lieu."]}

        offer = educational_models.CollectiveOffer.query.filter_by(id=offer.id).one()
        assert offer.venueId == venue.id

    def test_partial_patch_offer(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"educationalInstitutionId": educational_institution.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId == educational_institution.id
        assert educational_institution.isActive is True

    def test_patch_private_api_offer(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        api_key = offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(
            validation=OfferValidationStatus.PENDING, name="old_name", venue=venue, provider=api_key.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"name": "new_name"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 422

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.name == "old_name"

    def test_partial_patch_offer_uai(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)
        educational_institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")

        payload = {"educationalInstitution": "UAI123"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId == educational_institution.id
        assert educational_institution.isActive is True

    @time_machine.travel(time_travel_str)
    def test_should_update_endDatetime_and_startDatetime(self, client):
        educational_factories.EducationalCurrentYearFactory()

        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()

        assert offer.collectiveStock.startDatetime == next_month_minus_one_day
        assert offer.collectiveStock.endDatetime == next_month

    def test_should_raise_400_because_endDatetime_is_before_startDatetime(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        next_month = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(days=30)
        next_month_minus_one_day = next_month - timedelta(days=1)

        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(next_month, None).isoformat(),
            "endDatetime": date_utils.utc_datetime_to_department_timezone(next_month_minus_one_day, None).isoformat(),
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    def test_should_raise_400_because_booking_limit_is_after_start(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        new_start = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(days=30)
        new_end = new_start + timedelta(days=10)
        new_limit = new_start + timedelta(days=5)

        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(new_start, None).isoformat(),
            "endDatetime": date_utils.utc_datetime_to_department_timezone(new_end, None).isoformat(),
            "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(new_limit, None).isoformat(),
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    def test_patch_offer_uai_and_institution_id(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        educational_institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {
            "educationalInstitution": "UAI123",
            "educationalInstitutionId": educational_institution.id,
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {
            "__root__": [
                "Les champs educationalInstitution et educationalInstitutionId sont mutuellement exclusifs. "
                "Vous ne pouvez pas remplir les deux en même temps"
            ]
        }

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId is None

    def test_patch_offer_invalid_api_key(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"description": "une description d'offre"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 401
        assert response.json == {"auth": "API key required"}

    def test_patch_offer_invalid_offerer(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=provider_factories.ProviderFactory())
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"description": "une description d'offre"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette offre collective."]
        }

    def test_patch_offer_invalid_phone_number(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"contactPhone": "NOT A PHONE NUMBER"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"contactPhone": ["Ce numéro de telephone ne semble pas valide"]}

    def test_patch_offer_institution_not_active(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        educational_institution = educational_factories.EducationalInstitutionFactory(isActive=False)
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"educationalInstitutionId": educational_institution.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 403
        assert response.json == {"global": ["cet institution est expiré."]}

    def test_add_valid_image(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_add_invalid_image_size(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_SIZE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"imageFile": ["L'image doit faire exactement 400*600 pixels"]}

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_add_invalid_image_type(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_TYPE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"imageFile": ["Les formats acceptés sont:  png, jpg, jpeg, mpo, webp"]}

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_delete_image(self, client):
        # SETUP
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )
        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        # END SETUP

        # actual test
        payload = {"imageFile": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{stock.collectiveOffer.id}", json=payload
            )

        assert response.status_code == 200
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_patch_offer_invalid_domains(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider, domains=[domain]
        )

        payload = {"domains": [0]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 404
        assert response.json == {"domains": ["Domaine scolaire non trouvé."]}
        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=offer.id).one()
        assert offer.domains[0].id == domain.id

    def test_patch_offer_empty_domains(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, provider=venue_provider.provider)

        payload = {"domains": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}

    def test_patch_offer_bad_institution(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider, institution=educational_institution
        )

        payload = {"educationalInstitutionId": 0}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 404
        assert response.json == {"educationalInstitutionId": ["Établissement scolaire non trouvé."]}
        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=offer.id).one()
        assert offer.institutionId == educational_institution.id

    def test_unknown_national_program(self, client):
        venue_provider = provider_factories.VenueProviderFactory()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider, nationalProgramId=None
        )

        payload = {"nationalProgramId": 0}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{offer.id}", json=payload
            )

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif inconnu"]}
        assert offer.nationalProgramId is None

    def test_national_program_null(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=educational_factories.NationalProgramFactory(),
        )
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)
        assert offer.nationalProgramId is not None

        payload = {"nationalProgramId": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(f"/v2/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 200
        assert offer.nationalProgramId is None

    def test_should_update_expired_booking(self, client):
        now = datetime.utcnow()
        limit = now - timedelta(days=2)

        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=now + timedelta(days=5), bookingLimitDatetime=limit
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock,
            status=educational_models.CollectiveBookingStatus.CANCELLED,
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.EXPIRED,
            cancellationDate=now - timedelta(days=1),
            confirmationLimitDate=limit,
        )

        new_limit = now + timedelta(days=1)
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(
                self.endpoint_url.format(offer_id=offer.id), json={"bookingLimitDatetime": new_limit.isoformat()}
            )
            assert response.status_code == 200

        db.session.refresh(stock)
        db.session.refresh(booking)
        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == educational_models.CollectiveBookingStatus.PENDING
        assert booking.cancellationReason == None
        assert booking.cancellationDate == None
        assert booking.confirmationLimitDate == new_limit

    def test_description_invalid(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(
                self.endpoint_url.format(offer_id=offer.id), json={"description": "too_long" * 200}
            )

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    @time_machine.travel(time_travel_str)
    def test_different_educational_years(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        # 2021-2022
        educational_factories.EducationalYearFactory(
            beginningDate=datetime(2021, 9, 1), expirationDate=datetime(2022, 8, 31)
        )
        # 2022-2023
        educational_factories.EducationalYearFactory(
            beginningDate=datetime(2022, 9, 1), expirationDate=datetime(2023, 8, 31)
        )
        # 2023-2024
        educational_factories.EducationalYearFactory(
            beginningDate=datetime(2023, 9, 1), expirationDate=datetime(2024, 8, 31)
        )
        # offer on year 2022-2023
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=datetime(2022, 10, 5))
        stock_start = stock.startDatetime
        stock_end = stock.endDatetime

        # update end to year 2023-2024
        payload = {
            "endDatetime": date_utils.utc_datetime_to_department_timezone(datetime(2023, 10, 5), None).isoformat()
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}
        db.session.refresh(stock)
        assert stock.startDatetime == stock_start
        assert stock.endDatetime == stock_end

        # update start to year 2021-2022
        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(datetime(2021, 10, 5), None).isoformat()
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}
        db.session.refresh(stock)
        assert stock.startDatetime == stock_start
        assert stock.endDatetime == stock_end

        # update start and end to different years
        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(datetime(2021, 10, 5), None).isoformat(),
            "endDatetime": date_utils.utc_datetime_to_department_timezone(datetime(2022, 10, 5), None).isoformat(),
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}
        db.session.refresh(stock)
        assert stock.startDatetime == stock_start
        assert stock.endDatetime == stock_end

    @time_machine.travel(time_travel_str)
    def test_educational_year_missing_start(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"startDatetime": stock.startDatetime.replace(stock.startDatetime.year + 1).isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["Année scolaire manquante pour la date de début."]}

    @time_machine.travel(time_travel_str)
    def test_educational_year_missing_end(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"endDatetime": stock.endDatetime.replace(stock.endDatetime.year + 1).isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["Année scolaire manquante pour la date de fin."]}

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_end_before_stock_start(self, client, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        start = datetime.utcnow() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=start)

        input_end = start - timedelta(days=1)
        if with_timezone:
            input_end = date_utils.utc_datetime_to_department_timezone(input_end, None)

        payload = {"endDatetime": input_end.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_start_after_stock_end(self, client, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        end = datetime.utcnow() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=end - timedelta(days=1), endDatetime=end
        )

        input_start = end + timedelta(days=1)
        if with_timezone:
            input_start = date_utils.utc_datetime_to_department_timezone(input_start, None)

        payload = {"startDatetime": input_start.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_start_before_stock_booking_limit(self, client, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        start = datetime.utcnow() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=start, bookingLimitDatetime=start - timedelta(days=2)
        )

        input_start = start - timedelta(days=3)
        if with_timezone:
            input_start = date_utils.utc_datetime_to_department_timezone(input_start, None)

        payload = {"startDatetime": input_start.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]
        }

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_booking_limit_after_stock_start(self, client, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        start = datetime.utcnow() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=start)

        input_limit = start + timedelta(days=3)
        if with_timezone:
            input_limit = date_utils.utc_datetime_to_department_timezone(input_limit, None)

        payload = {"bookingLimitDatetime": input_limit.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]
        }

    def test_patch_offer_with_school_location(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        collective_offer = educational_factories.CollectiveOfferOnSchoolLocationFactory(
            venue=venue, provider=venue_provider.provider
        )

        payload = {
            "name": "New name",
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
                f"/v2/collective/offers/{collective_offer.id}", json=payload
            )
        assert response.status_code == 200

        assert "location" in response.json

        assert response.json["location"] == {
            "type": "SCHOOL",
        }

        db.session.refresh(collective_offer)
        assert collective_offer.name == "New name"


@pytest.mark.usefixtures("db_session")
class UpdateOfferVenueTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_change_to_offerer_venue(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        # we accept None for otherAddress but we store "" as our GET schemas expect a string
        dst = self.offer_venue_offerer_venue(venue_provider.venueId)
        expected = {**dst, "otherAddress": ""}

        offer = self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_school(),
            dst=dst,
            expected=expected,
        )

        assert offer.offererAddressId == venue_provider.venue.offererAddressId
        assert offer.locationType == educational_models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_change_to_offerer_venue_other_venue(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        other_venue = offerers_factories.VenueFactory(managingOfferer=venue_provider.venue.managingOfferer)
        other_venue.venueProviders.append(
            providers_models.VenueProvider(venue=other_venue, provider=venue_provider.provider)
        )

        # we accept None for otherAddress but we store "" as our GET schemas expect a string
        dst = self.offer_venue_offerer_venue(other_venue.id)
        expected = {**dst, "otherAddress": ""}

        offer = self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_school(),
            dst=dst,
            expected=expected,
        )

        assert offer.offererAddress.addressId == other_venue.offererAddress.addressId
        assert offer.offererAddress.offererId == other_venue.offererAddress.offererId
        assert offer.offererAddress.label == other_venue.common_name
        assert offer.locationType == educational_models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_change_to_school(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        # we accept None for otherAddress but we store "" as our GET schemas expect a string
        dst = self.offer_venue_school()
        expected = {**dst, "otherAddress": ""}

        offer = self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_other(),
            dst=dst,
            expected=expected,
        )

        assert offer.offererAddressId is None
        assert offer.locationType == educational_models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

    def test_change_to_other_address(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        offer = self.assert_offer_venue_has_been_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_offerer_venue(venue_provider.venueId),
            dst=self.offer_venue_other(),
        )

        assert offer.offererAddressId is None
        assert offer.locationType == educational_models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "something, Somewhereshire"

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

    def test_offer_venue_is_not_updated_when_venue_id_is_unknown(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        self.assert_offer_venue_is_not_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_offerer_venue(venue_provider.venueId),
            payload=self.offer_venue_offerer_venue(-1),
            status_code=404,
            json_error={"venueId": ["Ce lieu n'a pas été trouvé."]},
        )

    def test_offer_venue_is_not_updated_when_venue_id_is_not_allowed(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        other_venue = offerers_factories.VenueFactory()

        self.assert_offer_venue_is_not_updated(
            client=client,
            api_key=plain_api_key,
            venue_provider=venue_provider,
            src=self.offer_venue_offerer_venue(venue_provider.venueId),
            payload=self.offer_venue_offerer_venue(other_venue.id),
            status_code=404,
            json_error={"venueId": ["Ce lieu n'a pas été trouvé."]},
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
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(plain_api_key).patch(
                f"/v2/collective/offers/{offer.id}", json={"offerVenue": self.offer_venue_school()}
            )

        # test says 404 but the implementation says 403 and since we
        # need to implement this abstract method... lets keep it that
        # way (for now).
        assert response.status_code == 403

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass  # Check does not exist for now

    def setup_and_send_request(self, client, api_key, src, payload, venue_provider):
        offer = educational_factories.CollectiveStockFactory(
            collectiveOffer__offerVenue=src,
            collectiveOffer__venue=venue_provider.venue,
            collectiveOffer__provider=venue_provider.provider,
        ).collectiveOffer

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
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

        return offer

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


@pytest.mark.usefixtures("db_session")
class UpdatePriceTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        num_queries = 2  # Select API key + rollback
        super().test_should_raise_401_because_api_key_not_linked_to_provider(client, num_queries=num_queries)

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        pass

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass

    def test_update_price_no_booking(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(self.endpoint_url.format(offer_id=offer.id), json={"totalPrice": 250})

        assert response.status_code == 200
        assert stock.price == 250

    def test_update_price_pending_booking(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(f"/v2/collective/offers/{offer.id}", json={"totalPrice": 250})

        assert response.status_code == 200
        assert stock.price == 250

    def test_update_price_cancelled_booking(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.CancelledCollectiveBookingFactory(collectiveStock=stock)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(f"/v2/collective/offers/{offer.id}", json={"totalPrice": 250})

        assert response.status_code == 200
        assert stock.price == 250

    def test_update_price_used_booking(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.UsedCollectiveBookingFactory(collectiveStock=stock)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(f"/v2/collective/offers/{offer.id}", json={"totalPrice": 150})

        assert response.status_code == 422
        assert response.json == {"global": ["Offre non éditable."]}
        assert stock.price == 200

    def test_update_price_reimbursed_booking(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.ReimbursedCollectiveBookingFactory(collectiveStock=stock)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(f"/v2/collective/offers/{offer.id}", json={"totalPrice": 150})

        assert response.status_code == 422
        assert response.json == {"global": ["Offre non éditable."]}
        assert stock.price == 200

    def test_update_price_confirmed_booking_lower(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)

        new_tickets = stock.numberOfTickets + 10
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(
                f"/v2/collective/offers/{offer.id}",
                json={"totalPrice": 150, "educationalPriceDetail": "hello", "numberOfTickets": new_tickets},
            )

        assert response.status_code == 200
        assert stock.price == 150
        assert stock.priceDetail == "hello"
        assert stock.numberOfTickets == new_tickets

    def test_update_price_confirmed_booking_higher(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(f"/v2/collective/offers/{offer.id}", json={"totalPrice": 250})

        assert response.status_code == 400
        assert response.json == {"price": ["Le prix ne peut pas etre supérieur au prix existant"]}
        assert stock.price == 200

    def test_update_other_field_confirmed_booking(self, client):
        key, venue_provider = self.setup_active_venue_provider()
        client_with_token = client.with_explicit_token(key)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)

        limit = stock.bookingLimitDatetime
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client_with_token.patch(
                f"/v2/collective/offers/{offer.id}",
                json={"bookingLimitDatetime": (limit + timedelta(days=1)).isoformat()},
            )

        assert response.status_code == 400
        assert response.json == {
            "global": ["Seuls les champs totalPrice, educationalPriceDetail, numberOfTickets peuvent être modifiés."]
        }
        assert stock.bookingLimitDatetime == limit


@pytest.mark.usefixtures("db_session")
class AllowedActionsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_401_because_api_key_not_linked_to_provider(self, client):
        pass

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        pass

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_edit_details(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {"name": "New name", "description": "New description"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 200
        db.session.refresh(offer)
        assert offer.name == "New name"
        assert offer.description == "New description"

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_edit_details(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {"name": "New name", "description": "New description"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
        }

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_increase_price(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_price = offer.collectiveStock.price + 100
        payload = {"totalPrice": new_price}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 200
        stock = offer.collectiveStock
        db.session.refresh(stock)
        assert stock.price == new_price

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_increase_price(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_price = offer.collectiveStock.price + 100
        payload = {"totalPrice": new_price}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
        }

    @time_machine.travel(time_travel_str)
    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DATES) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_edit_dates(self, client, status):
        educational_factories.EducationalCurrentYearFactory()
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_limit = datetime.now(timezone.utc) + timedelta(days=10)
        new_start = new_limit + timedelta(days=5)
        new_end = new_limit + timedelta(days=7)
        payload = {
            "bookingLimitDatetime": new_limit.isoformat(),
            "startDatetime": new_start.isoformat(),
            "endDatetime": new_end.isoformat(),
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 200
        stock = offer.collectiveStock
        db.session.refresh(stock)
        assert stock.bookingLimitDatetime == new_limit.replace(tzinfo=None)
        assert stock.startDatetime == new_start.replace(tzinfo=None)
        assert stock.endDatetime == new_end.replace(tzinfo=None)

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DATES) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_edit_dates(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_date = datetime.now(timezone.utc) + timedelta(days=5)
        for date_field in ("bookingLimitDatetime", "startDatetime", "endDatetime"):
            with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
                response = client.with_explicit_token(key).patch(
                    self.endpoint_url.format(offer_id=offer.id), json={date_field: new_date.isoformat()}
                )

            assert response.status_code == 400
            assert response.json == {
                "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
            }

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_INSTITUTION) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_edit_institution(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(
                self.endpoint_url.format(offer_id=offer.id), json={"educationalInstitution": "111"}
            )

        assert response.status_code == 400

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DISCOUNT) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_lower_price_and_edit_price_details(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {"totalPrice": 1, "educationalPriceDetail": "yes", "numberOfTickets": 1200}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(self.endpoint_url.format(offer_id=offer.id), json=payload)

        assert response.status_code == 200
        stock = offer.collectiveStock
        db.session.refresh(stock)
        assert stock.price == 1
        assert stock.priceDetail == "yes"
        assert stock.numberOfTickets == 1200

    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DISCOUNT) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_lower_price_and_edit_price_details(self, client, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        for payload in ({"totalPrice": 1}, {"educationalPriceDetail": "yes", "numberOfTickets": 1200}):
            with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
                response = client.with_explicit_token(key).patch(
                    self.endpoint_url.format(offer_id=offer.id), json=payload
                )

            assert response.status_code == 400
            assert response.json == {
                "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
            }

    @time_machine.travel(time_travel_str)
    @pytest.mark.features(WIP_ENABLE_COLLECTIVE_NEW_STATUS_PUBLIC_API=True)
    @pytest.mark.parametrize(
        "field,value",
        (
            ("educationalInstitution", "111"),
            ("educationalInstitutionId", 1),
            ("bookingLimitDatetime", "2021-11-01 15:00:00"),
            ("startDatetime", "2021-11-01 15:00:00"),
            ("endDatetime", "2021-11-01 15:00:00"),
            ("name", "New name"),
            ("totalPrice", 2000),  # increase price
            ("totalPrice", 1),  # decrease price
            ("educationalPriceDetail", "yes"),
            ("numberOfTickets", 1200),
        ),
    )
    def test_unallowed_action_archived(self, client, field, value):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.ArchivedPublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_explicit_token(key).patch(
                self.endpoint_url.format(offer_id=offer.id), json={field: value}
            )

        assert response.status_code == 400
        assert response.json == {"global": "Cette action n'est pas autorisée car le statut de l'offre est ARCHIVED"}
