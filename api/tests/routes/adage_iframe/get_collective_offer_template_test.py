from datetime import datetime
from datetime import timedelta

from flask import url_for
from freezegun.api import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models import offer_mixin
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


EMAIL = "toto@mail.com"


@pytest.fixture(name="eac_client")
def eac_client_fixture(client):
    return client.with_adage_token(email=EMAIL, uai="1234UAI")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return educational_factories.EducationalRedactorFactory(email=EMAIL)


@freeze_time("2020-11-17 15:00:00")
class CollectiveOfferTemplateTest:
    def test_get_collective_offer_template(self, eac_client, redactor):
        template_start = datetime.utcnow() + timedelta(days=1)
        template_end = datetime.utcnow() + timedelta(days=100)
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(
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
            startEndDates=[educational_factories.TemplateStartEndDatesFactory()],
        )

        url = url_for("adage_iframe.get_collective_offer_template", offer_id=offer.id)

        # 1. fetch redactor
        # 2. fetch collective offer and related data
        # 3. fetch the offerVenue's details (Venue)
        # 4. find out if its a redactor's favorite
        # 5. find out startEndDates
        with assert_num_queries(5):
            response = eac_client.get(url)

        assert response.status_code == 200
        assert response.json == {
            "description": "offer description",
            "id": offer.id,
            "isExpired": False,
            "isSoldOut": False,
            "name": "offer name",
            "subcategoryLabel": offer.subcategory.app_label,
            "venue": {
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                "id": offer.venue.id,
                "name": offer.venue.name,
                "postalCode": "75000",
                "publicName": offer.venue.publicName,
                "managingOfferer": {"name": offer.venue.managingOfferer.name},
            },
            "interventionArea": offer.interventionArea,
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "durationMinutes": None,
            "contactEmail": offer.contactEmail,
            "contactPhone": offer.contactPhone,
            "offerVenue": {
                "addressType": "offererVenue",
                "address": venue.address,
                "city": venue.city,
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
            "startEndDates": [
                {
                    "end": format_into_utc_date(offer.startEndDates[0].end),
                    "id": offer.startEndDates[0].id,
                    "start": format_into_utc_date(offer.startEndDates[0].start),
                }
            ],
        }
        assert offer.startEndDates
        start_end_dates = offer.startEndDates

        assert len(start_end_dates) == 1
        assert start_end_dates[0].start == template_start
        assert start_end_dates[0].end == template_end

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
        # 4. find out startEndDates
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
        # 3. find out startEndDates
        with assert_num_queries(3):
            response = eac_client.get(dst)

        assert response.status_code == 200
