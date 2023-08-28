from flask import url_for
import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


class FavoriteTemplateTest:
    endpoint = "adage_iframe.post_collective_template_favorites"

    def test_post_favorite_offer_template_test(self, client, caplog):
        collectiveOfferTemplate1 = educational_factories.CollectiveOfferTemplateFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        response = test_client.post(
            url_for(self.endpoint),
            json={"offerId": collectiveOfferTemplate1.id},
        )

        assert response.status_code == 200
        assert response.json == {
            "educationalRedactorId": educational_redactor.id,
            "collectiveOfferTemplateId": collectiveOfferTemplate1.id,
        }

    def test_post_favorite_no_template_test(self, client, caplog):
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        response = test_client.post(
            url_for(self.endpoint),
            json={"offerId": 1234},
        )

        assert response.status_code == 404
        assert response.json == {"offer": ["Aucune offre trouvée pour cet id."]}

    def test_post_favorite_not_authentified_test(self, client, caplog):
        collectiveOffer1 = educational_factories.CollectiveOfferFactory()

        # when
        response = client.post(
            url_for(self.endpoint),
            json={"offerId": collectiveOffer1.id},
        )

        assert response.status_code == 403
        assert response.json == {"Authorization": "Unrecognized token"}
