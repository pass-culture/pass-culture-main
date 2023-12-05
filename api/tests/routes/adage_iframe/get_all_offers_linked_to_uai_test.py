from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class AllOffersByUaiTest:
    def test_all_offers_by_uai(self, client):
        # given

        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        collective_offer = educational_factories.CollectiveOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            domains=[educational_factories.EducationalDomainFactory()],
            institution=educational_institution,
            teacher=educational_factories.EducationalRedactorFactory(),
            nationalProgramId=national_program.id,
        )
        stock = educational_factories.CollectiveStockFactory(
            price=10,
            collectiveOffer=collective_offer,
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when

        # 1 fetch collective_offer
        # 2 fetch favorite offer
        # 3 fetch favorite_collective_offer
        with assert_num_queries(3):
            response = test_client.get("/adage-iframe/collective/all-offers")

        # then
        assert response.status_code == 200
        assert response.json == {
            "collectiveOffers": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": collective_offer.id,
                    "subcategoryLabel": collective_offer.subcategory.app_label,
                    "description": collective_offer.description,
                    "isExpired": False,
                    "isSoldOut": False,
                    "name": collective_offer.name,
                    "stock": {
                        "id": stock.id,
                        "beginningDatetime": stock.beginningDatetime.isoformat(),
                        "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(),
                        "isBookable": stock.isBookable,
                        "price": 1000,
                        "numberOfTickets": stock.numberOfTickets,
                        "educationalPriceDetail": None,
                    },
                    "venue": {
                        "id": collective_offer.venue.id,
                        "address": "1 boulevard Poissonnière",
                        "city": "Paris",
                        "name": collective_offer.venue.name,
                        "postalCode": collective_offer.venue.postalCode,
                        "publicName": collective_offer.venue.publicName,
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "distance": None,
                        "managingOfferer": {"name": collective_offer.venue.managingOfferer.name},
                        "adageId": None,
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
                    "contactEmail": collective_offer.contactEmail,
                    "contactPhone": collective_offer.contactPhone,
                    "durationMinutes": collective_offer.durationMinutes,
                    "offerId": collective_offer.offerId,
                    "educationalPriceDetail": None,
                    "domains": [{"id": collective_offer.domains[0].id, "name": collective_offer.domains[0].name}],
                    "educationalInstitution": {
                        "id": educational_institution.id,
                        "name": educational_institution.name,
                        "postalCode": educational_institution.postalCode,
                        "city": educational_institution.city,
                        "institutionType": educational_institution.institutionType,
                    },
                    "interventionArea": ["93", "94", "95"],
                    "imageCredit": None,
                    "imageUrl": None,
                    "teacher": {
                        "email": stock.collectiveOffer.teacher.email,
                        "firstName": stock.collectiveOffer.teacher.firstName,
                        "lastName": stock.collectiveOffer.teacher.lastName,
                        "civility": stock.collectiveOffer.teacher.civility,
                    },
                    "nationalProgram": {
                        "id": stock.collectiveOffer.nationalProgram.id,
                        "name": stock.collectiveOffer.nationalProgram.name,
                    },
                    "isFavorite": False,
                    "formats": [fmt.value for fmt in subcategories.SEANCE_CINE.formats],
                }
            ]
        }

    def test_all_offers_by_uai_favorite(self, client):
        # given

        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        national_program = educational_factories.NationalProgramFactory()
        collective_offer = educational_factories.CollectiveOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            domains=[educational_factories.EducationalDomainFactory()],
            institution=educational_institution,
            teacher=educational_factories.EducationalRedactorFactory(),
            nationalProgramId=national_program.id,
            educationalRedactorsFavorite=[educational_redactor],
        )
        stock = educational_factories.CollectiveStockFactory(
            price=10,
            collectiveOffer=collective_offer,
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when

        # 1 fetch collective_offer
        # 2 fetch favorite offer
        # 3 fetch favorite_collective_offer
        with assert_num_queries(3):
            response = test_client.get("/adage-iframe/collective/all-offers")

        # then
        assert response.status_code == 200
        assert response.json == {
            "collectiveOffers": [
                {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": False,
                    "motorDisabilityCompliant": False,
                    "visualDisabilityCompliant": False,
                    "id": collective_offer.id,
                    "subcategoryLabel": collective_offer.subcategory.app_label,
                    "description": collective_offer.description,
                    "isExpired": False,
                    "isSoldOut": False,
                    "name": collective_offer.name,
                    "stock": {
                        "id": stock.id,
                        "beginningDatetime": stock.beginningDatetime.isoformat(),
                        "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(),
                        "isBookable": stock.isBookable,
                        "price": 1000,
                        "numberOfTickets": stock.numberOfTickets,
                        "educationalPriceDetail": None,
                    },
                    "venue": {
                        "id": collective_offer.venue.id,
                        "address": "1 boulevard Poissonnière",
                        "city": "Paris",
                        "name": collective_offer.venue.name,
                        "postalCode": collective_offer.venue.postalCode,
                        "publicName": collective_offer.venue.publicName,
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "distance": None,
                        "managingOfferer": {"name": collective_offer.venue.managingOfferer.name},
                        "adageId": None,
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
                    "contactEmail": collective_offer.contactEmail,
                    "contactPhone": collective_offer.contactPhone,
                    "durationMinutes": collective_offer.durationMinutes,
                    "offerId": collective_offer.offerId,
                    "educationalPriceDetail": None,
                    "domains": [{"id": collective_offer.domains[0].id, "name": collective_offer.domains[0].name}],
                    "educationalInstitution": {
                        "id": educational_institution.id,
                        "name": educational_institution.name,
                        "postalCode": educational_institution.postalCode,
                        "city": educational_institution.city,
                        "institutionType": educational_institution.institutionType,
                    },
                    "interventionArea": ["93", "94", "95"],
                    "imageCredit": None,
                    "imageUrl": None,
                    "teacher": {
                        "email": stock.collectiveOffer.teacher.email,
                        "firstName": stock.collectiveOffer.teacher.firstName,
                        "lastName": stock.collectiveOffer.teacher.lastName,
                        "civility": stock.collectiveOffer.teacher.civility,
                    },
                    "nationalProgram": {
                        "id": stock.collectiveOffer.nationalProgram.id,
                        "name": stock.collectiveOffer.nationalProgram.name,
                    },
                    "isFavorite": True,
                    "formats": [fmt.value for fmt in subcategories.SEANCE_CINE.formats],
                }
            ]
        }

    def test_all_offers_by_uai_not_bookable(self, client):
        # given

        educational_institution = educational_factories.EducationalInstitutionFactory()
        collective_offer = educational_factories.CollectiveOfferFactory(
            institution=educational_institution,
        )

        educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.utcnow() - timedelta(days=1),
            collectiveOffer=collective_offer,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when

        # 1 fetch collective_offer
        # 2 fetch favorite offer
        # 3 fetch favorite_collective_offer
        with assert_num_queries(3):
            response = test_client.get("/adage-iframe/collective/all-offers")

        # then
        assert response.status_code == 200
        assert response.json == {"collectiveOffers": []}

    def test_all_offers_by_uai_no_uai(self, client):
        # given

        national_program = educational_factories.NationalProgramFactory()
        collective_offer = educational_factories.CollectiveOfferFactory(
            domains=[educational_factories.EducationalDomainFactory()],
            institution=None,
            teacher=educational_factories.EducationalRedactorFactory(),
            nationalProgramId=national_program.id,
        )
        educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime(2021, 5, 15),
            price=10,
            collectiveOffer=collective_offer,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(email=educational_redactor.email, uai=None)

        # when
        response = test_client.get("/adage-iframe/collective/all-offers")

        # then
        assert response.status_code == 400
        assert response.json == {"institutionId": "institutionId is required"}
