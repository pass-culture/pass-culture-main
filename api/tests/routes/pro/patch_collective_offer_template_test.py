from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.educational.exceptions import CulturalPartnerNotFoundException
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import EducationalDomainFactory
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @freeze_time("2019-01-01T12:00:00Z")
    def test_patch_collective_offer_template(self, client):
        # Given
        domain = EducationalDomainFactory(name="Danse")
        offer = CollectiveOfferTemplateFactory(
            mentalDisabilityCompliant=False,
            contactEmail="johndoe@yopmail.com",
            contactPhone="0600000000",
            subcategoryId="CINE_PLEIN_AIR",
            priceDetail="price detail",
            domains=[],
        )
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "contactEmail": "toto@example.com",
            "subcategoryId": "CONCERT",
            "priceDetail": "pouet",
            "domains": [domain.id],
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 200
        assert response.json["name"] == "New name"
        assert response.json["mentalDisabilityCompliant"]
        assert response.json["contactPhone"] == "0600000000"
        assert response.json["contactEmail"] == "toto@example.com"
        assert response.json["subcategoryId"] == "CONCERT"
        assert response.json["educationalPriceDetail"] == "pouet"

        updated_offer = CollectiveOfferTemplate.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"
        assert updated_offer.priceDetail == "pouet"
        assert updated_offer.domains == [domain]


class Returns400Test:
    def test_patch_non_approved_offer_fails(self, app, client):
        offer = CollectiveOfferTemplateFactory(validation=OfferValidationStatus.PENDING)
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
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_patch_offer_with_empty_name(self, app, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
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
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_null_name(self, app, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"name": None}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_non_educational_subcategory(self, app, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
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
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400

    def test_patch_offer_with_empty_educational_domains(self, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"domains": []}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 400


class Returns403Test:
    def test_when_user_is_not_attached_to_offerer(self, app, client):
        # Given
        offer = CollectiveOfferTemplateFactory(name="Old name")
        offerers_factories.UserOffererFactory(user__email="user@example.com")

        # When
        data = {"name": "New name"}
        response = client.with_session_auth("user@example.com").patch(
            f"/collective/offers-template/{humanize(offer.id)}", json=data
        )

        # Then
        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert CollectiveOfferTemplate.query.get(offer.id).name == "Old name"


class Returns404Test:
    def test_returns_404_if_offer_does_not_exist(self, app, client):
        # given
        users_factories.UserFactory(email="user@example.com")

        # when
        response = client.with_session_auth("user@example.com").patch("/collective/offers-template/ADFGA", json={})

        # then
        assert response.status_code == 404

    def test_patch_collective_offer_replacing_venue_with_same_offerer(self, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"name": "New name"}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 200
        assert response.json["name"] == "New name"

    def test_patch_offer_with_unknown_educational_domain(self, client):
        # Given
        offer = CollectiveOfferTemplateFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offer.venue.managingOfferer,
        )
        data = {"domains": [0]}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 404
        assert response.json["code"] == "EDUCATIONAL_DOMAIN_NOT_FOUND"

    def test_patch_collective_offer_template_replacing_by_unknown_venue(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )
        offer = CollectiveOfferTemplateFactory(venue__managingOfferer=offerer)
        data = {"venueId": 0}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

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
        offer = CollectiveOfferTemplateFactory(venue__managingOfferer=offerer)
        venue2 = offerers_factories.VenueFactory(managingOfferer=offerer2)
        data = {"venueId": venue2.id}

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # Then
        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}

    def test_edit_collective_offer_template_with_offerer_unregister_in_adage(self, client):
        # GIVEN

        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(
            user__email="user@example.com",
            offerer=offerer,
        )
        offer = CollectiveOfferTemplateFactory(venue__managingOfferer=offerer)

        data = {
            "contactEmail": "toto@example.com",
        }

        # WHEN
        client = client.with_session_auth("user@example.com")
        with patch(
            "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer",
            side_effect=CulturalPartnerNotFoundException,
        ):
            response = client.patch(f"/collective/offers-template/{humanize(offer.id)}", json=data)

        # THEN
        assert response.status_code == 403
        assert response.json == {"Partner": "User not in Adage can't edit the offer"}
