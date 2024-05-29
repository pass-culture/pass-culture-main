from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import EducationalDomainFactory
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


PATCH_CAN_CREATE_OFFER_PATH = "pcapi.routes.pro.collective_offers.offerers_api.can_offerer_create_educational_offer"


@dataclass
class OfferContext:
    user_offerer: offerers_models.UserOfferer
    venue: offerers_models.Venue
    offer: educational_models.CollectiveOfferTemplate

    @property
    def user(self):
        return self.user_offerer.user


def build_offer_context(offer=None, offer_kwargs=None):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    if not offer:
        offer = CollectiveOfferTemplateFactory(**({"venue": venue} | (offer_kwargs or {})))

    return OfferContext(user_offerer=user_offerer, venue=venue, offer=offer)


def build_pro_client(client, user):
    return client.with_session_auth(user.email)


@dataclass
class PayloadContext:
    national_program: educational_models.NationalProgram
    template_start: datetime
    template_end: datetime
    domain: educational_models.EducationalDomain
    payload: dict


def build_template_start():
    return datetime.utcnow() + timedelta(days=1)


def build_template_end(template_start=None):
    if not template_start:
        template_start = build_template_start()
    return template_start + timedelta(days=100)


def build_payload_context():
    national_program = educational_factories.NationalProgramFactory()
    template_start = build_template_start()
    template_end = build_template_end(template_start)
    domain = EducationalDomainFactory(name="Danse")
    return PayloadContext(
        national_program=national_program,
        template_start=template_start,
        template_end=template_end,
        domain=domain,
        payload={
            "name": "New name",
            "mentalDisabilityCompliant": True,
            "contactEmail": "toto@example.com",
            "subcategoryId": "CONCERT",
            "priceDetail": "pouet",
            "nationalProgramId": national_program.id,
            "dates": {"start": template_start.isoformat(), "end": template_end.isoformat()},
            "domains": [domain.id],
            "formats": [subcategories.EacFormat.CONCERT.value],
        },
    )


