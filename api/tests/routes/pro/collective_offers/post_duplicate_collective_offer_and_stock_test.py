import datetime
from pathlib import Path
from unittest import mock

import pytest

from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.exceptions import CantGetImageFromUrl
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.users import factories as user_factories
from pcapi.models import db
from pcapi.models import validation_status_mixin
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils.date import format_into_utc_date

import tests


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER

STATUSES_NOT_ALLOWING_DUPLICATE = (educational_models.CollectiveOfferDisplayedStatus.DRAFT,)

STATUSES_ALLOWING_DUPLICATE = tuple(
    set(educational_models.CollectiveOfferDisplayedStatus)
    - {*STATUSES_NOT_ALLOWING_DUPLICATE, educational_models.CollectiveOfferDisplayedStatus.HIDDEN}
)


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
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert response.status_code == 201
        assert response.json["imageCredit"] == offer.imageCredit
        assert response.json["imageUrl"] == duplicate.imageUrl

    def test_duplicate_collective_offer(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            institution=institution,
            nationalProgram=national_program,
            domains=[domain],
        )
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
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
            "contactEmail": "collectiveofferfactory+contact@example.com",
            "contactPhone": "+33199006328",
            "isPublicApi": False,
            "id": duplicate.id,
            "name": offer.name,
            "venue": {
                "departementCode": "75",
                "managingOfferer": {
                    "id": offerer.id,
                    "name": venue.managingOfferer.name,
                    "siren": venue.managingOfferer.siren,
                },
                "id": venue.id,
                "imgUrl": None,
                "name": venue.name,
                "publicName": venue.publicName,
            },
            "displayedStatus": "DRAFT",
            "domains": [{"id": domain.id, "name": domain.name}],
            "interventionArea": ["93", "94", "95"],
            "imageCredit": None,
            "imageUrl": None,
            "collectiveStock": {
                "id": duplicate.collectiveStock.id,
                "startDatetime": format_into_utc_date(offer.collectiveStock.startDatetime),
                "endDatetime": format_into_utc_date(offer.collectiveStock.endDatetime),
                "bookingLimitDatetime": format_into_utc_date(offer.collectiveStock.bookingLimitDatetime),
                "price": 100.0,
                "numberOfTickets": 25,
                "educationalPriceDetail": offer.collectiveStock.priceDetail,
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
            "templateId": None,
            "booking": None,
            "teacher": None,
            "nationalProgram": {"id": national_program.id, "name": national_program.name},
            "provider": None,
            "formats": [fmt.value for fmt in duplicate.formats],
            "isTemplate": False,
            "dates": {
                "end": format_into_utc_date(offer.collectiveStock.endDatetime),
                "start": format_into_utc_date(offer.collectiveStock.startDatetime),
            },
            "allowedActions": [
                "CAN_EDIT_DETAILS",
                "CAN_EDIT_DATES",
                "CAN_EDIT_INSTITUTION",
                "CAN_EDIT_DISCOUNT",
                "CAN_ARCHIVE",
            ],
            "location": {
                "location": None,
                "locationComment": None,
                "locationType": "TO_BE_DEFINED",
            },
            "history": {
                "future": [
                    "PUBLISHED",
                    "PREBOOKED",
                    "BOOKED",
                    "ENDED",
                    "REIMBURSED",
                ],
                "past": [
                    {"datetime": None, "status": "DRAFT"},
                ],
            },
        }

    @pytest.mark.parametrize("status", STATUSES_ALLOWING_DUPLICATE)
    def test_duplicate_allowed_action(self, client, status):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.create_collective_offer_by_status(status=status, venue=venue)

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer.id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert duplicate.name == offer.name

    def test_duplicate_ended(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.EndedCollectiveOfferConfirmedBookingFactory(venue=venue)

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer.id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert duplicate.name == offer.name

    @pytest.mark.parametrize("status", STATUSES_NOT_ALLOWING_DUPLICATE)
    def test_duplicate_unallowed_action(self, client, status):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.create_collective_offer_by_status(status=status, venue=venue)

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer.id}/duplicate")

        assert response.status_code == 403
        assert response.json == {"validation": ["Cette action n'est pas autorisée sur cette offre"]}

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

    def test_duplicate_collective_offer_validation_information(self, client):
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

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert duplicate.validation == offers_models.OfferValidationStatus.DRAFT
        assert duplicate.lastValidationDate is None
        assert duplicate.lastValidationType is None
        assert duplicate.lastValidationAuthorUserId is None

    def test_duplicate_collective_offer_inactive_program(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        national_program = educational_factories.NationalProgramFactory(isActive=False)
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, nationalProgram=national_program, domains=[domain]
        )

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer.id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert duplicate.domains == [domain]
        assert duplicate.nationalProgramId is None

    def test_duplicate_collective_offer_invalid_program(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue, nationalProgram=national_program, domains=[domain]
        )

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer.id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert duplicate.domains == [domain]
        assert duplicate.nationalProgramId is None

    def test_duplicate_collective_offer_missing_domains(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        national_program = educational_factories.NationalProgramFactory()
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue, nationalProgram=national_program)

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer.id}/duplicate")

        assert response.status_code == 201
        duplicate = db.session.query(educational_models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert duplicate.domains == []
        assert duplicate.nationalProgramId is None
