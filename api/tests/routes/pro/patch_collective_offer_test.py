from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import EducationalDomainFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import StudentLevels
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_booking
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @freeze_time("2019-01-01T12:00:00Z")
    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer(self, client):
        # Given
        offer = CollectiveOfferFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            bookingEmails=["booking@youpi.com", "kingboo@piyou.com"],
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            educational_domains=None,
            students=[StudentLevels.CAP1],
            interventionArea=["01", "07", "08"],
        )
        booking = CollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer, collectiveStock__beginningDatetime=datetime(2020, 1, 1)
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        domain = EducationalDomainFactory(name="Architecture")

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
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

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
                ]
            ),
        )

        adage_request = adage_api_testing.adage_requests[0]
        adage_request["sent_data"].updatedFields = sorted(adage_request["sent_data"].updatedFields)

        assert adage_request["sent_data"] == expected_payload
        assert adage_request["url"] == "https://adage_base_url/v1/prereservation-edit"

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    def test_patch_collective_offer_do_not_notify_educational_redactor_when_no_active_booking(
        self,
        client,
    ):
        # Given
        offer = CollectiveOfferFactory()
        CollectiveBookingFactory(collectiveStock__collectiveOffer=offer, status=CollectiveBookingStatus.CANCELLED)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200
        assert len(adage_api_testing.adage_requests) == 0

    def test_patch_offer_with_empty_intervention_area_in_offerer_venue(self, client):
        # Given
        offer = CollectiveOfferFactory(interventionArea=["01", "02"])
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "interventionArea": [],
            "offerVenue": {
                "addressType": "offererVenue",
                "otherAddress": "",
                "venueId": "",
            },
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200
        assert offer.interventionArea == []

    def test_patch_collective_offer_update_legacy_template(self, client):
        # Given
        template = CollectiveOfferTemplateFactory(domains=[], interventionArea=[])
        offer = CollectiveOfferFactory(templateId=template.id)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        domain = EducationalDomainFactory(name="Architecture")

        # When
        data = {
            "domains": [domain.id],
            "interventionArea": ["01", "2A"],
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 200
        assert template.domains == [domain]
        assert template.interventionArea == ["01", "2A"]


class Returns400Test:
    def test_patch_non_approved_offer_fails(self, app, client):
        offer = CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        data = {
            "visualDisabilityCompliant": True,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_patch_offer_with_empty_name(self, app, client):
        # Given
        offer = CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": " "}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_null_name(self, app, client):
        # Given
        offer = CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"name": None}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_non_educational_subcategory(self, client):
        # Given
        offer = CollectiveOfferFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {"subcategoryId": "LIVRE_PAPIER"}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_empty_educational_domain(self, client):
        # Given
        offer = CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "domains": [],
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_domain(self, app, client):
        # Given
        offer = CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "domains": None,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_empty_intervention_area(self, client):
        # Given
        offer = CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "interventionArea": [],
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_intervention_area(self, client):
        # Given
        offer = CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "interventionArea": None,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_none_description(self, client):
        # Given
        offer = CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "description": None,
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 400


class Returns403Test:
    def when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = CollectiveOfferFactory(name="Old name")
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert CollectiveOffer.query.get(offer.id).name == "Old name"

    def test_cannot_update_offer_with_used_booking(self, client):
        # Given
        offer = CollectiveOfferFactory()
        UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer=offer,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "name": "New name",
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"offer": "the used or refund offer can't be edited."}

    def test_patch_collective_offer_replacing_by_unknown_venue(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )
        offer = CollectiveOfferFactory(venue__managingOfferer=offerer)

        # When
        data = {"venueId": 0}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 404
        assert response.json["venueId"] == "The venue does not exist."

    def test_patch_collective_offer_replacing_venue_with_different_offerer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )
        offer = CollectiveOfferFactory(venue__managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer2)

        # When
        data = {"venueId": venue2.id}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}


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
        offer = CollectiveOfferFactory(
            educational_domains=None,
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )

        # When
        data = {
            "domains": [0],
        }
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 404
        assert response.json["code"] == "EDUCATIONAL_DOMAIN_NOT_FOUND"
