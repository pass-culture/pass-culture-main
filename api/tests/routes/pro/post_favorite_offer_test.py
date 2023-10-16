import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


class FavoriteOfferTest:
    def test_post_favorite_offer_test(self, client):
        collective_offer = educational_factories.CollectiveOfferFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        response = test_client.post(
            f"/adage-iframe/collective/offers/{collective_offer.id}/favorites",
        )

        assert response.status_code == 204

    def test_post_favorite_no_offer_test(self, client):
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        response = test_client.post(
            "/adage-iframe/collective/offers/non/favorites",
        )
        assert response.status_code == 404

    def test_post_favorite_not_authentified_test(self, client):
        collective_offer = educational_factories.CollectiveOfferFactory()

        # when
        response = client.post(
            f"/adage-iframe/collective/offers/{collective_offer.id}/favorites",
        )

        assert response.status_code == 403
        assert response.json == {"Authorization": "Unrecognized token"}
