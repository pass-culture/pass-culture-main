from datetime import datetime
from unittest.mock import patch

from flask import url_for
import pytest
import time_machine

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import StudentLevels
import pcapi.core.educational.testing as educational_testing
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.providers.factories as providers_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking


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
    endpoint = "Private API.edit_collective_offer"

    @time_machine.travel("2019-01-01 12:00:00")
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            bookingEmails=["booking@youpi.com", "kingboo@piyou.com"],
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            educational_domains=None,
            students=[StudentLevels.CAP1],
            interventionArea=["01", "07", "08"],
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer, collectiveStock__beginningDatetime=datetime(2020, 1, 1)
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        domain = educational_factories.EducationalDomainFactory(name="Architecture")
        national_program = educational_factories.NationalProgramFactory()

        # When
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

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
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

        updated_offer = CollectiveOffer.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.bookingEmails == ["pifpouf@testmail.com", "bimbam@testmail.com"]
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"
        assert updated_offer.students == [StudentLevels.COLLEGE4]
        assert updated_offer.domains == [domain]
        assert updated_offer.interventionArea == ["01", "2A"]
        assert updated_offer.description == "Ma super description"
        assert updated_offer.formats == [subcategories.EacFormat.CONCERT]

        expected_payload = EducationalBookingEdition(
            **serialize_collective_booking(booking).dict(),
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

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer_do_not_notify_educational_redactor_when_no_active_booking(
        self,
        client,
    ):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer, status=CollectiveBookingStatus.CANCELLED
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "name": "New name",
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 200
        assert len(offer.students) == 1
        assert offer.students[0].value == "Collège - 6e"

    @pytest.mark.parametrize(
        "factory",
        [
            educational_factories.PendingCollectiveBookingFactory,
            educational_factories.ConfirmedCollectiveBookingFactory,
        ],
    )
    def test_update_venue_both_offer_and_booking(self, auth_client, venue, other_related_venue, factory):

        offer = educational_factories.CollectiveOfferFactory(venue=other_related_venue)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        booking = factory(venue=other_related_venue, collectiveStock=stock)
        cancelled_booking = educational_factories.CancelledCollectiveBookingFactory(
            venue=other_related_venue, collectiveStock=stock
        )

        patch_path = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"
        with patch(patch_path):
            response = auth_client.patch(url_for(self.endpoint, offer_id=offer.id), json={"venueId": venue.id})
            assert response.status_code == 200

        db.session.refresh(offer)
        db.session.refresh(booking)
        db.session.refresh(cancelled_booking)

        assert offer.venueId == venue.id
        assert booking.venueId == venue.id
        assert cancelled_booking.venueId == venue.id

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
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
        patch_path = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"
        auth_client = client.with_session_auth("user@example.com")
        with patch(patch_path):
            response = auth_client.patch(url_for(self.endpoint, offer_id=offer.id), json=data)
            assert response.status_code == 200

        db.session.refresh(offer)
        assert offer.name == "New name"
        assert offer.mentalDisabilityCompliant
        assert offer.description == "Ma super description"
        assert offer.contactEmail == "toto@example.com"
        assert offer.bookingEmails == ["pifpouf@testmail.com", "bimbam@testmail.com"]
        assert offer.subcategoryId == "CONCERT"
        assert offer.students == [StudentLevels.COLLEGE4]
        assert offer.interventionArea == ["01", "2A"]
        assert offer.formats == [subcategories.EacFormat.CONCERT]


class Returns400Test:
    def test_patch_non_approved_offer_fails(self, app, client):
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400

    @time_machine.travel("2019-01-01T12:00:00Z")
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_update_collective_offer_with_unknown_national_program(self, client):
        offer = educational_factories.CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            bookingEmails=["booking@youpi.com", "kingboo@piyou.com"],
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            educational_domains=None,
            students=[StudentLevels.CAP1],
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"global": ["National program not found"]}

    def test_update_collective_offer_booking_emails_invalid(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"bookingEmails": ["test@testmail.com", "test@test", "test"]}
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {
            "bookingEmails.1": ["Le format d'email est incorrect."],
            "bookingEmails.2": ["Le format d'email est incorrect."],
        }


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory(name="Old name")
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        data = {"name": "New name"}
        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
        assert CollectiveOffer.query.get(offer.id).name == "Old name"

    def test_cannot_update_offer_with_used_booking(self, client):
        # Given
        offer = educational_factories.CollectiveOfferFactory()
        educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "name": "New name",
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"offer": "the used or refund offer can't be edited."}

    def test_cannot_update_offer_created_by_public_api(self, client):
        # Given
        provider = providers_factories.ProviderFactory()
        offer = educational_factories.CollectiveOfferFactory(provider=provider)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "name": "New name",
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"global": ["Collective offer created by public API is only editable via API."]}

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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}

    def test_update_collective_offer_venue_of_reimbursed_offer_fails(self, client, other_related_venue):
        offer = educational_factories.ReimbursedCollectiveOfferFactory()
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"venueId": other_related_venue.id}
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json == {"offer": "the used or refund offer can't be edited."}

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

        endpoint = "Private API.edit_collective_offer"
        patch_path = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"
        with patch(patch_path):
            response = auth_client.patch(url_for(endpoint, offer_id=offer.id), json={"venueId": venue.id})
            assert response.status_code == 403

        db.session.refresh(offer)
        db.session.refresh(booking)
        db.session.refresh(finance_event)

        assert offer.venueId == other_related_venue.id
        assert booking.venueId == other_related_venue.id
        assert finance_event.venueId == other_related_venue.id

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS)
    def test_patch_collective_offer_unallowed_action(self, client, status):
        offer = educational_factories.create_collective_offer_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        previous_name = offer.name
        previous_description = offer.description
        data = {"name": "New name", "description": "Ma super description"}
        patch_path = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"
        auth_client = client.with_session_auth("user@example.com")
        with patch(patch_path):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)
            assert response.status_code == 403
            assert response.json == {"offer": "This collective offer status does not allow editing details"}

        db.session.refresh(offer)
        assert offer.name == previous_name
        assert offer.description == previous_description

    @override_features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    def test_patch_collective_offer_ended(self, client):
        offer = educational_factories.EndedCollectiveOfferFactory(booking_is_confirmed=True)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        previous_name = offer.name
        previous_description = offer.description
        data = {"name": "New name", "description": "Ma super description"}
        patch_path = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"
        auth_client = client.with_session_auth("user@example.com")
        with patch(patch_path):
            response = auth_client.patch(f"/collective/offers/{offer.id}", json=data)
            assert response.status_code == 403
            assert response.json == {"offer": "This collective offer status does not allow editing details"}

        db.session.refresh(offer)
        assert offer.name == previous_name
        assert offer.description == previous_description


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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
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
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer", return_value=False
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # THEN
        assert response.status_code == 403
        assert response.json == {"Partner": "User not in Adage can't edit the offer"}

    def test_patch_collective_offer_replacing_by_unknown_venue(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )
        offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer)
        data = {"venueId": 0}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers/{offer.id}", json=data)

        # Then
        assert response.status_code == 404
        assert response.json["venueId"] == "The venue does not exist."
