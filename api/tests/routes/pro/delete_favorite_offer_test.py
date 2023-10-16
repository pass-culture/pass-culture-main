import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


class AdageFavoriteDeleteTest:
    def test_delete_favorite_offer_test(self, client):
        offer = educational_factories.CollectiveOfferFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        educational_redactor = educational_factories.EducationalRedactorWithFavoriteCollectiveOffer(
            favoriteCollectiveOffers=[offer]
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        response = test_client.delete(
            f"/adage-iframe/collective/offer/{offer.id}/favorites",
        )

        assert response.status_code == 204
        assert not educational_redactor.favoriteCollectiveOffers

    def test_delete_favorite_no_offer_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        # when
        response = test_client.delete(
            "/adage-iframe/collective/offer/gnagnagna/favorites",
        )

        assert response.status_code == 404
