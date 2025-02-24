import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


class AdageFavoriteDeleteTest:
    def test_delete_favorite_template_test(self, client):
        template = educational_factories.CollectiveOfferTemplateFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        educational_redactor = educational_factories.EducationalRedactorWithFavoriteCollectiveOfferTemplateFactory(
            favoriteCollectiveOfferTemplates=[template]
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        # when
        response = test_client.delete(
            f"/adage-iframe/collective/template/{template.id}/favorites",
        )

        assert response.status_code == 204
        assert not educational_redactor.favoriteCollectiveOfferTemplates

    def test_delete_already_deleted_favorite_template_test(self, client):
        template = educational_factories.CollectiveOfferTemplateFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        educational_redactor = educational_factories.EducationalRedactorWithFavoriteCollectiveOfferTemplateFactory(
            favoriteCollectiveOfferTemplates=[template]
        )

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        # when
        response = test_client.delete(
            f"/adage-iframe/collective/template/{template.id}/favorites",
        )

        assert response.status_code == 204
        assert not educational_redactor.favoriteCollectiveOfferTemplates

        # when
        response = test_client.delete(
            f"/adage-iframe/collective/template/{template.id}/favorites",
        )
        assert response.status_code == 204

    def test_delete_favorite_no_template_test(self, client):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        # when
        response = test_client.delete(
            "/adage-iframe/collective/template/gnagnagna",
        )

        assert response.status_code == 404
