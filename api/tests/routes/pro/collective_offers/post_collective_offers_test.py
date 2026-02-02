from unittest.mock import patch

import pytest

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def base_offer_payload(
    venue,
    domain_ids=None,
    template_id=None,
    national_program_id=None,
    formats=None,
    add_domain_to_program=True,
) -> dict:
    if domain_ids is None:
        domain_ids = [educational_factories.EducationalDomainFactory().id]

    if not national_program_id and domain_ids:
        national_program_id = educational_factories.NationalProgramFactory().id

    if national_program_id and add_domain_to_program:
        educational_factories.DomainToNationalProgramFactory(
            nationalProgramId=national_program_id, domainId=domain_ids[0]
        )

    if formats is None:
        formats = [EacFormat.CONCERT.value]

    return {
        "venueId": venue.id,
        "description": "Ma super description",
        "bookingEmails": ["offer1@example.com", "offer2@example.com"],
        "domains": domain_ids,
        "durationMinutes": 60,
        "name": "La pièce de théâtre",
        "contactEmail": "pouet@example.com",
        "contactPhone": "01 99 00 25 68",
        "location": {
            "locationType": models.CollectiveLocationType.SCHOOL.value,
            "locationComment": None,
            "location": None,
        },
        "students": ["Lycée - Seconde", "Lycée - Première"],
        "audioDisabilityCompliant": False,
        "mentalDisabilityCompliant": True,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
        "interventionArea": ["75", "92", "93"],
        "templateId": template_id,
        "nationalProgramId": national_program_id,
        "formats": formats,
    }


def assert_offer_values(offer: models.CollectiveOffer, data, user, offerer):
    # if there is no booking emails and the offer is build from a
    # template, the booking emails are set using the contact email
    if not data["bookingEmails"] and data["templateId"]:
        if data["contactEmail"]:
            assert offer.bookingEmails == [data["contactEmail"]]
        else:
            assert offer.bookingEmails == []
    else:
        assert set(offer.bookingEmails) == set(data["bookingEmails"])
    assert offer.venueId == data["venueId"]
    assert offer.durationMinutes == data["durationMinutes"]
    assert offer.venue.managingOffererId == offerer.id
    assert offer.motorDisabilityCompliant == data["motorDisabilityCompliant"]
    assert offer.visualDisabilityCompliant == data["visualDisabilityCompliant"]
    assert offer.audioDisabilityCompliant == data["audioDisabilityCompliant"]
    assert offer.mentalDisabilityCompliant == data["mentalDisabilityCompliant"]
    assert offer.contactEmail == data["contactEmail"]
    assert offer.contactPhone == data["contactPhone"]
    assert offer.locationType == models.CollectiveLocationType[data["location"]["locationType"]]
    assert offer.locationComment == data["location"]["locationComment"]
    assert offer.interventionArea == data["interventionArea"]
    assert {st.value for st in offer.students} == set(data["students"])
    assert {d.id for d in offer.domains} == set(data["domains"])
    assert offer.description == data["description"]
    assert offer.templateId == data["templateId"]
    assert offer.author.full_name == user.full_name
    assert offer.nationalProgramId == data["nationalProgramId"]
    assert {fmt.value for fmt in offer.formats} == set(data["formats"])


