from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import models
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.models import CollectiveOffer
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories


def base_offer_payload(
    venue, domains=None, subcategory_id=None, template_id=None, national_program_id=None, formats=None
) -> dict:
    if domains is None:
        domains = [educational_factories.EducationalDomainFactory().id]

    if not subcategory_id:
        subcategory_id = subcategories.SPECTACLE_REPRESENTATION.id

    if not national_program_id:
        national_program_id = educational_factories.NationalProgramFactory().id

    if formats is None:
        formats = [subcategories.EacFormat.CONCERT.value]

    return {
        "venueId": venue.id,
        "description": "Ma super description",
        "bookingEmails": ["offer1@example.com", "offer2@example.com"],
        "domains": domains,
        "durationMinutes": 60,
        "name": "La pièce de théâtre",
        "subcategoryId": subcategory_id,
        "contactEmail": "pouet@example.com",
        "contactPhone": "01 99 00 25 68",
        "offerVenue": {
            "addressType": "school",
            "venueId": venue.id,
            "otherAddress": "17 rue aléatoire",
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


def assert_offer_values(offer, data, user, offerer):
    # if there is no booking emails and the offer is build from a
    # template, the booking emails are set using the contact email
    if not data["bookingEmails"] and data["templateId"]:
        if data["contactEmail"]:
            assert offer.bookingEmails == [data["contactEmail"]]
        else:
            assert offer.bookingEmails == []
    else:
        assert set(offer.bookingEmails) == set(data["bookingEmails"])
    assert offer.subcategoryId == data["subcategoryId"]
    assert offer.venueId == data["venueId"]
    assert offer.durationMinutes == data["durationMinutes"]
    assert offer.venue.managingOffererId == offerer.id
    assert offer.motorDisabilityCompliant == data["motorDisabilityCompliant"]
    assert offer.visualDisabilityCompliant == data["visualDisabilityCompliant"]
    assert offer.audioDisabilityCompliant == data["audioDisabilityCompliant"]
    assert offer.mentalDisabilityCompliant == data["mentalDisabilityCompliant"]
    assert offer.contactEmail == data["contactEmail"]
    assert offer.contactPhone == data["contactPhone"]
    assert offer.offerVenue == data["offerVenue"]
    assert offer.interventionArea == data["interventionArea"]
    assert {st.value for st in offer.students} == set(data["students"])
    assert {d.id for d in offer.domains} == set(data["domains"])
    assert offer.description == data["description"]
    assert offer.templateId == data["templateId"]
    assert offer.author.full_name == user.full_name
    assert offer.nationalProgramId == data["nationalProgramId"]
    assert {fmt.value for fmt in offer.formats} == set(data["formats"])


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_collective_offer(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        data = base_offer_payload(venue=venue)

        # When
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = CollectiveOffer.query.filter_by(id=offer_id).one()

        assert_offer_values(offer, data, user, offerer)

    def test_create_collective_offer_college_6(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        # When
        data = {**base_offer_payload(venue=venue), "students": ["Collège - 6e"]}
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = CollectiveOffer.query.filter_by(id=offer_id).one()

        assert_offer_values(offer, data, user, offerer)

    def test_create_collective_offer_empty_intervention_area(self, client):
        """Test that intervention area can be empty if offerVenue is set
        to offererVenue
        """
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue)
        data["interventionArea"] = []
        data["offerVenue"] = {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201

    def test_create_offer_from_template_no_domains_nor_intervention_area_nor_booking_emails(self, client):
        """Ensure that if a template id is set, domains, intervention
        area and booking emails can be missing
        Also ensures the contact mail/phone can be missing
        """
        # Given
        venue = offerers_factories.VenueFactory()
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        # When
        data = {
            **base_offer_payload(venue=venue, domains=[], template_id=template.id),
            "interventionArea": [],
            "bookingEmails": [],
        }

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201, response.json

        offer_id = response.json["id"]
        offer = CollectiveOffer.query.filter_by(id=offer_id).one()

        assert_offer_values(offer, data, user, offerer)

    def test_create_offer_from_template_no_contact_email(self, client):
        """Ensure that if a template id is set, domains, intervention
        area and booking emails can be missing
        Also ensures the contact mail/phone can be missing
        """
        # Given
        venue = offerers_factories.VenueFactory()
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, contactEmail=None, contactPhone=None
        )
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        # When
        data = {
            **base_offer_payload(venue=venue, domains=[], template_id=template.id),
            "contactEmail": "",
            "contactPhone": "",
        }

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201, response.json

        offer_id = response.json["id"]
        offer = CollectiveOffer.query.filter_by(id=offer_id).one()

        # Alter contactEmail because we expect None although we sent ""
        data["contactEmail"] = None
        assert_offer_values(offer, data, user, offerer)

    def test_create_offer_from_template_no_contact_email_nor_booking_emails(self, client):
        """Ensure that if a template id is set, domains, intervention
        area and booking emails can be missing
        Also ensures the contact mail/phone can be missing
        """
        # Given
        venue = offerers_factories.VenueFactory()
        template = educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, contactEmail=None, contactPhone=None
        )
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        # When
        data = {
            **base_offer_payload(venue=venue, domains=[], template_id=template.id),
            "interventionArea": [],
            "bookingEmails": [],
            "contactEmail": "",
            "contactPhone": "",
        }

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201, response.json

        offer_id = response.json["id"]
        offer = CollectiveOffer.query.filter_by(id=offer_id).one()

        # Alter contactEmail because we expect None although we sent ""
        data["contactEmail"] = None
        assert_offer_values(offer, data, user, offerer)

    @override_features(WIP_ENABLE_MARSEILLE=True)
    def test_create_collective_offer_primary_level(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "students": ["Écoles Marseille - Maternelle"]}
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201

        offer = CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.students == [models.StudentLevels.ECOLES_MARSEILLE_MATERNELLE]

    @override_features(WIP_ENABLE_MARSEILLE=False)
    def test_create_collective_offer_primary_level_FF_disabled(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "students": ["Écoles Marseille - Maternelle"]}
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert "students" in response.json


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def test_create_collective_offer_random_user(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue)
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 403
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_adage_offerer(self, client):
        # Given
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue)
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer", side_effect=raise_ac):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 403
        assert CollectiveOffer.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_create_collective_offer_unknown_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, subcategory_id="pouet")
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_unselectable_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, subcategory_id=subcategories.OEUVRE_ART.id)
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_collective_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, subcategory_id=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0

    def test_create_collective_offer_empty_domains(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, domains=[])
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert CollectiveOffer.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_create_collective_offer_with_unknown_domain(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        domain = educational_factories.EducationalDomainFactory()

        # When
        data = base_offer_payload(venue=venue, domains=[0, domain.id])

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
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
        data = base_offer_payload(venue=venue, national_program_id=-1)

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "COLLECTIVE_OFFER_NATIONAL_PROGRAM_NOT_FOUND"}

    def test_create_collective_offer_with_no_collective_offer_template(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue, template_id=1234567890)

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 404
        assert response.json == {"code": "COLLECTIVE_OFFER_TEMPLATE_NOT_FOUND"}

    def test_create_collective_offer_no_booking_email(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = {**base_offer_payload(venue=venue), "bookingEmails": []}

        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
