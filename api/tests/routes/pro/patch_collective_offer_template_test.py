from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


@dataclass
class OfferContext:
    user_offerer: offerers_models.UserOfferer
    venue: offerers_models.Venue
    offer: models.CollectiveOfferTemplate

    @property
    def user(self):
        return self.user_offerer.user


def build_offer_context(offer=None, offer_kwargs=None):
    user_offerer = offerers_factories.UserOffererFactory()
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

    if not offer:
        offer = educational_factories.CollectiveOfferTemplateFactory(**({"venue": venue} | (offer_kwargs or {})))

    return OfferContext(user_offerer=user_offerer, venue=venue, offer=offer)


def build_pro_client(client, user):
    return client.with_session_auth(user.email)


@dataclass
class PayloadContext:
    national_program: models.NationalProgram
    template_start: datetime
    template_end: datetime
    domain: models.EducationalDomain
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
    domain = educational_factories.EducationalDomainFactory(name="Danse", nationalPrograms=[national_program])
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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
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

        updated_offer = models.CollectiveOfferTemplate.query.get(offer_id)
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
        assert updated_offer.contactForm == models.OfferContactFormEnum.FORM

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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200

    def test_without_dates_does_not_update_offer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        assert offer.dateRange.lower
        assert offer.dateRange.upper

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json={})
            assert response.status_code == 200

        updated_offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer.id).one()

        assert updated_offer.dateRange.lower
        assert updated_offer.dateRange.upper

    def test_with_empty_dates_updates_offer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        assert offer.dateRange.lower
        assert offer.dateRange.upper

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer.id}", json={"dates": None})
            assert response.status_code == 200

        updated_offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange is None

    def test_with_almost_empty_data_updates_offer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        assert offer.dateRange.lower
        assert offer.dateRange.upper

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(
                f"/collective/offers-template/{offer.id}", json={"contactPhone": None, "dates": None}
            )
            assert response.status_code == 200

        updated_offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange is None

    def test_with_null_phone_data(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(
                f"/collective/offers-template/{offer_ctx.offer.id}", json={"contactPhone": None}
            )
            assert response.status_code == 200

    def test_with_email_phone_and_url_contact(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(
                f"/collective/offers-template/{offer.id}",
                json={
                    "contactEmail": "a@b.com",
                    "contactPhone": "0101",
                    "contactUrl": "http://localhost/",
                    "contactForm": None,
                },
            )
            assert response.status_code == 200

        updated_offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.contactEmail == "a@b.com"
        assert updated_offer.contactPhone == "0101"
        assert updated_offer.contactUrl == "http://localhost/"
        assert updated_offer.contactForm is None

    def test_with_start_and_end_equal(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer = offer_ctx.offer
        now = datetime.utcnow()

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(
                f"/collective/offers-template/{offer.id}",
                json={"dates": {"start": now.isoformat(), "end": now.isoformat()}},
            )
            assert response.status_code == 200

        updated_offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer.id).one()
        assert updated_offer.dateRange.lower == now
        assert updated_offer.dateRange.upper == now + timedelta(seconds=1)

    def test_contact_form_both_null_form_and_url(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        payload = payload_ctx.payload

        payload["contactUrl"] = None
        payload["contactForm"] = None

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        assert response.status_code == 200
        assert response.json["contactForm"] is None
        assert response.json["contactUrl"] is None

    @pytest.mark.parametrize("status", educational_testing.STATUSES_ALLOWING_EDIT_DETAILS_TEMPLATE)
    def test_patch_collective_offer_allowed_action(self, client, status):
        offer = educational_factories.create_collective_offer_template_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        data = {"name": "New name", "description": "Ma super description"}
        auth_client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers-template/{offer.id}", json=data)
            assert response.status_code == 200

            db.session.refresh(offer)
            assert offer.name == "New name"
            assert offer.description == "Ma super description"

    def test_offer_venue_offerer_venue(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        assert len(offer_ctx.offer.interventionArea) > 0

        venue = offerers_factories.VenueFactory(managingOfferer=offer_ctx.venue.managingOfferer)

        payload = {"offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.offerVenue == payload["offerVenue"]
        assert offer.interventionArea == []

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_school(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        initial_intervention_area = offer_ctx.offer.interventionArea
        assert len(initial_intervention_area) > 0

        payload = {"offerVenue": {"addressType": "school", "otherAddress": "", "venueId": None}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.offerVenue == payload["offerVenue"]
        assert offer.interventionArea == initial_intervention_area

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_other(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        initial_intervention_area = offer_ctx.offer.interventionArea
        assert len(initial_intervention_area) > 0

        payload = {"offerVenue": {"addressType": "other", "otherAddress": "In Paris", "venueId": None}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.offerVenue == payload["offerVenue"]
        assert offer.interventionArea == initial_intervention_area

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_address_venue(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        oa = offer_ctx.venue.offererAddress
        payload = {
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
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()

        assert offer.offererAddressId == oa.id
        assert offer.locationType == models.CollectiveLocationType.ADDRESS
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "offererVenue", "otherAddress": "", "venueId": offer_ctx.venue.id}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_school(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "school", "otherAddress": "", "venueId": None}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_address(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()

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
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()

        assert offer.offererAddressId is None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"

        assert offer.offerVenue == {"addressType": "other", "otherAddress": "Right here", "venueId": None}

    def test_national_program_unchanged(self, client):
        program = educational_factories.NationalProgramFactory()
        offer_ctx = build_offer_context(offer_kwargs={"nationalProgram": program})
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {"name": "hello"}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.nationalProgramId == program.id

    def test_national_program_set_none(self, client):
        program = educational_factories.NationalProgramFactory()
        offer_ctx = build_offer_context(offer_kwargs={"nationalProgram": program})
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {"nationalProgramId": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.nationalProgramId is None

    def test_national_program_valid_update_program(self, client):
        new_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[new_program])
        offer_ctx = build_offer_context(offer_kwargs={"educational_domains": [current_domain]})
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {"nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.nationalProgramId == new_program.id
        assert [domain.id for domain in offer.domains] == [current_domain.id]

    def test_national_program_valid_update_domains(self, client):
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        offer_ctx = build_offer_context(
            offer_kwargs={"educational_domains": [current_domain], "nationalProgram": current_program}
        )
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {"domains": [new_domain.id]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.nationalProgramId == current_program.id
        assert [domain.id for domain in offer.domains] == [new_domain.id]

    def test_national_program_valid_update_domains_and_program(self, client):
        current_program = educational_factories.NationalProgramFactory()
        current_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[current_program])
        new_program = educational_factories.NationalProgramFactory()
        new_domain = educational_factories.EducationalDomainFactory(nationalPrograms=[new_program])
        offer_ctx = build_offer_context(
            offer_kwargs={"educational_domains": [current_domain], "nationalProgram": current_program}
        )
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {"domains": [new_domain.id], "nationalProgramId": new_program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 200
        offer = models.CollectiveOfferTemplate.query.filter(models.CollectiveOfferTemplate.id == offer_id).one()
        assert offer.nationalProgramId == new_program.id
        assert [domain.id for domain in offer.domains] == [new_domain.id]


class Returns400Test:
    def test_empty_name(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"name": " "}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"name": [""]}

    def test_null_name(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"name": None}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"name": [""]}

    def test_non_educational_subcategory(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"subcategoryId": "LIVRE_PAPIER"}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"subcategoryId": "this subcategory is not educational"}

    def test_empty_educational_domains(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"domains": []}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}

    def test_unknown_national_program(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"nationalProgramId": -1}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["National program not found"]}

    def test_inactive_national_program(self, client):
        program = educational_factories.NationalProgramFactory(isActive=False)
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[program])
        offer_ctx = build_offer_context(offer_kwargs={"domains": [domain]})

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        data = {"nationalProgramId": program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INACTIVE"}

    def test_invalid_national_program_update_program(self, client):
        program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory()
        offer_ctx = build_offer_context(offer_kwargs={"domains": [domain]})

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        data = {"nationalProgramId": program.id}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_invalid_national_program_update_domains(self, client):
        program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[program])
        offer_ctx = build_offer_context(offer_kwargs={"domains": [domain], "nationalProgram": program})

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        data = {"domains": [educational_factories.EducationalDomainFactory().id]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

    def test_invalid_national_program_update_domains_and_program(self, client):
        program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory(nationalPrograms=[program])
        offer_ctx = build_offer_context(offer_kwargs={"domains": [domain], "nationalProgram": program})

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        data = {
            "domains": [educational_factories.EducationalDomainFactory().id],
            "nationalProgramId": educational_factories.NationalProgramFactory().id,
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_INVALID"}

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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
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
        payload["contactForm"] = models.OfferContactFormEnum.FORM.value

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        db.session.flush()  # otherwise "Failed to add object to the flush context!" in teardown

        assert response.status_code == 400
        assert response.json == {"__root__": ["error: url and form are both not null"]}

    def test_booking_emails_invalid(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        payload = payload_ctx.payload

        payload["bookingEmails"] = ["test@testmail.com", "test@test", "test"]
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "bookingEmails.1": ["Le format d'email est incorrect."],
            "bookingEmails.2": ["Le format d'email est incorrect."],
        }

    def test_description_invalid(self, client):
        offer_ctx = build_offer_context()
        payload_ctx = build_payload_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id
        payload = payload_ctx.payload

        payload["description"] = "too_long" * 200
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_cannot_receive_offer_venue(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "offerVenue": {
                "addressType": models.OfferAddressType.SCHOOL.value,
                "venueId": None,
                "otherAddress": "",
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"offerVenue": ["Cannot receive offerVenue, use location instead"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=False)
    def test_cannot_receive_location(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"location": ["Cannot receive location, use offerVenue instead"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_template_with_location_type_school_must_not_receive_location_comment(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": "FORBIDDEN COMMENT",
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_template_with_location_type_address_must_not_receive_location_comment(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": "FORBIDDEN COMMENT",
                "address": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {
            "location.locationComment": ["locationComment is not allowed for the provided locationType"]
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_template_with_location_type_address_must_provide_address(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"location.address": ["address is required for the provided locationType"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_template_with_location_type_school_must_provide_intervention_area(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "interventionArea": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area is required and must not be empty"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_template_with_location_type_school_must_provide_correct_intervention_area(
        self, client
    ):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "interventionArea": ["75", "1234"],
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be a valid area"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_patch_collective_offer_with_location_type_address_must_not_provide_intervention_area(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        payload = {
            "interventionArea": ["75", "91"],
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": educational_testing.ADDRESS_DICT,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must be empty"]}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    @pytest.mark.parametrize(
        "location_type",
        (
            models.CollectiveLocationType.TO_BE_DEFINED.value,
            models.CollectiveLocationType.SCHOOL.value,
        ),
    )
    def test_update_collective_offer_template_with_location_type_when_address_must_not_be_provided(
        self, client, location_type
    ):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {
            "location": {
                "locationType": location_type,
                "locationComment": None,
                "address": educational_testing.ADDRESS_DICT,
            }
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 400
        assert response.json == {"location.address": ["address is not allowed for the provided locationType"]}


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
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            return pro_client.patch(f"/collective/offers-template/{offer_id}", json={"dates": dates})


class Returns403Test:
    @pytest.mark.features(ENABLE_COLLECTIVE_NEW_STATUSES=True)
    @pytest.mark.parametrize("status", educational_testing.STATUSES_NOT_ALLOWING_EDIT_DETAILS_TEMPLATE)
    def test_patch_collective_offer_unallowed_action(self, client, status):
        offer = educational_factories.create_collective_offer_template_by_status(status)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        previous_name = offer.name
        previous_description = offer.description
        data = {"name": "New name", "description": "Ma super description"}
        auth_client = client.with_session_auth("user@example.com")
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = auth_client.patch(f"/collective/offers-template/{offer.id}", json=data)
            assert response.status_code == 403
            assert response.json == {"global": ["Cette action n'est pas autorisée sur cette offre"]}

        db.session.refresh(offer)
        assert offer.name == previous_name
        assert offer.description == previous_description

    def test_user_is_not_attached_to_offerer(self, client):
        offer = educational_factories.CollectiveOfferTemplateFactory(name="Old name")
        offer_ctx = build_offer_context(offer=offer)

        pro_client = build_pro_client(client, offer_ctx.user)

        data = {"name": "New name"}
        response = pro_client.patch(f"/collective/offers-template/{offer.id}", json=data)

        assert response.status_code == 403
        assert response.json["global"] == [
            "Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."
        ]
        assert models.CollectiveOfferTemplate.query.get(offer.id).name == "Old name"

    def test_replacing_venue_with_different_offerer(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        unrelated_venue = offerers_factories.VenueFactory()
        data = {"venueId": unrelated_venue.id}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 403
        assert response.json == {"venueId": "New venue needs to have the same offerer"}

    def test_cultural_partner_not_found(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"name": "Update some random field"}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, return_value=False):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 403
        assert response.json == {"Partner": "User not in Adage can't edit the offer"}

    def test_offerer_address_venue_not_allowed(self, client):
        offer_ctx = build_offer_context()
        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        venue = offerers_factories.VenueFactory()

        payload = {"offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=payload)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }


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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 404
        assert response.json["code"] == "EDUCATIONAL_DOMAIN_NOT_FOUND"

    def test_replacing_by_unknown_venue(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"venueId": 0}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 404
        assert response.json == {"venueId": "The venue does not exist."}

    def test_replacing_by_unknown_venue_in_offer_venue(self, client):
        offer_ctx = build_offer_context()

        pro_client = build_pro_client(client, offer_ctx.user)
        offer_id = offer_ctx.offer.id

        data = {"offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": 0}}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = pro_client.patch(f"/collective/offers-template/{offer_id}", json=data)

        assert response.status_code == 404
        assert response.json == {"venueId": "The venue does not exist."}
