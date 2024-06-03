from datetime import datetime

from flask import url_for
import pytest
import time_machine

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


def get_test_client(client, redactor, institution):
    if not institution:
        return client.with_adage_token(email=redactor.email, uai=None)
    return client.with_adage_token(email=redactor.email, uai=institution.institutionId)


class GetFavoriteOfferTest:
    endpoint = "adage_iframe.get_collective_favorites"

    @time_machine.travel("2020-11-17 15:00:00")
    def test_get_favorite_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            collectiveOffer__subcategoryId=subcategories.SEANCE_CINE.id,
            collectiveOffer__name="offer name",
            collectiveOffer__description="offer description",
            price=10,
            collectiveOffer__students=[StudentLevels.GENERAL2],
            collectiveOffer__educational_domains=[educational_factories.EducationalDomainFactory()],
            collectiveOffer__institution=educational_institution,
            collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(),
            collectiveOffer__nationalProgramId=national_program.id,
        )

        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory(
            subcategoryId=subcategories.EVENEMENT_CINE.id,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOffers=[stock.collectiveOffer],
            favoriteCollectiveOfferTemplates=[collective_offer_template],
        )

        test_client = get_test_client(client, educational_redactor, educational_institution)

        # fetch redactor (1 query)
        # fetch collective offer (1 query)
        # fetch collective offer images data (1 query)
        # fetch collective offer template (1 query)
        # fetch collective offer template images data (1 query)
        with assert_num_queries(5):
            response = test_client.get(url_for(self.endpoint))
        assert response.status_code == 200
        assert response.json == {
            "favoritesOffer": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": stock.collectiveOffer.id,
                    "description": "offer description",
                    "isExpired": False,
                    "isSoldOut": False,
                    "isFavorite": True,
                    "name": "offer name",
                    "stock": {
                        "id": stock.id,
                        "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                        "startDatetime": format_into_utc_date(stock.startDatetime),
                        "endDatetime": format_into_utc_date(stock.endDatetime),
                        "bookingLimitDatetime": format_into_utc_date(stock.bookingLimitDatetime),
                        "isBookable": True,
                        "price": 1000,
                        "numberOfTickets": 25,
                        "educationalPriceDetail": stock.priceDetail,
                    },
                    "venue": {
                        "adageId": None,
                        "address": "1 boulevard Poissonnière",
                        "city": "Paris",
                        "distance": None,
                        "id": stock.collectiveOffer.venue.id,
                        "imgUrl": None,
                        "managingOfferer": {"name": stock.collectiveOffer.venue.managingOfferer.name},
                        "name": stock.collectiveOffer.venue.name,
                        "postalCode": "75000",
                        "departmentCode": stock.collectiveOffer.venue.departementCode,
                        "publicName": stock.collectiveOffer.venue.publicName,
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                    },
                    "students": ["Lycée - Seconde"],
                    "offerVenue": {
                        "addressType": "other",
                        "otherAddress": "1 rue des polissons, Paris 75017",
                        "venueId": None,
                        "name": None,
                        "publicName": None,
                        "address": None,
                        "postalCode": None,
                        "city": None,
                        "distance": None,
                    },
                    "contactEmail": "collectiveofferfactory+contact@example.com",
                    "contactPhone": "+33199006328",
                    "durationMinutes": None,
                    "offerId": None,
                    "educationalPriceDetail": None,
                    "domains": [
                        {"id": stock.collectiveOffer.domains[0].id, "name": stock.collectiveOffer.domains[0].name}
                    ],
                    "educationalInstitution": {
                        "id": educational_institution.id,
                        "name": educational_institution.name,
                        "postalCode": "75000",
                        "city": "PARIS",
                        "institutionType": "COLLEGE",
                    },
                    "interventionArea": ["93", "94", "95"],
                    "imageCredit": None,
                    "imageUrl": None,
                    "teacher": {
                        "email": stock.collectiveOffer.teacher.email,
                        "firstName": "Reda",
                        "lastName": "Khteur",
                        "civility": "M.",
                    },
                    "nationalProgram": {
                        "id": stock.collectiveOffer.nationalProgram.id,
                        "name": stock.collectiveOffer.nationalProgram.name,
                    },
                    "formats": [fmt.value for fmt in subcategories.SEANCE_CINE.formats],
                    "isTemplate": False,
                }
            ],
            "favoritesTemplate": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": collective_offer_template.id,
                    "description": collective_offer_template.description,
                    "isExpired": False,
                    "isSoldOut": False,
                    "isFavorite": True,
                    "name": collective_offer_template.name,
                    "venue": {
                        "adageId": None,
                        "address": "1 boulevard Poissonnière",
                        "city": "Paris",
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "distance": None,
                        "id": collective_offer_template.venue.id,
                        "imgUrl": None,
                        "managingOfferer": {"name": collective_offer_template.venue.managingOfferer.name},
                        "name": collective_offer_template.venue.name,
                        "postalCode": "75000",
                        "departmentCode": stock.collectiveOffer.venue.departementCode,
                        "publicName": collective_offer_template.venue.publicName,
                    },
                    "students": ["Lycée - Seconde"],
                    "offerVenue": {
                        "addressType": "other",
                        "distance": None,
                        "otherAddress": "1 rue des polissons, Paris 75017",
                        "venueId": None,
                        "name": None,
                        "publicName": None,
                        "address": None,
                        "postalCode": None,
                        "city": None,
                    },
                    "contactEmail": "collectiveofferfactory+contact@example.com",
                    "contactPhone": collective_offer_template.contactPhone,
                    "contactUrl": collective_offer_template.contactUrl,
                    "contactForm": collective_offer_template.contactForm.value,
                    "durationMinutes": None,
                    "educationalPriceDetail": None,
                    "offerId": None,
                    "domains": [
                        {
                            "id": collective_offer_template.domains[0].id,
                            "name": collective_offer_template.domains[0].name,
                        }
                    ],
                    "interventionArea": ["2A", "2B"],
                    "imageCredit": None,
                    "imageUrl": None,
                    "nationalProgram": None,
                    "dates": {
                        "start": format_into_utc_date(collective_offer_template.start),
                        "end": format_into_utc_date(collective_offer_template.end),
                    },
                    "formats": [fmt.value for fmt in subcategories.EVENEMENT_CINE.formats],
                    "isTemplate": True,
                }
            ],
        }

    def test_get_favorite_offer_only_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        stock1 = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            collectiveOffer__name="offer name",
            collectiveOffer__description="offer description",
            price=10,
            collectiveOffer__students=[StudentLevels.GENERAL2],
            collectiveOffer__educational_domains=[educational_factories.EducationalDomainFactory()],
            collectiveOffer__institution=educational_institution,
            collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(),
            collectiveOffer__nationalProgramId=national_program.id,
        )
        stock2 = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            collectiveOffer__name="offer name",
            collectiveOffer__description="offer description",
            price=10,
            collectiveOffer__students=[StudentLevels.GENERAL2],
            collectiveOffer__educational_domains=[educational_factories.EducationalDomainFactory()],
            collectiveOffer__institution=educational_institution,
            collectiveOffer__teacher=educational_factories.EducationalRedactorFactory(),
            collectiveOffer__nationalProgramId=national_program.id,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOffers=[stock1.collectiveOffer, stock2.collectiveOffer],
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # fetch redactor (1 query)
        # fetch collective offer (1 query)
        # fetch collective offer template (1 query)
        # fetch images data (1 query)
        with assert_num_queries(4):
            test_client = get_test_client(client, educational_redactor, educational_institution)
            response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 200
        assert response.json["favoritesOffer"]
        assert not response.json["favoritesTemplate"]

    def test_get_favorite_template_only_test(self, client):
        collective_offer_templates = educational_factories.CollectiveOfferTemplateFactory.create_batch(2)
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=collective_offer_templates,
        )
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # fetch redactor (1 query)
        # fetch collective offer (1 query)
        # fetch collective offer template (1 query)
        # fetch images data (1 query)
        with assert_num_queries(4):
            test_client = get_test_client(client, educational_redactor, educational_institution)
            response = test_client.get(url_for(self.endpoint))
            assert response.status_code == 200
            assert not response.json["favoritesOffer"]
            assert response.json["favoritesTemplate"]

    def test_missing_institution_id(self, client):
        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = get_test_client(client, educational_redactor, None)
        response = test_client.get(url_for(self.endpoint))

        assert response.status_code == 403
        assert "institution" in response.json["message"]
