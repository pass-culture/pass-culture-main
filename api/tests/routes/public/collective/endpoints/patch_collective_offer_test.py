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
from pcapi.core.geography import factories as geography_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import factories as provider_factories
from pcapi.models import db
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
# the ARCHIVED status must be tested separately as we need the ArchivedPublishedCollectiveOfferFactory factory
STATUSES_NOT_IN_PUBLIC_API = {
    educational_models.CollectiveOfferDisplayedStatus.DRAFT,
    educational_models.CollectiveOfferDisplayedStatus.ARCHIVED,
}

time_travel_str = "2021-10-01 15:00:00"


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicPatchOfferTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

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
    def test_patch_offer(self):
        educational_factories.EducationalCurrentYearFactory()
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        other_venue_provider = provider_factories.VenueProviderFactory(
            provider=venue_provider.provider, venue__managingOfferer=venue.managingOfferer, venue__pricing_point=venue
        )
        other_venue = other_venue_provider.venue

        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])
        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet",
            imageId="123456789",
            venue=venue,
            provider=venue_provider.provider,
            nationalProgramId=None,
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

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
            "location": {"type": educational_models.CollectiveLocationType.SCHOOL.value},
            "interventionArea": ["33", "75"],
            "imageCredit": "a great artist",
            "nationalProgramId": national_program.id,
            # stock part
            "startDatetime": stock.startDatetime.isoformat(timespec="seconds"),
            "endDatetime": stock.endDatetime.isoformat(timespec="seconds"),
            "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(timespec="seconds"),
            "totalPrice": 96.25,
            "numberOfTickets": 30,
            "educationalPriceDetail": "Justification du prix",
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

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
        assert offer.interventionArea == ["33", "75"]
        assert offer.audioDisabilityCompliant is True
        assert offer.mentalDisabilityCompliant is True
        assert offer.motorDisabilityCompliant is True
        assert offer.visualDisabilityCompliant is True
        assert offer.hasImage is True
        assert offer.imageCredit == "a great artist"
        assert offer.nationalProgramId == national_program.id

        assert offer.collectiveStock.startDatetime == datetime.fromisoformat(payload["startDatetime"])
        assert offer.collectiveStock.endDatetime == datetime.fromisoformat(payload["endDatetime"])
        assert offer.collectiveStock.bookingLimitDatetime == datetime.fromisoformat(payload["bookingLimitDatetime"])
        assert offer.collectiveStock.price == Decimal(payload["totalPrice"])
        assert offer.collectiveStock.priceDetail == payload["educationalPriceDetail"]

    @pytest.mark.parametrize("field", NON_REQUIRED_NON_NULLABLE_FIELDS)
    def test_non_nullable_field(self, field):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={field: None})

        assert response.status_code == 400
        assert response.json == {field: ["Ce champ peut ne pas être présent mais ne peut pas être null."]}

    @pytest.mark.parametrize("field,error", NON_REQUIRED_NON_NULLABLE_FIELDS_CUSTOM_ERROR.items())
    def test_non_nullable_field_custom_error(self, field, error):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={field: None})

        assert response.status_code == 400
        assert response.json == {field: [error]}

    def test_change_venue(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        other_venue_provider = provider_factories.VenueProviderFactory(
            provider=venue_provider.provider, venue__managingOfferer=venue.managingOfferer, venue__pricing_point=venue
        )
        other_venue = other_venue_provider.venue

        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, provider=venue_provider.provider)

        payload = {"venueId": other_venue.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=offer.id).one()
        assert offer.venueId == other_venue.id

    def test_update_venue_does_nothing_if_unchanged(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, provider=venue_provider.provider)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            with patch("pcapi.core.educational.api.offer.move_collective_offer_venue") as move_mock:
                response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={"venueId": venue.id})

        move_mock.assert_not_called()
        assert response.status_code == 200
        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=offer.id).one()
        assert offer.venueId == venue.id

    def test_change_venue_error(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        # venue with different pricing point
        other_venue_provider = provider_factories.VenueProviderFactory(
            provider=venue_provider.provider, venue__managingOfferer=venue.managingOfferer
        )
        other_venue = other_venue_provider.venue

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, provider=venue_provider.provider)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body={"venueId": other_venue.id})

        assert response.status_code == 400
        assert response.json == {"venueId": ["L'offre ne peut pas être déplacée sur ce lieu."]}

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=offer.id).one()
        assert offer.venueId == venue.id

    @time_machine.travel(time_travel_str)
    def test_should_update_endDatetime_and_startDatetime(self):
        educational_factories.EducationalCurrentYearFactory()

        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        next_month = date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + timedelta(days=30)
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
            response = self.make_request(plain_api_key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()

        assert offer.collectiveStock.startDatetime == next_month_minus_one_day
        assert offer.collectiveStock.endDatetime == next_month

    def test_should_raise_400_because_endDatetime_is_before_startDatetime(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(
            imageCredit="pouet", imageId="123456789", venue=venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        next_month = date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + timedelta(days=30)
        next_month_minus_one_day = next_month - timedelta(days=1)

        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(next_month, None).isoformat(),
            "endDatetime": date_utils.utc_datetime_to_department_timezone(next_month_minus_one_day, None).isoformat(),
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    def test_should_raise_400_because_booking_limit_is_after_start(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        new_start = date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + timedelta(days=30)
        new_end = new_start + timedelta(days=10)
        new_limit = new_start + timedelta(days=5)

        payload = {
            "startDatetime": date_utils.utc_datetime_to_department_timezone(new_start, None).isoformat(),
            "endDatetime": date_utils.utc_datetime_to_department_timezone(new_end, None).isoformat(),
            "bookingLimitDatetime": date_utils.utc_datetime_to_department_timezone(new_limit, None).isoformat(),
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "bookingLimitDatetime": [
                "La date limite de réservation ne peut être postérieure à la date de début de l'évènement"
            ]
        }

    def test_patch_offer_uai_and_institution_id(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

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
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "__root__": [
                "Les champs educationalInstitution et educationalInstitutionId sont mutuellement exclusifs. "
                "Vous ne pouvez pas remplir les deux en même temps"
            ]
        }

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.institutionId is None

    def test_patch_offer_invalid_offerer(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=provider_factories.ProviderFactory())
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"description": "une description d'offre"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette offre collective."]
        }

    def test_patch_offer_invalid_phone_number(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"contactPhone": "NOT A PHONE NUMBER"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"contactPhone": ["Ce numéro de telephone ne semble pas valide"]}

    def test_add_valid_image(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_add_invalid_image_size(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_SIZE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"imageFile": ["L'image doit faire exactement 400*600 pixels"]}

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_add_invalid_image_type(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"name": "pouet", "imageCredit": "a great artist", "imageFile": image_data.WRONG_IMAGE_TYPE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"imageFile": ["Les formats acceptés sont:  png, jpg, jpeg, mpo, webp"]}

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.name != "pouet"

    def test_delete_image(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        offer = educational_factories.CollectiveOfferFactory(venue=venue, provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"imageCredit": "a great artist", "imageFile": image_data.GOOD_IMAGE}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)
        assert response.status_code == 200

        offer = db.session.query(educational_models.CollectiveOffer).filter_by(id=stock.collectiveOffer.id).one()
        assert offer.hasImage is True
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        # END SETUP

        # actual test
        payload = {"imageFile": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(plain_api_key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 200
        assert offer.hasImage is False
        assert not (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    @pytest.mark.parametrize("input_with_timezone", (True, False))
    def test_should_update_expired_booking(self, input_with_timezone):
        now = date_utils.get_naive_utc_now()
        limit = now - timedelta(days=2)

        key, venue_provider = self.setup_active_venue_provider()
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
        limit_in_payload = new_limit.isoformat()
        if input_with_timezone:
            limit_in_payload = limit_in_payload + "Z"
        payload = {"bookingLimitDatetime": limit_in_payload}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)
            assert response.status_code == 200

        db.session.refresh(stock)
        db.session.refresh(booking)
        assert stock.bookingLimitDatetime == new_limit
        assert booking.status == educational_models.CollectiveBookingStatus.PENDING
        assert booking.cancellationReason == None
        assert booking.cancellationDate == None
        assert booking.confirmationLimitDate == new_limit

    def test_description_invalid(self):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body={"description": "too_long" * 200})

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    @time_machine.travel(time_travel_str)
    def test_different_educational_years(self):
        key, venue_provider = self.setup_active_venue_provider()

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
            response = self.make_request(key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

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
            response = self.make_request(key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

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
            response = self.make_request(key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["Les dates de début et de fin ne sont pas sur la même année scolaire."]}
        db.session.refresh(stock)
        assert stock.startDatetime == stock_start
        assert stock.endDatetime == stock_end

    @time_machine.travel(time_travel_str)
    def test_educational_year_missing_start(self):
        key, venue_provider = self.setup_active_venue_provider()

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"startDatetime": stock.startDatetime.replace(stock.startDatetime.year + 1).isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"startDatetime": ["Année scolaire manquante pour la date de début."]}

    @time_machine.travel(time_travel_str)
    def test_educational_year_missing_end(self):
        key, venue_provider = self.setup_active_venue_provider()

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        payload = {"endDatetime": stock.endDatetime.replace(stock.endDatetime.year + 1).isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": stock.collectiveOffer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"endDatetime": ["Année scolaire manquante pour la date de fin."]}

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_end_before_stock_start(self, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        start = date_utils.get_naive_utc_now() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=start)

        input_end = start - timedelta(days=1)
        if with_timezone:
            input_end = date_utils.utc_datetime_to_department_timezone(input_end, None)

        payload = {"endDatetime": input_end.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_start_after_stock_end(self, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        end = date_utils.get_naive_utc_now() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=end - timedelta(days=1), endDatetime=end
        )

        input_start = end + timedelta(days=1)
        if with_timezone:
            input_start = date_utils.utc_datetime_to_department_timezone(input_start, None)

        payload = {"startDatetime": input_start.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"global": ["La date de fin de l'évènement ne peut précéder la date de début."]}

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_start_before_stock_booking_limit(self, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        start = date_utils.get_naive_utc_now() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(
            collectiveOffer=offer, startDatetime=start, bookingLimitDatetime=start - timedelta(days=2)
        )

        input_start = start - timedelta(days=3)
        if with_timezone:
            input_start = date_utils.utc_datetime_to_department_timezone(input_start, None)

        payload = {"startDatetime": input_start.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]
        }

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize("with_timezone", [True, False])
    def test_booking_limit_after_stock_start(self, with_timezone):
        key, venue_provider = self.setup_active_venue_provider()

        educational_factories.EducationalCurrentYearFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        start = date_utils.get_naive_utc_now() + timedelta(days=5)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=start)

        input_limit = start + timedelta(days=3)
        if with_timezone:
            input_limit = date_utils.utc_datetime_to_department_timezone(input_limit, None)

        payload = {"bookingLimitDatetime": input_limit.isoformat()}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": ["La date limite de réservation ne peut être postérieure à la date de début de l'évènement"]
        }

    def test_patch_offer_update_to_school_location(self):
        key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        collective_offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider
        )
        payload = {"location": {"type": "SCHOOL"}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": collective_offer.id}, json_body=payload)
        assert response.status_code == 200

        assert response.json["location"] == {"type": "SCHOOL"}

        db.session.refresh(collective_offer)
        assert collective_offer.locationType == educational_models.CollectiveLocationType.SCHOOL
        assert collective_offer.locationComment is None
        assert collective_offer.offererAddressId is None

    def test_patch_offer_update_to_to_be_defined_location(self):
        key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        collective_offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider
        )

        payload = {"location": {"type": "TO_BE_DEFINED", "comment": "In Paris"}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": collective_offer.id}, json_body=payload)
        assert response.status_code == 200

        assert response.json["location"] == {"type": "TO_BE_DEFINED", "comment": "In Paris"}

        db.session.refresh(collective_offer)
        assert collective_offer.locationType == educational_models.CollectiveLocationType.TO_BE_DEFINED
        assert collective_offer.locationComment == "In Paris"
        assert collective_offer.offererAddressId is None

    def test_patch_offer_update_to_address_on_venue_location(self):
        key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        collective_offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider
        )

        payload = {"location": {"type": "ADDRESS", "isVenueAddress": True}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": collective_offer.id}, json_body=payload)
        assert response.status_code == 200

        assert response.json["location"] == {"type": "ADDRESS", "isVenueAddress": True}

        db.session.refresh(collective_offer)
        assert collective_offer.locationType == educational_models.CollectiveLocationType.ADDRESS
        assert collective_offer.locationComment is None
        assert collective_offer.offererAddress.type is None  # TODO: soon to be OFFER_LOCATION
        assert collective_offer.offererAddressId != venue.offererAddress.id
        assert collective_offer.offererAddress.addressId == venue.offererAddress.addressId
        assert collective_offer.offererAddress.label == venue.publicName

    def test_patch_offer_update_to_address_on_other_location(self):
        key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        collective_offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider
        )

        address = geography_factories.AddressFactory(street="123 rue de la paix", postalCode="75000", city="Paris")

        payload = {
            "location": {
                "type": "ADDRESS",
                "isVenueAddress": False,
                "addressLabel": "My second address",
                "addressId": address.id,
            }
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": collective_offer.id}, json_body=payload)
        assert response.status_code == 200

        assert response.json["location"] == {
            "type": "ADDRESS",
            "isVenueAddress": False,
            "addressLabel": "My second address",
            "addressId": address.id,
        }

        offerer_address = (
            db.session.query(offerers_models.OffererAddress)
            .filter_by(addressId=address.id, offererId=venue.managingOffererId)
            .one()
        )

        db.session.refresh(collective_offer)
        assert offerer_address.label == "My second address"

        assert collective_offer.locationType == educational_models.CollectiveLocationType.ADDRESS
        assert collective_offer.locationComment is None
        assert not collective_offer.offererAddress == venue.offererAddress
        assert collective_offer.offererAddress == offerer_address

    @pytest.mark.parametrize(
        "location,error",
        [
            (None, "Ce champ peut ne pas être présent mais ne peut pas être null."),
            (1, "Le champ location doit être un objet"),
            ({}, "Le champ type est requis"),
            ({"type": "bloup"}, "Les valeurs autorisées pour le champ type sont SCHOOL, ADDRESS, TO_BE_DEFINED"),
            ({"type": "SCHOOL", "isVenueAddress": True}, "Quand type=SCHOOL, aucun autre champ n'est accepté"),
            (
                {"type": "ADDRESS", "locationComment": "hello"},
                "Quand type=ADDRESS, seuls les champs isVenueAddress, addressId, addressLabel sont acceptés",
            ),
            ({"type": "ADDRESS"}, "Quand type=ADDRESS, isVenueAddress est requis"),
            (
                {"type": "ADDRESS", "isVenueAddress": True, "addressId": 1},
                "Quand type=ADDRESS et isVenueAddress=true, aucun autre champ n'est accepté",
            ),
            (
                {"type": "ADDRESS", "isVenueAddress": False},
                "Quand type=ADDRESS et isVenueAddress=false, le champ addressId est requis",
            ),
            ({"type": "TO_BE_DEFINED", "addressId": 1}, "Quand type=TO_BE_DEFINED, seul le champ comment est accepté"),
        ],
    )
    def test_patch_location_invalid(self, location, error):
        key, venue_provider = self.setup_active_venue_provider()
        venue = offerers_factories.VenueFactory(venueProviders=[venue_provider])
        collective_offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, provider=venue_provider.provider
        )

        payload = {"location": location}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": collective_offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"location": [error]}


@pytest.mark.usefixtures("db_session")
class UpdatePriceTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        pass

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass

    def test_update_price_no_booking(self):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body={"totalPrice": 250})

        assert response.status_code == 200
        assert stock.price == 250

    def test_update_price_pending_booking(self):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.PendingCollectiveBookingFactory(collectiveStock=stock)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body={"totalPrice": 250})

        assert response.status_code == 200
        assert stock.price == 250

    def test_update_price_confirmed_booking_lower(self):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer, price=200)
        educational_factories.ConfirmedCollectiveBookingFactory(collectiveStock=stock)

        new_tickets = stock.numberOfTickets + 10
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(
                key,
                {"offer_id": offer.id},
                json_body={"totalPrice": 150, "educationalPriceDetail": "hello", "numberOfTickets": new_tickets},
            )

        assert response.status_code == 200
        assert stock.price == 150
        assert stock.priceDetail == "hello"
        assert stock.numberOfTickets == new_tickets


@pytest.mark.usefixtures("db_session")
class AllowedActionsTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        pass

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_edit_details(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {"name": "New name", "description": "New description"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        db.session.refresh(offer)
        assert offer.name == "New name"
        assert offer.description == "New description"

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_edit_details(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {"name": "New name", "description": "New description"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
        }

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_increase_price(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_price = offer.collectiveStock.price + 100
        payload = {"totalPrice": new_price}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        stock = offer.collectiveStock
        db.session.refresh(stock)
        assert stock.price == new_price

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_increase_price(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_price = offer.collectiveStock.price + 100
        payload = {"totalPrice": new_price}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {
            "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
        }

    @time_machine.travel(time_travel_str)
    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DATES) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_edit_dates(self, status):
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
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        stock = offer.collectiveStock
        db.session.refresh(stock)
        assert stock.bookingLimitDatetime == new_limit.replace(tzinfo=None)
        assert stock.startDatetime == new_start.replace(tzinfo=None)
        assert stock.endDatetime == new_end.replace(tzinfo=None)

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DATES) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_edit_dates(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        new_date = datetime.now(timezone.utc) + timedelta(days=5)
        for date_field in ("bookingLimitDatetime", "startDatetime", "endDatetime"):
            with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
                response = self.make_request(key, {"offer_id": offer.id}, json_body={date_field: new_date.isoformat()})

            assert response.status_code == 400
            assert response.json == {
                "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
            }

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_INSTITUTION) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_edit_institution(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body={"educationalInstitution": "111"})

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_ALLOWING_EDIT_DISCOUNT) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_allowed_action_lower_price_and_edit_price_details(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        payload = {"totalPrice": 1, "educationalPriceDetail": "yes", "numberOfTickets": 1200}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        stock = offer.collectiveStock
        db.session.refresh(stock)
        assert stock.price == 1
        assert stock.priceDetail == "yes"
        assert stock.numberOfTickets == 1200

    @pytest.mark.parametrize(
        "status", set(educational_testing.STATUSES_NOT_ALLOWING_EDIT_DISCOUNT) - STATUSES_NOT_IN_PUBLIC_API
    )
    def test_unallowed_action_lower_price_and_edit_price_details(self, status):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.create_collective_offer_by_status(
            status, venue=venue_provider.venue, provider=venue_provider.provider
        )

        for payload in ({"totalPrice": 1}, {"educationalPriceDetail": "yes", "numberOfTickets": 1200}):
            with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
                response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

            assert response.status_code == 400
            assert response.json == {
                "global": f"Cette action n'est pas autorisée car le statut de l'offre est {status.value}"
            }

    @time_machine.travel(time_travel_str)
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
    def test_unallowed_action_archived(self, field, value):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.ArchivedPublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body={field: value})

        assert response.status_code == 400
        assert response.json == {"global": "Cette action n'est pas autorisée car le statut de l'offre est ARCHIVED"}


@pytest.mark.usefixtures("db_session")
class DomainsAndNationalProgramTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1}

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        pass

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        pass

    def test_update_domains_unknown(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider, domains=[current_domain]
        )

        payload = {"domains": [0]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 404
        assert response.json == {"domains": ["Domaine scolaire non trouvé."]}
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_update_domains_empty(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider, domains=[current_domain]
        )

        payload = {"domains": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_update_program_unknown(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider, nationalProgram=current_program
        )

        payload = {"nationalProgramId": 0}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif inconnu"]}
        assert offer.nationalProgramId == current_program.id

    def test_update_program_null(self):
        key, venue_provider = self.setup_active_venue_provider()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=educational_factories.NationalProgramFactory(),
        )

        payload = {"nationalProgramId": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        assert offer.nationalProgramId is None

    def test_update_program(self):
        key, venue_provider = self.setup_active_venue_provider()
        new_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[new_program])
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue, provider=venue_provider.provider, domains=[current_domain]
        )

        payload = {"nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        assert offer.nationalProgramId == new_program.id
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_update_domains(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=current_program,
            domains=[current_domain],
        )

        payload = {"domains": [new_domain.id]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        assert offer.nationalProgramId == current_program.id
        assert [domain.id for domain in offer.domains] == [new_domain.id]

    def test_update_domains_and_program(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_program = educational_factories.NationalProgramFactory()
        new_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[new_program])
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=current_program,
            domains=[current_domain],
        )

        payload = {"domains": [new_domain.id], "nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 200
        assert offer.nationalProgramId == new_program.id
        assert [domain.id for domain in offer.domains] == [new_domain.id]

    def test_update_program_inactive(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        new_program = educational_factories.NationalProgramFactory(isActive=False)
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program, new_program])
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=current_program,
            domains=[current_domain],
        )

        payload = {"nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif national inactif."]}
        assert offer.nationalProgramId == current_program.id
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_update_program_invalid(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=current_program,
            domains=[current_domain],
        )

        payload = {"nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif national non valide."]}
        assert offer.nationalProgramId == current_program.id
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_update_domains_invalid(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=current_program,
            domains=[current_domain],
        )

        payload = {"domains": [new_domain.id]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif national non valide."]}
        assert offer.nationalProgramId == current_program.id
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_update_domains_and_program_invalid(self):
        key, venue_provider = self.setup_active_venue_provider()
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_program = educational_factories.NationalProgramFactory()
        new_domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            nationalProgram=current_program,
            domains=[current_domain],
        )

        payload = {"domains": [new_domain.id], "nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = self.make_request(key, {"offer_id": offer.id}, json_body=payload)

        assert response.status_code == 400
        assert response.json == {"nationalProgramId": ["Dispositif national non valide."]}
        assert [domain.id for domain in offer.domains] == [current_domain.id]
        assert offer.nationalProgramId == current_program.id
