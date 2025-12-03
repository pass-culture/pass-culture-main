from datetime import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.categories.models import EacFormat
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.schemas import EducationalBookingEdition
from pcapi.core.educational.serialization.collective_booking import serialize_collective_booking
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venue")
def venue_fixture():
    return offerers_factories.CollectiveVenueFactory(pricing_point="self")


@pytest.fixture(name="other_related_venue")
def other_related_venue_fixture(venue):
    return offerers_factories.CollectiveVenueFactory(managingOfferer=venue.managingOfferer, pricing_point=venue)


@pytest.fixture(name="user_offerer")
def user_offerer_fixture(venue):
    return offerers_factories.UserOffererFactory(
        user__email="user@example.com",
        offerer=venue.managingOfferer,
    )


@pytest.fixture(name="auth_client")
def auth_client_fixture(client, user_offerer):
    return client.with_session_auth(user_offerer.user.email)


class Returns200Test:
    @time_machine.travel("2019-01-01 12:00:00")
    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer(self, client):
        offer = educational_factories.CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            bookingEmails=["booking@youpi.com", "kingboo@piyou.com"],
            contactPhone="0600000000",
            educational_domains=[educational_factories.EducationalDomainFactory()],
            students=[models.StudentLevels.CAP1],
            interventionArea=["01", "07", "08"],
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer,
            collectiveStock__startDatetime=datetime(2020, 1, 1),
            status=models.CollectiveBookingStatus.PENDING,
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(
            name="Architecture", nationalPrograms=[national_program]
        )

        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "description": "Ma super description",
            "contactEmail": "toto@example.com",
            "bookingEmails": ["pifpouf@testmail.com", "bimbam@testmail.com"],
            "domains": [domain.id],
            "students": ["Collège - 4e"],
            "interventionArea": ["01", "2A"],
            "nationalProgramId": national_program.id,
            "formats": [EacFormat.CONCERT.value],
        }

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        assert response.json["name"] == "New name"
        assert response.json["mentalDisabilityCompliant"]
        assert response.json["contactPhone"] == "0600000000"
        assert response.json["contactEmail"] == "toto@example.com"
        assert response.json["bookingEmails"] == ["pifpouf@testmail.com", "bimbam@testmail.com"]
        assert response.json["formats"] == ["Concert"]
        assert response.json["students"] == ["Collège - 4e"]
        assert response.json["interventionArea"] == ["01", "2A"]
        assert response.json["description"] == "Ma super description"
        assert response.json["nationalProgram"] == {"id": national_program.id, "name": national_program.name}
        assert not response.json["isTemplate"]

        updated_offer = db.session.get(models.CollectiveOffer, offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.bookingEmails == ["pifpouf@testmail.com", "bimbam@testmail.com"]
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.students == [models.StudentLevels.COLLEGE4]
        assert updated_offer.domains == [domain]
        assert updated_offer.interventionArea == ["01", "2A"]
        assert updated_offer.description == "Ma super description"
        assert updated_offer.formats == [EacFormat.CONCERT]

        expected_payload = EducationalBookingEdition(
            **serialize_collective_booking(booking).dict(),
            updatedFields=sorted(
                [
                    "name",
                    "nationalProgramId",
                    "students",
                    "contactEmail",
                    "bookingEmails",
                    "interventionArea",
                    "mentalDisabilityCompliant",
                    "domains",
                    "description",
                    "formats",
                ]
            ),
        )

        adage_request = educational_testing.adage_requests[0]
        adage_request["sent_data"].updatedFields = sorted(adage_request["sent_data"].updatedFields)

        assert adage_request["sent_data"] == expected_payload
        assert adage_request["url"] == "https://adage_base_url/v1/prereservation-edit"

    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer_do_not_notify_educational_redactor_when_no_booking(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        data = {"name": "New name"}

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        assert len(educational_testing.adage_requests) == 0

    def test_patch_collective_offer_update_student_level_college_6(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"students": ["Collège - 6e"]}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 200
        assert len(offer.students) == 1
        assert offer.students[0].value == "Collège - 6e"

    def test_update_venue_both_offer_and_booking(self, auth_client, venue, other_related_venue):
        offer = educational_factories.CollectiveOfferFactory(venue=other_related_venue)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        booking = educational_factories.PendingCollectiveBookingFactory(
            venue=other_related_venue, collectiveStock=stock
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": venue.id})
            assert response.status_code == 200

        db.session.refresh(offer)
        db.session.refresh(booking)

        assert offer.venueId == venue.id
        assert booking.venueId == venue.id

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_EDIT_DETAILS)
    def test_patch_collective_offer_allowed_action(self, client, status):
        offer = educational_factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "description": "Ma super description",
            "contactEmail": "toto@example.com",
            "bookingEmails": ["pifpouf@testmail.com", "bimbam@testmail.com"],
            "students": ["Collège - 4e"],
            "interventionArea": ["01", "2A"],
            "formats": [EacFormat.CONCERT.value],
        }

        auth_client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)
            assert response.status_code == 200

        db.session.refresh(offer)
        assert offer.name == "New name"
        assert offer.mentalDisabilityCompliant
        assert offer.description == "Ma super description"
        assert offer.contactEmail == "toto@example.com"
        assert offer.bookingEmails == ["pifpouf@testmail.com", "bimbam@testmail.com"]
        assert offer.students == [models.StudentLevels.COLLEGE4]
        assert offer.interventionArea == ["01", "2A"]
        assert offer.formats == [EacFormat.CONCERT]

    def test_location_address_venue(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        oa = offer.venue.offererAddress
        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": {
                    "banId": oa.address.banId,
                    "isVenueAddress": True,
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
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION
        assert offer.offererAddress.addressId == oa.addressId
        assert offer.offererAddress.label == oa.label
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_school(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

    def test_location_address(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddress.label == "My address"
        assert offer.offererAddress.address.city == "Paris"
        assert offer.offererAddress.address.postalCode == "75001"
        assert offer.offererAddress.address.street == "3 Rue de Valois"
        assert offer.offererAddress.address.isManualEdition == False
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_location_to_be_defined(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "location": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"

    def test_location_change_venue(self, client):
        # offer is located at the address of its venue
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue, locationType=models.CollectiveLocationType.ADDRESS, offererAddress=venue.offererAddress
        )
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        # we change offer.venue and set the location to the new venue address
        other_venue = offerers_factories.VenueFactory(
            managingOfferer=offer.venue.managingOfferer, pricing_point=offer.venue
        )
        new_address = other_venue.offererAddress.address
        data = {
            "venueId": other_venue.id,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": {
                    "banId": new_address.banId,
                    "isVenueAddress": True,
                    "isManualEdition": False,
                    "inseeCode": new_address.inseeCode,
                    "city": new_address.city,
                    "latitude": new_address.latitude,
                    "longitude": new_address.longitude,
                    "postalCode": new_address.postalCode,
                    "street": new_address.street,
                },
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.venueId == other_venue.id
        assert offer.offererAddress.type != offerers_models.LocationType.VENUE_LOCATION
        assert offer.offererAddress.addressId == other_venue.offererAddress.addressId
        assert offer.offererAddress.label == other_venue.offererAddress.label
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

    def test_national_program_unchanged(self, client):
        program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(nationalProgram=program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"name": "hello"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.nationalProgramId == program.id

    def test_national_program_set_none(self, client):
        program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(nationalProgram=program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"nationalProgramId": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.nationalProgramId is None

    def test_national_program_valid_update_program(self, client):
        new_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[new_program])
        offer = educational_factories.CollectiveOfferFactory(domains=[current_domain])
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.nationalProgramId == new_program.id
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_national_program_valid_update_domains(self, client):
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        offer = educational_factories.CollectiveOfferFactory(domains=[current_domain], nationalProgram=current_program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"domains": [new_domain.id]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.nationalProgramId == current_program.id
        assert [domain.id for domain in offer.domains] == [new_domain.id]

    def test_national_program_valid_update_domains_and_program(self, client):
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_program = educational_factories.NationalProgramFactory()
        new_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[new_program])
        offer = educational_factories.CollectiveOfferFactory(domains=[current_domain], nationalProgram=current_program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"domains": [new_domain.id], "nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = db.session.query(models.CollectiveOffer).filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.nationalProgramId == new_program.id
        assert [domain.id for domain in offer.domains] == [new_domain.id]


class Returns400Test:
    def test_patch_offer_with_empty_name(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"name": " "}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_null_name(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": None}
        response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_empty_formats(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com")
        data = {"formats": []}

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"formats": ["formats must have at least one value"]}

    def test_patch_offer_with_empty_educational_domain(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "domains": [],
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)
        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_domain(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "domains": None,
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_description(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        data = {"description": None}

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400

    @time_machine.travel("2019-01-01T12:00:00Z")
    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_update_collective_offer_with_unknown_national_program(self, client):
        offer = educational_factories.CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            bookingEmails=["booking@youpi.com", "kingboo@piyou.com"],
            contactPhone="0600000000",
            educational_domains=None,
            students=[models.StudentLevels.CAP1],
            interventionArea=["01", "07", "08"],
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        domain = educational_factories.EducationalDomainFactory(name="Architecture")

        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "description": "Ma super description",
            "contactEmail": "toto@example.com",
            "bookingEmails": ["pifpouf@testmail.com", "bimbam@testmail.com"],
            "formats": ["Concert"],
            "domains": [domain.id],
            "students": ["Collège - 4e"],
            "interventionArea": ["01", "2A"],
            "nationalProgramId": -1,
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"global": ["National program not found"]}

    def test_update_collective_offer_with_inactive_national_program(self, client):
        program = educational_factories.NationalProgramFactory(isActive=False)
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[program])
        offer = educational_factories.CollectiveOfferFactory(domains=[domain])
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"nationalProgramId": program.id}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}

    def test_update_collective_offer_with_invalid_national_program_update_program(self, client):
        program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory()
        offer = educational_factories.CollectiveOfferFactory(domains=[domain])
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"nationalProgramId": program.id}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_update_collective_offer_with_invalid_national_program_update_domains(self, client):
        program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[program])
        offer = educational_factories.CollectiveOfferFactory(domains=[domain], nationalProgram=program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"domains": [educational_factories.EducationalDomainFactory().id]}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_update_collective_offer_with_invalid_national_program_update_domains_and_program(self, client):
        program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[program])
        offer = educational_factories.CollectiveOfferFactory(domains=[domain], nationalProgram=program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "domains": [educational_factories.EducationalDomainFactory().id],
            "nationalProgramId": educational_factories.NationalProgramFactory().id,
        }
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_update_collective_offer_booking_emails_invalid(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"bookingEmails": ["test@testmail.com", "test@test", "test"]}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {
            "bookingEmails.1": ["Le format d'email est incorrect."],
            "bookingEmails.2": ["Le format d'email est incorrect."],
        }

    def test_patch_collective_offer_replacing_by_venue_with_no_pricing_point(self, auth_client, venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": other_venue.id})
            assert response.status_code == 400
            assert response.json == {"venueId": ["No venue with a pricing point found for the destination venue."]}

    def test_patch_collective_offer_replacing_by_venue_not_eligible(self, auth_client, venue, other_related_venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": other_venue.id})
            assert response.status_code == 400
            assert response.json == {"venueId": ["Ce partenaire culturel n'est pas éligible au transfert de l'offre"]}

    def test_patch_collective_offer_description_invalid(self, auth_client, venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"description": "too_long" * 200})

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    def test_patch_collective_offer_with_location_type_school_must_not_receive_location_comment(
        self, auth_client, venue
    ):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": "FORBIDDEN COMMENT",
                "location": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }

    def test_patch_collective_offer_with_location_type_address_must_not_receive_location_comment(
        self, auth_client, venue
    ):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": "FORBIDDEN COMMENT",
                "location": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }

    def test_patch_collective_offer_with_location_type_school_must_provide_intervention_area(self, auth_client, venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        payload = {
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area is required and must not be empty"]}

    def test_patch_collective_offer_with_location_type_address_must_not_provide_intervention_area(
        self, auth_client, venue
    ):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        payload = {
            "interventionArea": ["75", "91"],
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be empty"]}

    def test_patch_collective_offer_with_location_type_school_must_provide_correct_intervention_area(
        self, auth_client, venue
    ):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        payload = {
            "interventionArea": ["75", "1234"],
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "location": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be a valid area"]}

    def test_patch_collective_offer_with_location_type_address_must_provide_address(self, auth_client, venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is required for the provided locationType"]}

    def test_patch_collective_offer_with_change_location_type(self, auth_client, venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue,
        )

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "location": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is required for the provided locationType"]}

    @pytest.mark.parametrize(
        "location_type",
        (
            models.CollectiveLocationType.TO_BE_DEFINED.value,
            models.CollectiveLocationType.SCHOOL.value,
        ),
    )
    def test_update_collective_offer_template_with_location_type_when_address_must_not_be_provided(
        self, auth_client, venue, location_type
    ):
        offer = educational_factories.PublishedCollectiveOfferFactory(
            venue=venue,
        )
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            "location": {
                "locationType": location_type,
                "locationComment": None,
                "location": educational_testing.ADDRESS_DICT,
            }
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.location": ["address is not allowed for the provided locationType"]}

    def test_location_none(self, auth_client, venue):
        offer = educational_factories.PublishedCollectiveOfferFactory(venue=venue)

        data = {"location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["location cannot be NULL."]}


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(name="Old name")
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        data = {"name": "New name"}
        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
        assert db.session.get(models.CollectiveOffer, offer.id).name == "Old name"

    def test_patch_collective_offer_replacing_venue_with_different_offerer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )
        offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer2)
        data = {"venueId": venue2.id}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}

    @pytest.mark.parametrize(
        "factory",
        [
            educational_factories.UsedCollectiveBookingFactory,
            educational_factories.ReimbursedCollectiveBookingFactory,
        ],
    )
    def test_update_venue_updates_finance_events(self, auth_client, factory, venue, other_related_venue):
        offer = educational_factories.CollectiveOfferFactory(venue=other_related_venue)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        booking = factory(
            # we need to set dateUsed to avoid errors when moving the finance event
            venue=other_related_venue,
            collectiveStock=stock,
            dateUsed=datetime(2024, 1, 1),
        )

        finance_event = finance_factories.FinanceEventFactory(
            status=finance_models.FinanceEventStatus.READY,
            collectiveBooking=booking,
            booking=None,
            venue=other_related_venue,
            valueDate=datetime(2024, 1, 1),
        )

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": venue.id})
            assert response.status_code == 403

        db.session.refresh(offer)
        db.session.refresh(booking)
        db.session.refresh(finance_event)

        assert offer.venueId == other_related_venue.id
        assert booking.venueId == other_related_venue.id
        assert finance_event.venueId == other_related_venue.id

    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS)
    def test_patch_collective_offer_unallowed_action(self, client, status):
        offer = educational_factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        previous_name = offer.name
        previous_description = offer.description
        data = {"name": "New name", "description": "Ma super description"}

        auth_client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)
            assert response.status_code == 403
            assert response.json == {"offer": "This collective offer status does not allow editing details"}

        db.session.refresh(offer)
        assert offer.name == previous_name
        assert offer.description == previous_description

    def test_patch_collective_offer_ended(self, client):
        offer = educational_factories.EndedCollectiveOfferConfirmedBookingFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        previous_name = offer.name
        previous_description = offer.description
        data = {"name": "New name", "description": "Ma super description"}

        auth_client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)
            assert response.status_code == 403
            assert response.json == {"offer": "This collective offer status does not allow editing details"}

        db.session.refresh(offer)
        assert offer.name == previous_name
        assert offer.description == previous_description

    def test_update_venue_from_past_stock(self, auth_client, venue, other_related_venue):
        offer = educational_factories.CollectiveOfferFactory(venue=other_related_venue)
        educational_factories.CollectiveStockFactory(collectiveOffer=offer, startDatetime=datetime(2024, 1, 1))

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": venue.id})
            assert response.status_code == 403
            assert response.json == {"offer": "This collective offer status does not allow editing details"}


class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, app, client):
        # given
        users_factories.UserFactory(email="user@example.com")

        # when
        response = client.with_session_auth("user@example.com").patch("/collective/offers/ADFGA", json={})

        # then
        assert response.status_code == 404

    def test_patch_offer_with_unknown_educational_domain(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "domains": [0],
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 404
        assert response.json["code"] == "EDUCATIONAL_DOMAIN_NOT_FOUND"

    def test_edit_collective_offer_with_offerer_unregister_in_adage(self, client):
        # GIVEN

        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "contactEmail": "toto@example.com",
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, return_value=False):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # THEN
        assert response.status_code == 403
        assert response.json == {"Partner": "User not in Adage can't edit the offer"}

    def test_patch_collective_offer_replacing_by_unknown_venue(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer)
        data = {"venueId": 0}

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 404
        assert response.json == {"venueId": "The venue does not exist."}
