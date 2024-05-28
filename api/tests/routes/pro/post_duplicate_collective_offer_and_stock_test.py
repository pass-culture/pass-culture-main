import datetime
from pathlib import Path
from unittest import mock

import pytest

from pcapi import settings
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import CantGetImageFromUrl
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.users import factories as user_factories
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils.date import format_into_utc_date

import tests


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def teardown_method(self, *args):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / educational_models.CollectiveOffer.__name__.lower()
        if storage_folder.exists():
            for child in storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()

    def test_duplicate_collective_offer_image(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        image_oiseau_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            imageId="00000125999998",
            imageCredit="vision d'horreur selon Hitchcock",
            imageCrop={"gnagna": "Non"},
            imageHasOriginal=False,
        )

        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        with mock.patch("pcapi.core.educational.api.offer.get_image_from_url", return_value=image_oiseau_bytes):
            response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        # Then
        duplicate = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert response.status_code == 201
        assert response.json["imageCredit"] == offer.imageCredit
        assert response.json["imageUrl"] == duplicate.imageUrl

    def test_duplicate_collective_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue=venue,
            institution=institution,
            nationalProgram=national_program,
        )
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When
        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        # Then
        assert response.status_code == 201
        duplicate = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert response.json == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "bookingEmails": [
                "collectiveofferfactory+booking@example.com",
                "collectiveofferfactory+booking@example2.com",
            ],
            "dateCreated": format_into_utc_date(duplicate.dateCreated),
            "description": offer.description,
            "durationMinutes": None,
            "students": ["Lycée - Seconde"],
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
            "contactEmail": "collectiveofferfactory+contact@example.com",
            "contactPhone": "+33199006328",
            "hasBookingLimitDatetimesPassed": False,
            "offerId": None,
            "isActive": False,
            "isEditable": True,
            "isPublicApi": False,
            "id": duplicate.id,
            "name": offer.name,
            "subcategoryId": offer.subcategoryId,
            "isNonFreeOffer": None,
            "venue": {
                "departementCode": "75",
                "managingOfferer": {
                    "id": offerer.id,
                    "name": venue.managingOfferer.name,
                    "allowedOnAdage": venue.managingOfferer.allowedOnAdage,
                    "siren": venue.managingOfferer.siren,
                },
                "id": venue.id,
                "imgUrl": None,
                "name": venue.name,
                "publicName": venue.publicName,
            },
            "status": "DRAFT",
            "domains": [],
            "interventionArea": ["93", "94", "95"],
            "isCancellable": False,
            "imageCredit": None,
            "imageUrl": None,
            "isBookable": False,
            "collectiveStock": {
                "id": duplicate.collectiveStock.id,
                "isBooked": False,
                "isCancellable": False,
                "beginningDatetime": format_into_utc_date(offer.collectiveStock.beginningDatetime),
                "endDatetime": None,
                "startDatetime": None,
                "bookingLimitDatetime": format_into_utc_date(offer.collectiveStock.bookingLimitDatetime),
                "price": 100.0,
                "numberOfTickets": 25,
                "educationalPriceDetail": None,
                "isEducationalStockEditable": True,
            },
            "institution": {
                "id": duplicate.institution.id,
                "name": duplicate.institution.name,
                "institutionType": duplicate.institution.institutionType,
                "postalCode": duplicate.institution.postalCode,
                "city": duplicate.institution.city,
                "phoneNumber": duplicate.institution.phoneNumber,
                "institutionId": duplicate.institution.institutionId,
            },
            "isVisibilityEditable": True,
            "templateId": None,
            "lastBookingStatus": None,
            "lastBookingId": None,
            "teacher": None,
            "nationalProgram": {"id": national_program.id, "name": national_program.name},
            "provider": None,
            "formats": [fmt.value for fmt in subcategories.SEANCE_CINE.formats],
            "isTemplate": False,
        }

    def test_duplicate_collective_offer_without_subcategoryId(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        formats = ["CONCERT"]
        offer = educational_factories.CollectiveOfferFactory(subcategoryId=None, venue=venue, formats=formats)
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When
        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        # Then
        assert response.status_code == 201
        assert response.json.get("formats") == ["Concert"]

    def test_duplicate_collective_offer_draft_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.DRAFT,
        )
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        assert response.status_code == 403
        assert response.json == {"validation": ["l'offre ne passe pas la validation"]}

    def test_duplicate_collective_offer_offerer_not_validated(self, client):
        # Given
        offerer = offerers_factories.OffererFactory(
            validationStatus=validation_status_mixin.ValidationStatus.REJECTED,
        )
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue)
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        assert response.status_code == 403
        assert response.json == {"offerer": ["la structure n'est pas autorisée à dupliquer l'offre"]}

    def test_duplicate_collective_offer_image_not_found(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            imageId="00000125999998",
            imageCredit="vision d'horreur selon Hitchcock",
            imageCrop={"gnagna": "Non"},
            imageHasOriginal=False,
        )

        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        with mock.patch(
            "pcapi.core.educational.api.offer.get_image_from_url",
            side_effect=CantGetImageFromUrl,
        ):
            response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        # Then
        assert response.status_code == 404

    def test_duplicate_collective_offer_validation_informations(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        user = user_factories.BaseUserFactory()
        lastValidationDate = datetime.date.today() - datetime.timedelta(days=2)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            institution=institution,
            nationalProgram=national_program,
            validation=offers_models.OfferValidationStatus.APPROVED,
            lastValidationType=OfferValidationType.MANUAL,
            lastValidationDate=lastValidationDate,
            lastValidationAuthorUserId=user.id,
        )
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When
        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        # Then
        assert response.status_code == 201
        duplicate = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert duplicate.lastValidationDate.date() == lastValidationDate
        assert duplicate.validation == offers_models.OfferValidationStatus.DRAFT
        assert duplicate.lastValidationType == OfferValidationType.MANUAL
        assert not duplicate.lastValidationAuthorUserId
