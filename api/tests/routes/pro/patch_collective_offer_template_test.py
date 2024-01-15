from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational.exceptions import CulturalPartnerNotFoundException
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import EducationalDomainFactory
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


PATCH_CAN_CREATE_OFFER_PATH = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"


@pytest.fixture(name="user_offerer")
def user_offerer_fixture():
    return offerers_factories.UserOffererFactory()


@pytest.fixture(name="venue")
def venue_fixture(offerer):
    return offerers_factories.VenueFactory(managingOfferer=offerer)


@pytest.fixture(name="user")
def user_fixture(user_offerer):
    return user_offerer.user


@pytest.fixture(name="offerer")
def offerer_fixture(user_offerer):
    return user_offerer.offerer


@pytest.fixture(name="pro_client")
def pro_client_fixture(client, user):
    return client.with_session_auth(user.email)


@pytest.fixture(name="offer")
def offer_fixture(venue):
    return CollectiveOfferTemplateFactory(
        mentalDisabilityCompliant=False,
        contactPhone="0600000000",
        venue=venue,
        domains=[],
    )


@pytest.fixture(name="template_start")
def template_start_fixture():
    return datetime.utcnow() + timedelta(days=1)


@pytest.fixture(name="template_end")
def template_end_fixture(template_start):
    return template_start + timedelta(days=100)


class Returns200Test:
    def test_patch_collective_offer_template(self, pro_client, offer, template_start, template_end):
        domain = EducationalDomainFactory(name="Danse")
        national_program = educational_factories.NationalProgramFactory()

        payload = {
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "contactEmail": "toto@example.com",
            "subcategoryId": "CONCERT",
            "priceDetail": "pouet",
            "nationalProgramId": national_program.id,
            "dates": {"start": template_start.isoformat(), "end": template_end.isoformat()},
            "domains": [domain.id],
            "formats": [subcategories.EacFormat.CONCERT.value],
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=payload)

        assert response.status_code == 200
        assert response.json["name"] == "New name"
        assert response.json["mentalDisabilityCompliant"]
        assert response.json["contactPhone"] == "0600000000"
        assert response.json["contactEmail"] == "toto@example.com"
        assert response.json["subcategoryId"] == "CONCERT"
        assert response.json["educationalPriceDetail"] == "pouet"
        assert response.json["nationalProgram"] == {"id": national_program.id, "name": national_program.name}

        updated_offer = CollectiveOfferTemplate.query.get(offer.id)
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.contactPhone == "0600000000"
        assert updated_offer.subcategoryId == "CONCERT"
        assert updated_offer.priceDetail == "pouet"
        assert updated_offer.domains == [domain]
        assert updated_offer.dateRange
        assert updated_offer.start == template_start
        assert updated_offer.end == template_end
        assert updated_offer.formats == [subcategories.EacFormat.CONCERT]

    def test_with_tz_aware_dates(self, pro_client, offer, template_start, template_end):
        payload = {
            "dates": {
                "start": format_into_utc_date(template_start),
                "end": format_into_utc_date(template_end),
            },
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=payload)

        assert response.status_code == 200

    def test_without_dates_does_not_update_offer(self, pro_client, offer, template_end):
        assert offer.dateRange.lower
        assert offer.dateRange.upper
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer.id)
            response = pro_client.patch(endpoint, json={})
        assert response.status_code == 200
        updated_offer = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange.lower
        assert updated_offer.dateRange.upper

    def test_with_empty_dates_updates_offer(self, pro_client, offer, template_end):
        assert offer.dateRange.lower
        assert offer.dateRange.upper
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer.id)
            response = pro_client.patch(endpoint, json={"dates": None})
        assert response.status_code == 200
        updated_offer = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange is None


class Returns400Test:
    def test_non_approved_offer_fails(self, pro_client, user):
        offer = CollectiveOfferTemplateFactory(validation=OfferValidationStatus.PENDING)
        offerers_factories.UserOffererFactory(user=user, offerer=offer.venue.managingOfferer)

        data = {"visualDisabilityCompliant": True}
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_empty_name(self, pro_client, offer):
        data = {"name": " "}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"name": [""]}

    def test_null_name(self, pro_client, offer):
        data = {"name": None}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"name": [""]}

    def test_non_educational_subcategory(self, pro_client, offer):
        data = {"subcategoryId": "LIVRE_PAPIER"}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"subcategoryId": "this subcategory is not educational"}

    def test_empty_educational_domains(self, pro_client, offer):
        data = {"domains": []}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}

    def test_unknown_national_program(self, pro_client, offer):
        data = {"nationalProgramId": -1}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["National program not found"]}


class InvalidDatesTest:
    def test_missing_start(self, pro_client, offer, template_end):
        response = self.send_request(pro_client, offer.id, {"end": template_end.isoformat()})
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_null(self, pro_client, offer, template_end):
        response = self.send_request(pro_client, offer.id, {"start": None, "end": template_end.isoformat()})
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_in_the_past(self, pro_client, offer, template_end):
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        dates = {"start": one_week_ago.isoformat(), "end": template_end.isoformat()}

        response = self.send_request(pro_client, offer.id, dates)
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_after_end(self, pro_client, offer, template_end):
        dates = {"start": (template_end + timedelta(days=1)).isoformat(), "end": template_end.isoformat()}
        response = self.send_request(pro_client, offer.id, dates)
        assert response.status_code == 400
        assert "dates.__root__" in response.json

    def test_missing_end(self, pro_client, offer, template_start):
        response = self.send_request(pro_client, offer.id, {"start": template_start.isoformat()})
        assert response.status_code == 400
        assert "dates.end" in response.json

    def test_end_is_null(self, pro_client, offer, template_start):
        response = self.send_request(pro_client, offer.id, {"start": template_start.isoformat(), "end": None})
        assert response.status_code == 400
        assert "dates.end" in response.json

    def send_request(self, pro_client, offer_id, dates):
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer_id)
            return pro_client.patch(endpoint, json={"dates": dates})


class Returns403Test:
    def test_user_is_not_attached_to_offerer(self, pro_client):
        offer = CollectiveOfferTemplateFactory(name="Old name")

        data = {"name": "New name"}
        response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."
        ]
        assert CollectiveOfferTemplate.query.get(offer.id).name == "Old name"

    def test_replacing_venue_with_different_offerer(self, pro_client, offer):
        unrelated_venue = offerers_factories.VenueFactory()
        data = {"venueId": unrelated_venue.id}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}

    def test_cultural_partner_not_found(self, pro_client, offer):
        data = {"name": "Update some random field"}

        with patch(PATCH_CAN_CREATE_OFFER_PATH, side_effect=CulturalPartnerNotFoundException):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json == {"Partner": "User not in Adage can't edit the offer"}


class Returns404Test:
    def test_offer_does_not_exist(self, pro_client):
        response = pro_client.patch("/collective/offers-template/12", json={})
        assert response.status_code == 404

    def test_unknown_educational_domain(self, pro_client, offer):
        data = {"domains": [0]}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 404
        assert response.json["code"] == "EDUCATIONAL_DOMAIN_NOT_FOUND"

    def test_replacing_by_unknown_venue(self, pro_client, offer):
        data = {"venueId": 0}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 404
        assert response.json["venueId"] == "The venue does not exist."
