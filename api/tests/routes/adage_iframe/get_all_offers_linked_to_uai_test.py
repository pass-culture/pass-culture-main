from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class AllOffersByUaiTest:
    def test_all_offers_by_uai(self, client):
        # given

        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.CollectiveOfferFactory()

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

    def test_all_offers_by_uai_favorite(self, client):
        # given

        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.CollectiveOfferFactory()

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
