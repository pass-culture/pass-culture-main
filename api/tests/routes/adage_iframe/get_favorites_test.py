from datetime import datetime

from freezegun.api import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import StudentLevels
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2020-11-17 15:00:00")
class GetFavoriteOfferTest:
    def test_get_favorite_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            offer__name="offer name",
            offer__description="offer description",
            price=10,
            offer__students=[StudentLevels.GENERAL2],
            offer__educational_domains=[educational_factories.EducationalDomainFactory()],
            offer__institution=educational_institution,
            offer__teacher=educational_factories.EducationalRedactorFactory(),
            offer__nationalProgramId=national_program.id,
        )

        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOffers=[stock.offer],
            favoriteCollectiveOfferTemplates=[collective_offer_template],
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        with assert_num_queries(3):
            response = test_client.get(
                "/adage-iframe/collective/favorites",
            )
        assert response.status_code == 200
        assert response.json == {
            "favoritesOffer": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": stock.offer.id,
                    "subcategoryLabel": stock.offer.subcategoryLabel,
                    "description": "offer description",
                    "isExpired": False,
                    "isSoldOut": False,
                    "name": "offer name",
                    "stock": {
                        "id": stock.id,
                        "beginningDatetime": "2021-05-15T00:00:00",
                        "bookingLimitDatetime": "2021-05-14T23:00:00",
                        "isBookable": True,
                        "price": 1000,
                        "numberOfTickets": 25,
                        "educationalPriceDetail": stock.priceDetail,
                    },
                    "venue": {
                        "id": stock.offer.venue.id,
                        "address": "1 boulevard Poissonnière",
                        "city": "Paris",
                        "name": stock.offer.venue.name,
                        "postalCode": "75000",
                        "publicName": stock.offer.venue.publicName,
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "managingOfferer": {"name": stock.offer.venue.managingOfferer.name},
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
                    },
                    "contactEmail": "collectiveofferfactory+contact@example.com",
                    "contactPhone": "+33199006328",
                    "durationMinutes": None,
                    "offerId": None,
                    "educationalPriceDetail": None,
                    "domains": [{"id": stock.offer.domains[0].id, "name": stock.offer.domains[0].name}],
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
                        "email": stock.offer.teacher.email,
                        "firstName": "Reda",
                        "lastName": "Khteur",
                        "civility": "M.",
                    },
                    "nationalProgram": {
                        "id": stock.offer.nationalProgram.id,
                        "name": stock.offer.nationalProgram.name,
                    },
                }
            ],
            "favoritesTemplate": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": collective_offer_template.id,
                    "subcategoryLabel": collective_offer_template.subcategoryLabel,
                    "description": collective_offer_template.description,
                    "isExpired": False,
                    "isSoldOut": False,
                    "name": collective_offer_template.name,
                    "venue": {
                        "id": collective_offer_template.venue.id,
                        "address": "1 boulevard Poissonnière",
                        "city": "Paris",
                        "name": collective_offer_template.venue.name,
                        "postalCode": "75000",
                        "publicName": collective_offer_template.venue.publicName,
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "managingOfferer": {"name": collective_offer_template.venue.managingOfferer.name},
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
                    },
                    "contactEmail": "collectiveofferfactory+contact@example.com",
                    "contactPhone": "+33199006328",
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
                }
            ],
        }

    def test_get_favorite_offer_only_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            offer__name="offer name",
            offer__description="offer description",
            price=10,
            offer__students=[StudentLevels.GENERAL2],
            offer__educational_domains=[educational_factories.EducationalDomainFactory()],
            offer__institution=educational_institution,
            offer__teacher=educational_factories.EducationalRedactorFactory(),
            offer__nationalProgramId=national_program.id,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOffers=[stock.offer],
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        with assert_num_queries(3):
            response = test_client.get(
                "/adage-iframe/collective/favorites",
            )

        assert response.status_code == 200
        assert response.json["favoritesOffer"]
        assert not response.json["favoritesTemplate"]

    def test_get_favorite_template_only_test(self, client):
        collective_offer_template = educational_factories.CollectiveOfferTemplateFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[collective_offer_template],
        )
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        with assert_num_queries(3):
            response = test_client.get(
                "/adage-iframe/collective/favorites",
            )
        assert response.status_code == 200
        assert not response.json["favoritesOffer"]
        assert response.json["favoritesTemplate"]
