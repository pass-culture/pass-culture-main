import datetime

from flask import url_for
import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import offer_mixin
from pcapi.utils import db as db_utils
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")

EMAIL = "toto@mail.com"


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai="1234UAI")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory(email=EMAIL)


@pytest.fixture(name="offer")
def offer_fixture():
    offer_range = educational_factories.DateRangeFactory(
        start=datetime.datetime.utcnow() - datetime.timedelta(days=7),
        end=datetime.datetime.utcnow() - datetime.timedelta(days=1),
    )
    return offer_range


class CollectiveOfferTemplateTest:
    def test_get_collective_offer_template(self, eac_client, redactor):
        IMG_URL = "http://localhost/some/picture.png"
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue__bannerUrl=IMG_URL,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=educational_factories.NationalProgramFactory().id,
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        with assert_num_queries(4):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.status == "ACTIVE"
        assert response.json == {
            "description": "offer description",
            "id": offer.id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "venue": {
                "adageId": None,
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "distance": None,
                "id": offer.venue.id,
                "imgUrl": IMG_URL,
                "managingOfferer": {"name": offer.venue.managingOfferer.name},
                "name": offer.venue.name,
                "postalCode": "75000",
                "publicName": offer.venue.publicName,
            },
            "interventionArea": offer.interventionArea,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "contactForm": offer.contactForm.value,
            "contactUrl": offer.contactUrl,
            "offerVenue": {
                "addressType": "offererVenue",
                "address": venue.address,
                "city": venue.city,
                "distance": None,
                "name": venue.name,
                "otherAddress": "",
                "postalCode": venue.postalCode,
                "publicName": venue.publicName,
                "venueId": venue.id,
            },
            "students": ["Lycée - Seconde"],
            "offerId": None,
            "educationalPriceDetail": "détail du prix",
            "domains": [{"id": offer.domains[0].id, "name": offer.domains[0].name}],
            "imageUrl": None,
            "imageCredit": None,
            "nationalProgram": {"id": offer.nationalProgramId, "name": offer.nationalProgram.name},
            "isFavorite": False,
            "dates": {
                "start": format_into_utc_date(offer.start),
                "end": format_into_utc_date(offer.end),
            },
            "formats": [fmt.value for fmt in subcategories.SEANCE_CINE.formats],
            "isTemplate": True,
        }

    def test_get_collective_offer_template_if_inactif(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=educational_factories.NationalProgramFactory().id,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=7),
                end=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            ),
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        # 5. fetch the venue's images
        with assert_num_queries(5):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.status == offer_mixin.OfferStatus.INACTIVE.value

    def test_get_collective_offer_template_without_date_range(self, eac_client, redactor):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="offer name",
            description="offer description",
            priceDetail="détail du prix",
            students=[StudentLevels.GENERAL2],
            offerVenue={
                "venueId": venue.id,
                "addressType": "offererVenue",
                "otherAddress": "",
            },
            nationalProgramId=educational_factories.NationalProgramFactory().id,
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=None,
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        # 5. fetch the venue's images
        with assert_num_queries(5):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert offer.status == offer_mixin.OfferStatus.ACTIVE.value

    def test_is_a_redactors_favorite(self, eac_client):
        """Ensure that the isFavorite field is true only if the
        redactor added it to its favorites.
        """
        offer = educational_factories.CollectiveOfferTemplateFactory()
        educational_factories.EducationalRedactorFactory(email=EMAIL, favoriteCollectiveOfferTemplates=[offer])

        dst = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer template and related data
        # 3. find out if its a redactor's favorite
        # 4. fetch the venue's images
        with assert_num_queries(4):
            response = eac_client.get(dst)

        assert response.status_code == 200
        assert response.json["isFavorite"]

    def test_should_return_404_when_no_collective_offer_template(self, eac_client, redactor):
        response = eac_client.get("/adage-iframe/collective/offers-template/0")
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation",
        [
            offer_mixin.OfferValidationStatus.DRAFT,
            offer_mixin.OfferValidationStatus.PENDING,
            offer_mixin.OfferValidationStatus.REJECTED,
        ],
    )
    def test_should_return_404_when_collective_offer_template_is_not_approved(self, eac_client, redactor, validation):
        offer = educational_factories.CollectiveOfferTemplateFactory(validation=validation)
        response = eac_client.get(f"/adage-iframe/collective/offers-template/{offer.id}")
        assert response.status_code == 404

    def test_non_redactor_is_ok(self, eac_client):
        """Ensure that an authenticated user that is a not an
        educational redactor can still fetch offers informations.
        """
        offer = educational_factories.CollectiveOfferTemplateFactory()
        dst = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the venue's images
        with assert_num_queries(3):
            response = eac_client.get(dst)

        assert response.status_code == 200