class Returns200Test:
    def test_create_collective_offer(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        data = base_offer_payload(venue=venue)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = db.session.get(models.CollectiveOffer, offer_id)

        assert_offer_values(offer, data, user, offerer)

        # 2 requests (for 2 bookingEmail) for sendinblue
        assert len(sendinblue_testing.sendinblue_requests) == 3

    def test_create_collective_offer_allowed_one_adage(self, client):
        # offerer is allowed on adage but has no venue with adageId
        # this can happen if the venue with adageId has been soft-deleted
        offerer = offerers_factories.OffererFactory(allowedOnAdage=True)
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, adageId=None)

        data = base_offer_payload(venue=venue)
        with patch("pcapi.core.educational.adage_backends.get_adage_offerer") as get_adage_offerer_mock:
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        get_adage_offerer_mock.assert_not_called()

        assert response.status_code == 201
        assert db.session.query(models.CollectiveOffer).one().id == response.json["id"]

    def test_create_collective_offer_college_6(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        data = {**base_offer_payload(venue=venue), "students": ["Collège - 6e"]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = db.session.get(models.CollectiveOffer, offer_id)

        assert_offer_values(offer, data, user, offerer)

    @pytest.mark.features(ENABLE_MARSEILLE=True)
    def test_create_collective_offer_primary_level(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "students": ["Écoles Marseille - Maternelle"]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201

        offer = db.session.get(models.CollectiveOffer, response.json["id"])
        assert offer.students == [models.StudentLevels.ECOLES_MARSEILLE_MATERNELLE]

    @pytest.mark.features(ENABLE_MARSEILLE=False)
    def test_create_collective_offer_primary_level_FF_disabled(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "students": ["Écoles Marseille - Maternelle"]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert "students" in response.json

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_CREATE_BOOKABLE_OFFER)
    def test_create_collective_offer_with_allowed_collective_offer_template(self, client, status):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        collective_offer_template = educational_factories.create_collective_offer_template_by_status(
            status, venue=venue
        )

        data = base_offer_payload(venue=venue, template_id=collective_offer_template.id)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201

    def test_location_address_venue(self, client):
        venue = offerers_factories.VenueFactory()
        oa = venue.offererAddress
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": {
                    "banId": oa.address.banId,
                    "isVenueLocation": True,
                    "isManualEdition": False,
                    "inseeCode": oa.address.inseeCode,
                    "city": oa.address.city,
                    "latitude": oa.address.latitude,
                    "longitude": oa.address.longitude,
                    "postalCode": oa.address.postalCode,
                    "street": oa.address.street,
                },
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOffer).filter_by(id=response.json["id"]).one()

        assert offer.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION
        assert offer.offererAddress.addressId == oa.addressId
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_school(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "interventionArea": ["75"],
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOffer).filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId == None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

    def test_location_address(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOffer).filter_by(id=response.json["id"]).one()

        assert offer.offererAddress.label == "My address"
        assert offer.offererAddress.address.city == "Paris"
        assert offer.offererAddress.address.postalCode == "75001"
        assert offer.offererAddress.address.street == "3 Rue de Valois"
        assert offer.offererAddress.address.isManualEdition == False
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_to_be_defined(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOffer).filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId == None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"

    def test_from_template_with_inactive_national_program(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)

        national_program = educational_factories.NationalProgramFactory(isActive=False)
        domain = educational_factories.EducationalDomainFactory()
        data = base_offer_payload(
            venue=venue, national_program_id=national_program.id, domain_ids=[domain.id], template_id=template.id
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert offer.domains == [domain]
        assert offer.nationalProgramId is None

    def test_from_template_with_invalid_national_program(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)

        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory()
        data = base_offer_payload(
            venue=venue,
            national_program_id=national_program.id,
            domain_ids=[domain.id],
            template_id=template.id,
            add_domain_to_program=False,
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = db.session.query(models.CollectiveOffer).filter_by(id=response.json["id"]).one()
        assert offer.domains == [domain]
        assert offer.nationalProgramId is None


class Returns403Test:
    def test_create_collective_offer_random_user(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = base_offer_payload(venue=venue)
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        assert response.status_code == 403
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_cannot_create_educational(self, client):
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = base_offer_payload(venue=venue)
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, side_effect=raise_ac):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 403
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_no_adage_offerer(self, client):
        venue = offerers_factories.VenueFactory(managingOfferer__allowedOnAdage=False)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = base_offer_payload(venue=venue)
        with patch("pcapi.core.educational.adage_backends.get_adage_offerer", return_value=[]):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 403
        assert response.json == {"offerer": "not found in adage"}
        assert db.session.query(models.CollectiveOffer).count() == 0


class Returns400Test:
    def test_create_collective_offer_booking_emails_invalid(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user=user)

        data = base_offer_payload(venue=venue)
        data["bookingEmails"] = ["test@testmail.com", "test@test", "test"]
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {
            "bookingEmails.1": ["Le format d'email est incorrect."],
            "bookingEmails.2": ["Le format d'email est incorrect."],
        }
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_no_booking_email(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "bookingEmails": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"bookingEmails": ["Un email doit etre renseigné."]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_empty_contact_email(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "contactEmail": ""}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"contactEmail": ["Le format d'email est incorrect."]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_invalid_contact_email(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "contactEmail": "test@test."}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"contactEmail": ["Le format d'email est incorrect."]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_no_formats(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "formats": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"formats": ["formats must have at least one value"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_no_domains(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "domains": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_description_invalid(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "description": "too_long" * 200}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_must_receive_location(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["Ce champ ne peut pas être nul"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_with_location_type_school_must_not_receive_location_comment(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": "FORBIDDED COMMENT",
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_with_location_type_address_must_not_receive_location_comment(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": "FORBIDDED COMMENT",
                "location": educational_testing.ADDRESS_DICT,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_with_location_type_school_must_provide_intervention_area(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area is required and must not be empty"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_with_location_type_school_must_provide_correct_intervention_area(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "interventionArea": ["977", "1234"],
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be a valid area"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    def test_create_collective_offer_with_location_type_address_must_provide_address(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is required for the provided locationType"]}
        assert db.session.query(models.CollectiveOffer).count() == 0

    @pytest.mark.parametrize(
        "location_type",
        (
            models.CollectiveLocationType.TO_BE_DEFINED.value,
            models.CollectiveLocationType.SCHOOL.value,
        ),
    )
    def test_create_collective_offer_with_location_type_when_address_must_not_be_provided(self, client, location_type):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": location_type,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is not allowed for the provided locationType"]}
        assert db.session.query(models.CollectiveOffer).count() == 0


class Returns404Test:
    def test_create_collective_offer_with_unknown_domain(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        domain = educational_factories.EducationalDomainFactory()

        # When
        data = base_offer_payload(venue=venue, domain_ids=[0, domain.id], add_domain_to_program=False)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_DOMAIN_NOT_FOUND"}

    def test_create_collective_offer_with_unknown_national_program(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue, national_program_id=-1, add_domain_to_program=False)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}

    def test_create_collective_offer_with_inactive_national_program(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        national_program = educational_factories.NationalProgramFactory(isActive=False)
        data = base_offer_payload(venue=venue, national_program_id=national_program.id)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}

    def test_create_collective_offer_with_invalid_national_program(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory()
        data = base_offer_payload(
            venue=venue, national_program_id=national_program.id, domain_ids=[domain.id], add_domain_to_program=False
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_create_collective_offer_with_no_collective_offer_template(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue, template_id=1234567890)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}

    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_CREATE_BOOKABLE_OFFER)
    def test_create_collective_offer_with_not_allowed_collective_offer_template(self, client, status):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        collective_offer_template = educational_factories.create_collective_offer_template_by_status(
            status, venue=venue
        )

        data = base_offer_payload(venue=venue, template_id=collective_offer_template.id)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 403
        assert response.json == {"code": "COLLECTIVE_OFFER_TEMPLATE_FORBIDDEN_ACTION"}

    def test_create_collective_offer_with_unknown_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = base_offer_payload(venue=venue)
        data["venueId"] = 0

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 404
