from datetime import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.educational.schemas import EducationalBookingEdition
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.adage.v1.serialization import prebooking


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
            subcategoryId="CINE_PLEIN_AIR",
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
            "subcategoryId": "CONCERT",
            "domains": [domain.id],
            "students": ["Collège - 4e"],
            "interventionArea": ["01", "2A"],
            "nationalProgramId": national_program.id,
            "formats": [subcategories.EacFormat.CONCERT.value],
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
        assert response.json["subcategoryId"] == "CONCERT"
        assert response.json["students"] == ["Collège - 4e"]
        assert response.json["interventionArea"] == ["01", "2A"]
        assert response.json["description"] == "Ma super description"
        assert response.json["nationalProgram"] == {"id": national_program.id, "name": national_program.name}
        assert not response.json["isTemplate"]

        updated_offer = models.CollectiveOffer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.bookingEmails == ["pifpouf@testmail.com", "bimbam@testmail.com"]
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"
        assert updated_offer.students == [models.StudentLevels.COLLEGE4]
        assert updated_offer.domains == [domain]
        assert updated_offer.interventionArea == ["01", "2A"]
        assert updated_offer.description == "Ma super description"
        assert updated_offer.formats == [subcategories.EacFormat.CONCERT]

        expected_payload = EducationalBookingEdition(
            **prebooking.serialize_collective_booking(booking).dict(),
            updatedFields=sorted(
                [
                    "name",
                    "students",
                    "contactEmail",
                    "bookingEmails",
                    "interventionArea",
                    "mentalDisabilityCompliant",
                    "subcategoryId",
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

    def test_patch_offer_with_empty_intervention_area_in_offerer_venue(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(interventionArea=["01", "02"])
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "interventionArea": [],
            "offerVenue": {
                "addressType": "offererVenue",
                "otherAddress": "",
                "venueId": offer.venue.id,
            },
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 200
        assert offer.interventionArea == []

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
            "subcategoryId": "CONCERT",
            "students": ["Collège - 4e"],
            "interventionArea": ["01", "2A"],
            "formats": [subcategories.EacFormat.CONCERT.value],
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
        assert offer.subcategoryId == "CONCERT"
        assert offer.students == [models.StudentLevels.COLLEGE4]
        assert offer.interventionArea == ["01", "2A"]
        assert offer.formats == [subcategories.EacFormat.CONCERT]

    def test_offer_venue_offerer_venue(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        assert len(offer.interventionArea) > 0
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": offer.venue.id}}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.offerVenue == data["offerVenue"]
        assert offer.interventionArea == []

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_school(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        initial_intervention_area = offer.interventionArea
        assert len(initial_intervention_area) > 0

        data = {"offerVenue": {"addressType": "school", "otherAddress": "", "venueId": None}}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.offerVenue == data["offerVenue"]
        assert offer.interventionArea == initial_intervention_area

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_other(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        initial_intervention_area = offer.interventionArea
        assert len(initial_intervention_area) > 0

        data = {"offerVenue": {"addressType": "other", "otherAddress": "In Paris", "venueId": None}}
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.offerVenue == data["offerVenue"]
        assert offer.interventionArea == initial_intervention_area

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_address_venue(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        oa = offer.venue.offererAddress
        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": {
                    "isVenueAddress": True,
                    "isManualEdition": False,
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
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddressId == oa.id
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "offererVenue", "otherAddress": "", "venueId": offer.venue.id}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_school(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "school", "otherAddress": "", "venueId": None}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_address(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddress.label == "My address"
        assert offer.offererAddress.address.city == "Paris"
        assert offer.offererAddress.address.postalCode == "75001"
        assert offer.offererAddress.address.street == "3 Rue de Valois"
        assert offer.offererAddress.address.isManualEdition == False
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

        assert offer.offerVenue == {
            "addressType": "other",
            "otherAddress": "3 Rue de Valois 75001 Paris",
            "venueId": None,
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_to_be_defined(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"

        assert offer.offerVenue == {"addressType": "other", "otherAddress": "Right here", "venueId": None}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_change_venue(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        # offer is located at the address of its venue
        offer.locationType = models.CollectiveLocationType.ADDRESS
        offer.offererAddress = offer.venue.offererAddress
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
                "address": {
                    "isVenueAddress": True,
                    "isManualEdition": False,
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
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()

        assert offer.venueId == other_venue.id
        assert offer.offererAddressId == other_venue.offererAddressId
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "offererVenue", "otherAddress": "", "venueId": other_venue.id}

    def test_national_program_unchanged(self, client):
        program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(nationalProgram=program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"name": "hello"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
        assert offer.nationalProgramId == program.id

    def test_national_program_set_none(self, client):
        program = educational_factories.NationalProgramFactory()
        offer = educational_factories.CollectiveOfferFactory(nationalProgram=program)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"nationalProgramId": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 200
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
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
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
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
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
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
        offer = models.CollectiveOffer.query.filter(models.CollectiveOffer.id == offer.id).one()
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

    def test_patch_offer_with_non_educational_subcategory(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"subcategoryId": "LIVRE_PAPIER"}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_empty_formats(self, client):
        # Given
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

    def test_patch_offer_with_empty_intervention_area(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "interventionArea": [],
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_intervention_area(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "interventionArea": None,
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_description(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "description": None,
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    @time_machine.travel("2019-01-01T12:00:00Z")
    @pytest.mark.settings(ADAGE_API_URL="https://adage_base_url")
    def test_update_collective_offer_with_unknown_national_program(self, client):
        offer = educational_factories.CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            bookingEmails=["booking@youpi.com", "kingboo@piyou.com"],
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
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
            "subcategoryId": "CONCERT",
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
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": other_venue.id})
            assert response.status_code == 400
            assert response.json == {"venueId": ["No venue with a pricing point found for the destination venue."]}

    def test_patch_collective_offer_replacing_by_venue_not_eligible(self, auth_client, venue, other_related_venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"venueId": other_venue.id})
            assert response.status_code == 400
            assert response.json == {"venueId": ["Ce partenaire culturel n'est pas éligible au transfert de l'offre"]}

    def test_patch_collective_offer_description_invalid(self, auth_client, venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json={"description": "too_long" * 200})

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_cannot_receive_offer_venue(self, auth_client, venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "offerVenue": {"addressType": models.OfferAddressType.SCHOOL.value, "venueId": None, "otherAddress": ""},
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"offerVenue": ["Cannot receive offerVenue, use location instead"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=False)
    def test_patch_collective_offer_cannot_receive_location(self, auth_client, venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"location": ["Cannot receive location, use offerVenue instead"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_school_must_not_receive_location_comment(
        self, auth_client, venue
    ):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": "FORBIDDEN COMMENT",
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_address_must_not_receive_location_comment(
        self, auth_client, venue
    ):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": "FORBIDDEN COMMENT",
                "address": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_school_must_provide_intervention_area(self, auth_client, venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area is required and must not be empty"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_address_must_not_provide_intervention_area(
        self, auth_client, venue
    ):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "interventionArea": ["75", "91"],
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be empty"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_school_must_provide_correct_intervention_area(
        self, auth_client, venue
    ):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        payload = {
            "interventionArea": ["75", "1234"],
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be a valid area"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_address_must_provide_address(self, auth_client, venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(venue=venue)

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.address": ["address is required for the provided locationType"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_change_location_type(self, auth_client, venue):
        offer = educational_factories.ActiveCollectiveOfferFactory(
            venue=venue,
        )

        data = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.address": ["address is required for the provided locationType"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
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
        offer = educational_factories.ActiveCollectiveOfferFactory(
            venue=venue,
        )
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            "location": {
                "locationType": location_type,
                "locationComment": None,
                "address": educational_testing.ADDRESS_DICT,
            }
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.address": ["address is not allowed for the provided locationType"]}


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
        assert models.CollectiveOffer.query.get(offer.id).name == "Old name"

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
        offer = educational_factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
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

    def test_offerer_address_venue_not_allowed(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)
        venue = offerers_factories.VenueFactory()
        data = {"offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}}

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }

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

    def test_patch_collective_offer_replacing_by_unknown_venue_in_offer_venue(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer)
        data = {"offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": 0}}

        client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 404
        assert response.json == {"venueId": "The venue does not exist."}
