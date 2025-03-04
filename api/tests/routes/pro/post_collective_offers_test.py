from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models
from pcapi.core.educational import testing as educational_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as sendinblue_testing


def base_offer_payload(
    venue,
    domains=None,
    subcategory_id=None,
    template_id=None,
    national_program_id=None,
    formats=None,
    add_domain_to_program=True,
) -> dict:
    if domains is None:
        domains = [educational_factories.EducationalDomainFactory().id]

    if not subcategory_id:
        subcategory_id = subcategories.SPECTACLE_REPRESENTATION.id

    if not national_program_id and domains:
        national_program_id = educational_factories.NationalProgramFactory().id

    if national_program_id and add_domain_to_program:
        educational_factories.DomainToNationalProgramFactory(nationalProgramId=national_program_id, domainId=domains[0])

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
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = models.CollectiveOffer.query.get(offer_id)

        assert_offer_values(offer, data, user, offerer)

        # 2 requests (for 2 bookingEmail) for sendinblue
        assert len(sendinblue_testing.sendinblue_requests) == 3

    def test_create_collective_offer_college_6(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user = offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com").user

        # When
        data = {**base_offer_payload(venue=venue), "students": ["Collège - 6e"]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201

        offer_id = response.json["id"]
        offer = models.CollectiveOffer.query.get(offer_id)

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

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 201

    @pytest.mark.features(WIP_ENABLE_MARSEILLE=True)
    def test_create_collective_offer_primary_level(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "students": ["Écoles Marseille - Maternelle"]}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201

        offer = models.CollectiveOffer.query.get(response.json["id"])
        assert offer.students == [models.StudentLevels.ECOLES_MARSEILLE_MATERNELLE]

    @pytest.mark.features(WIP_ENABLE_MARSEILLE=False)
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

    def test_offer_venue_offerer_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.offerVenue == data["offerVenue"]
        assert offer.interventionArea == []

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_school(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": {"addressType": "school", "otherAddress": "", "venueId": None},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.offerVenue == data["offerVenue"]
        assert len(offer.interventionArea) > 0

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    def test_offer_venue_other(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": {"addressType": "other", "otherAddress": "In Paris", "venueId": None},
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.offerVenue == data["offerVenue"]
        assert len(offer.interventionArea) > 0

        assert offer.offererAddressId == None
        assert offer.locationType == None
        assert offer.locationComment == None

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_venue(self, client):
        venue = offerers_factories.VenueFactory()
        oa = venue.offererAddress
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.VENUE.value,
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
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId == oa.id
        assert offer.locationType == models.CollectiveLocationType.VENUE
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "offererVenue", "otherAddress": "", "venueId": venue.id}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_school(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId == None
        assert offer.locationType == models.CollectiveLocationType.SCHOOL
        assert offer.locationComment is None

        assert offer.offerVenue == {"addressType": "school", "otherAddress": "", "venueId": None}

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_location_address(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.ADDRESS.value,
                "locationComment": None,
                "address": {
                    "isVenueAddress": False,
                    "isManualEdition": False,
                    "city": "Paris",
                    "label": "My address",
                    "latitude": "48.87171",
                    "longitude": "2.308289",
                    "postalCode": "75001",
                    "street": "3 Rue de Valois",
                },
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()

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
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": None,
            "location": {
                "locationType": models.CollectiveLocationType.TO_BE_DEFINED.value,
                "locationComment": "Right here",
                "address": None,
            },
        }

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 201
        offer = models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()

        assert offer.offererAddressId == None
        assert offer.locationType == models.CollectiveLocationType.TO_BE_DEFINED
        assert offer.locationComment == "Right here"

        assert offer.offerVenue == {"addressType": "other", "otherAddress": "Right here", "venueId": None}


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
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 403
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_adage_offerer(self, client):
        # Given
        def raise_ac(*args, **kwargs):
            raise educational_exceptions.CulturalPartnerNotFoundException("pouet")

        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")

        # When
        data = base_offer_payload(venue=venue)
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH, side_effect=raise_ac):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        # Then
        assert response.status_code == 403
        assert models.CollectiveOffer.query.count() == 0

    def test_offerer_address_venue_not_allowed(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")
        other_venue = offerers_factories.VenueFactory()

        data = {
            **base_offer_payload(venue=venue),
            "offerVenue": {"addressType": "offererVenue", "otherAddress": "", "venueId": other_venue.id},
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }


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
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_unselectable_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, subcategory_id=subcategories.OEUVRE_ART.id)
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_collective_category(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, subcategory_id=subcategories.SUPPORT_PHYSIQUE_FILM.id)
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_empty_domains(self, client):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user=user)

        # When
        data = base_offer_payload(venue=venue, domains=[])
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth(user.email).post("/collective/offers", json=data)

        # Then
        assert response.status_code == 400
        assert models.CollectiveOffer.query.count() == 0

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
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_booking_email(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "bookingEmails": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"bookingEmails": ["Un email doit etre renseigné."]}
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_intervention_area(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "interventionArea": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"interventionArea": ["intervention_area must have at least one value"]}
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_no_domains(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "domains": []}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"domains": ["domains must have at least one value"]}
        assert models.CollectiveOffer.query.count() == 0

    def test_create_collective_offer_description_invalid(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "description": "too_long" * 200}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"description": ["La description de l’offre doit faire au maximum 1500 caractères."]}
        assert models.CollectiveOffer.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_create_collective_offer_cannot_receive_offer_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"offerVenue": ["Cannot receive offerVenue, use location instead"]}
        assert models.CollectiveOffer.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_create_collective_offer_must_receive_location(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "offerVenue": None, "location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["location must be provided"]}
        assert models.CollectiveOffer.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=False)
    def test_create_collective_offer_cannot_receive_location(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {
            **base_offer_payload(venue=venue),
            "location": {
                "locationType": models.CollectiveLocationType.SCHOOL.value,
                "locationComment": None,
                "address": None,
            },
        }
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"location": ["Cannot receive location, use offerVenue instead"]}
        assert models.CollectiveOffer.query.count() == 0

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=False)
    def test_create_collective_offer_must_receive_offer_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = {**base_offer_payload(venue=venue), "offerVenue": None, "location": None}
        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 400
        assert response.json == {"offerVenue": ["offerVenue must be provided"]}
        assert models.CollectiveOffer.query.count() == 0


@pytest.mark.usefixtures("db_session")
class Returns404Test:
    def test_create_collective_offer_with_unknown_domain(self, client):
        # Given
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        domain = educational_factories.EducationalDomainFactory()

        # When
        data = base_offer_payload(venue=venue, domains=[0, domain.id], add_domain_to_program=False)

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
            venue=venue, national_program_id=national_program.id, domains=[domain.id], add_domain_to_program=False
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

    def test_create_collective_offer_with_unknown_venue_in_offer_venue(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer, user__email="user@example.com")

        data = base_offer_payload(venue=venue)
        data["offerVenue"] = {"addressType": "offererVenue", "otherAddress": "", "venueId": 0}

        with patch(educational_testing.PATCH_CAN_CREATE_OFFER_PATH):
            response = client.with_session_auth("user@example.com").post("/collective/offers", json=data)

        assert response.status_code == 404
        assert response.json == {"venueId": "The venue does not exist."}
