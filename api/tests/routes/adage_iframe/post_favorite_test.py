import logging

from freezegun.api import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2020-11-17 15:00:00")
class FavoriteTest:
    def test_post_favorite_offer_test(self, client, caplog):
        collectiveOffer1 = educational_factories.CollectiveOfferFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/collective/favories",
                json={"offerId": collectiveOffer1.id},
            )

        assert response.status_code == 200
        assert response.json == {
            "educationalRedactor": educational_institution.institutionId,
            "offerId": collectiveOffer1.id,
        }

    def test_post_favorite_offer_template_test(self, client, caplog):
        collectiveOfferTemplate1 = educational_factories.CollectiveOfferTemplateFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/collective/favories",
                json={"offerId": collectiveOfferTemplate1.id},
            )

        assert response.status_code == 200
        assert response.json == {
            "educationalRedactor": educational_institution.institutionId,
            "offerId": collectiveOfferTemplate1.id,
        }

    def test_post_favorite_no_offer_test(self, client, caplog):
        educational_redactor = educational_factories.EducationalRedactorFactory()
        educational_institution = educational_factories.EducationalInstitutionFactory()

        test_client = client.with_adage_token(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # when
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/collective/favories",
                json={"offerId": "I'm gonna make him an offer he can't refuse."},
            )

        assert response.status_code == 400
        assert response.json == {"offerId": ["Saisissez un nombre valide"]}

    def test_post_favorite_not_authentified_test(self, client, caplog):
        collectiveOffer1 = educational_factories.CollectiveOfferFactory()

        # when
        with caplog.at_level(logging.INFO):
            response = client.post(
                "/adage-iframe/collective/favories",
                json={"offerId": collectiveOffer1.id},
            )

        assert response.status_code == 403
        assert response.json == {"Authorization": "Unrecognized token"}
