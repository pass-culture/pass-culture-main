import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.testing import assert_num_queries

import tests
from tests.routes import image_data


IMAGES_DIR = Path(tests.__path__[0]) / "files"
UPLOAD_FOLDER = settings.LOCAL_STORAGE_DIR / educational_models.CollectiveOffer.FOLDER

PATH = ""


@pytest.fixture(name="venue_provider")
def venue_provider_fixture():
    return provider_factories.VenueProviderFactory()


@pytest.fixture(name="api_key")
def api_key_fixture(venue_provider):
    return offerers_factories.ApiKeyFactory(provider=venue_provider.provider)


@pytest.fixture(name="venue")
def venue_fixture(venue_provider):
    return venue_provider.venue


@pytest.fixture(name="national_program")
def national_program_fixture():
    return educational_factories.NationalProgramFactory()


@pytest.fixture(name="domain")
def domain_fixture(national_program):
    return educational_factories.EducationalDomainFactory(nationalPrograms=[national_program])


@pytest.fixture(name="institution")
def institution_fixture():
    return educational_factories.EducationalInstitutionFactory()


@pytest.fixture(name="payload")
def payload_fixture(venue_provider, domain, institution, national_program, venue):
    return {
        "venueId": venue.id,
        "name": "Un nom en français ævœc des diàcrtîtïqués",
        "description": "une description d'offre",
        "formats": [subcategories.EacFormat.CONCERT.value],
        "bookingEmails": ["offerer-email@example.com", "offerer-email2@example.com"],
        "contactEmail": "offerer-contact@example.com",
        "contactPhone": "+33100992798",
        "domains": [domain.id],
        "durationMinutes": 183,
        "students": [educational_models.StudentLevels.COLLEGE4.name],
        "audioDisabilityCompliant": True,
        "mentalDisabilityCompliant": True,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
        "offerVenue": {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        },
        "isActive": True,
        "nationalProgramId": national_program.id,
        # stock part
        "beginningDatetime": (datetime.datetime.utcnow() + datetime.timedelta(days=2)).isoformat(timespec="seconds"),
        "bookingLimitDatetime": (datetime.datetime.utcnow() + datetime.timedelta(days=2)).isoformat(timespec="seconds"),
        "totalPrice": 35621,
        "numberOfTickets": 30,
        "educationalPriceDetail": "Justification du prix",
        # link to educational institution
        "educationalInstitutionId": institution.id,
        "imageCredit": "pouet",
        "imageFile": image_data.GOOD_IMAGE,
    }


@pytest.fixture(name="public_client")
def public_client_fixture(client):
    return client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicPostOfferTest:
    def teardown_method(self, *args):
        """clear images after each tests"""
        storage_folder = UPLOAD_FOLDER / educational_models.CollectiveOffer.__name__.lower()
        if storage_folder.exists():
            for child in storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()

    def test_post_offers(
        self, public_client, payload, venue_provider, api_key, domain, institution, national_program, venue
    ):
        # TODO(jeremieb): it seems that we have a lot of queries...
        # 1. fetch feature flag
        # 2. fetch api key
        # 3. fetch venue
        # 4. fetch educational domain
        # 5. fetch educational domain (again)
        # 6. fetch educational institution
        # 7. insert collective offer
        # 8. insert collective offer domain
        # 9. insert collective stock
        # 10. fetch offer
        # 11. fetch offer validation rule
        # 12. update collective offer
        # 13. savepoint
        # 14. fetch collective offer
        # 15. update collective offer
        # 16. savepoint
        # 17. fetch collective offer
        # 18. fetch national program
        # 19. fetch collective stock
        # 20. fetch collective booking
        # 21. fetch educational domain
        # 22. fetch educational institution
        with assert_num_queries(22):
            with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
                response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == institution.id
        assert offer.interventionArea == []
        assert offer.offerVenue == {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }
        assert offer.providerId == venue_provider.providerId
        assert offer.hasImage is True
        assert offer.isPublicApi
        assert offer.nationalProgramId == national_program.id
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()
        assert offer.formats == [subcategories.EacFormat.CONCERT]

    def test_post_offers_with_uai(self, public_client, payload, venue_provider, api_key, domain, institution, venue):
        payload["educationalInstitution"] = institution.institutionId
        del payload["educationalInstitutionId"]

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 200

        offer = educational_models.CollectiveOffer.query.filter_by(id=response.json["id"]).one()
        assert offer.students == [educational_models.StudentLevels.COLLEGE4]
        assert offer.venueId == venue.id
        assert offer.name == payload["name"]
        assert offer.domains == [domain]
        assert offer.institutionId == institution.id
        assert offer.interventionArea == []
        assert offer.offerVenue == {
            "venueId": venue.id,
            "addressType": "offererVenue",
            "otherAddress": "",
        }
        assert offer.providerId == venue_provider.providerId
        assert offer.hasImage is True
        assert offer.isPublicApi
        assert (UPLOAD_FOLDER / offer._get_image_storage_id()).exists()

    def test_post_offers_with_uai_and_institution_id(self, public_client, payload, api_key, institution):
        payload["educationalInstitution"] = institution.institutionId
        payload["educationalInstitutionId"] = institution.id

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "__root__" in response.json

    def test_invalid_api_key(self, public_client, payload):
        with patch("pcapi.core.offerers.api.can_offerer_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 401

    def test_user_cannot_create_collective_offer(self, public_client, payload, api_key):
        with patch(
            "pcapi.core.offerers.api.can_venue_create_educational_offer",
            side_effect=educational_exceptions.CulturalPartnerNotFoundException,
        ):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 403

    def test_bad_educational_institution(self, public_client, payload, api_key):
        payload["educationalInstitutionId"] = -1

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404

    def test_bad_venue_id(self, public_client, payload, venue_provider, api_key):
        payload["venueId"] = -1

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404

    def test_invalid_image_size(self, public_client, payload, api_key):
        payload["imageFile"] = image_data.WRONG_IMAGE_SIZE

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "imageFile" in response.json

    def test_invalid_image_type(self, public_client, payload, api_key):
        payload["imageFile"] = image_data.WRONG_IMAGE_TYPE

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "imageFile" in response.json

    def test_post_offers_institution_not_active(self, public_client, payload, api_key):
        institution = educational_factories.EducationalInstitutionFactory(isActive=False)
        payload["educationalInstitutionId"] = institution.id

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 403

    def test_post_offers_invalid_domain(self, public_client, payload, api_key):
        payload["domains"] = [-1]

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert "domains" in response.json

    def test_national_program_not_linked_to_domains(self, public_client, payload, api_key):
        payload["nationalProgramId"] = educational_factories.NationalProgramFactory().id

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert "national_program" in response.json

    def test_invalid_offer_venue(self, public_client, payload, api_key, venue):
        payload["offerVenue"] = {
            "venueId": venue.id,
            "addressType": "other",
            "otherAddress": "",
        }

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 404
        assert "offerVenue.otherAddress" in response.json

    def test_missing_both_subcategory_and_formats(self, public_client, payload, api_key):
        del payload["formats"]

        with patch("pcapi.core.offerers.api.can_venue_create_educational_offer"):
            response = public_client.post("/v2/collective/offers/", json=payload)

        assert response.status_code == 400
        assert response.json == {"__root__": ["subcategory_id & formats: at least one should not be null"]}