class Returns200Test:
    def test_patch_collective_offer_template(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload_ctx.payload)

        assert response.status_code == 200
        assert response.json["name"] == "New name"
        assert response.json["mentalDisabilityCompliant"]
        assert response.json["contactPhone"] == offer_ctx.offer.contactPhone
        assert response.json["contactEmail"] == "toto@example.com"
        assert response.json["subcategoryId"] == "CONCERT"
        assert response.json["educationalPriceDetail"] == "pouet"
        assert response.json["nationalProgram"] == {
            "id": payload_ctx.national_program.id,
            "name": payload_ctx.national_program.name,
        }

        updated_offer = CollectiveOfferTemplate.query.filter_by(id=offer_id).one()
        assert updated_offer.name == "New name"
        assert updated_offer.mentalDisabilityCompliant
        assert updated_offer.subcategoryId == "CONCERT"
        assert updated_offer.priceDetail == "pouet"
        assert updated_offer.domains == [payload_ctx.domain]
        assert updated_offer.dateRange
        assert updated_offer.start == payload_ctx.template_start
        assert updated_offer.end == payload_ctx.template_end
        assert updated_offer.formats == [subcategories.EacFormat.CONCERT]
        assert updated_offer.contactEmail == "toto@example.com"
        assert updated_offer.contactPhone == offer_ctx.offer.contactPhone
        assert updated_offer.contactForm == educational_models.OfferContactFormEnum.FORM

    def test_with_tz_aware_dates(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "dates": {
                "start": format_into_utc_date(payload_ctx.template_start),
                "end": format_into_utc_date(payload_ctx.template_end),
            },
        }

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200

    def test_without_dates_does_not_update_offer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        assert offer.dateRange.lower
        assert offer.dateRange.upper

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer.id)
            response = pro_client.patch(endpoint, json={})
            assert response.status_code == 200

        updated_offer = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id == offer.id).one()

        assert updated_offer.dateRange.lower
        assert updated_offer.dateRange.upper

    def test_with_empty_dates_updates_offer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        assert offer.dateRange.lower
        assert offer.dateRange.upper

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer.id)
            response = pro_client.patch(endpoint, json={"dates": None})
            assert response.status_code == 200

        updated_offer = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange is None

    def test_with_almost_empty_data_updates_offer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        assert offer.dateRange.lower
        assert offer.dateRange.upper

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer.id)
            response = pro_client.patch(endpoint, json={"contactPhone": None, "dates": None})
            assert response.status_code == 200

        updated_offer = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange is None

    def test_with_null_phone_data(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer_ctx.offer.id)

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(endpoint, json={"contactPhone": None})
            assert response.status_code == 200

    def test_with_email_phone_and_url_contact(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer
        endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer.id)

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(
                endpoint,
                json={
                    "contactEmail": "a@b.com",
                    "contactPhone": "0101",
                    "contactUrl": "http://localhost/",
                    "contactForm": None,
                },
            )
            assert response.status_code == 200

        updated_offer = CollectiveOfferTemplate.query.filter(CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.contactEmail == "a@b.com"
        assert updated_offer.contactPhone == "0101"
        assert updated_offer.contactUrl == "http://localhost/"
        assert updated_offer.contactForm is None

    def test_contact_form_both_null_form_and_url(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        payload = payload_ctx.payload

        payload["contactUrl"] = None
        payload["contactForm"] = None

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        assert response.status_code == 200
        assert response.json["contactForm"] is None
        assert response.json["contactUrl"] is None


class Returns400Test:
    def test_non_approved_offer_fails(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)

        offer = CollectiveOfferTemplateFactory(validation=OfferValidationStatus.PENDING)
        offerers_factories.UserOffererFactory(user=offer_ctx.user, offerer=offer.venue.managingOfferer)

        data = {"visualDisabilityCompliant": True}
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Les offres refusées ou en attente de validation ne sont pas modifiables"]

    def test_empty_name(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"name": " "}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"name": [""]}

    def test_null_name(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"name": None}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"name": [""]}

    def test_non_educational_subcategory(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"subcategoryId": "LIVRE_PAPIER"}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"subcategoryId": "this subcategory is not educational"}

    def test_empty_educational_domains(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"domains": []}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}

    def test_unknown_national_program(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"nationalProgramId": -1}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["National program not found"]}

    def test_contact_form_all_fields_null(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        payload = payload_ctx.payload

        payload["contactEmail"] = None
        payload["contactPhone"] = None
        payload["contactUrl"] = None
        payload["contactForm"] = None

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        assert response.status_code == 400
        assert "contact[all]" in response.json

    def test_contact_form_both_form_and_url_set(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        payload = payload_ctx.payload

        payload["contactUrl"] = "https://example.com/contact"
        payload["contactForm"] = educational_models.OfferContactFormEnum.FORM.value

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        assert response.status_code == 400
        assert response.json == {"__root__": ["error: url and form are both not null"]}


class InvalidDatesTest:
    def test_missing_start(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        end = build_template_end().isoformat()
        response = self.send_request(pro_client, offer_id, {"end": end})

        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_null(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        end = build_template_end().isoformat()

        response = self.send_request(pro_client, offer_id, {"start": None, "end": end})
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_in_the_past(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        one_week_ago = datetime.utcnow() - timedelta(days=7)
        dates = {"start": one_week_ago.isoformat(), "end": build_template_end().isoformat()}

        response = self.send_request(pro_client, offer_id, dates)
        assert response.status_code == 400
        assert "dates.start" in response.json

    def test_start_is_after_end(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        template_end = build_template_end()
        dates = {"start": (template_end + timedelta(days=1)).isoformat(), "end": template_end.isoformat()}

        response = self.send_request(pro_client, offer_id, dates)

        assert response.status_code == 400
        assert "dates.__root__" in response.json

    def test_missing_end(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        start = build_template_start().isoformat()
        response = self.send_request(pro_client, offer_id, {"start": start})

        assert response.status_code == 400
        assert "dates.end" in response.json

    def test_end_is_null(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        start = build_template_start().isoformat()
        response = self.send_request(pro_client, offer_id, {"start": start, "end": None})

        assert response.status_code == 400
        assert "dates.end" in response.json

    def send_request(self, pro_client, offer_id, dates):
        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            endpoint = url_for("Private API.edit_collective_offer_template", offer_id=offer_id)
            return pro_client.patch(endpoint, json={"dates": dates})


class Returns403Test:
    def test_user_is_not_attached_to_offerer(self, client):
        offer = CollectiveOfferTemplateFactory(name="Old name")
        offer_ctx = build_offer_context(offer=offer)

        pro_client = build_pro_client(client, offer_ctx.user)

        data = {"name": "New name"}
        response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
        assert CollectiveOfferTemplate.query.filter_by(id=offer.id).one().name == "Old name"

    def test_replacing_venue_with_different_offerer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        unrelated_venue = offerers_factories.VenueFactory()
        data = {"venueId": unrelated_venue.id}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}

    def test_cultural_partner_not_found(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"name": "Update some random field"}

        with patch(PATCH_CAN_CREATE_OFFER_PATH, return_value=False):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 403
        assert response.json == {"Partner": "User not in Adage can't edit the offer"}


class Returns404Test:
    def test_offer_does_not_exist(self, client):
        user = offerers_factories.UserOffererFactory().user
        pro_client = build_pro_client(client, user)

        response = pro_client.patch("/collective/offers-template/12", json={})
        assert response.status_code == 404

    def test_unknown_educational_domain(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"domains": [0]}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 404
        assert response.json["code"] == "EDUCATIONAL_DOMAIN_NOT_FOUND"

    def test_replacing_by_unknown_venue(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"venueId": 0}

        with patch(PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 404
        assert response.json["venueId"] == "The venue does not exist."
