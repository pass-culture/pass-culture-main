import pytest

from pcapi.core.educational import factories
from pcapi.core.educational.api.favorites import get_redactor_all_favorites_count


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return factories.EducationalRedactorFactory()


@pytest.fixture(name="offer")
def collective_offer_fixture(redactor):
    offer = factories.CollectiveStockFactory().collectiveOffer
    redactor.favoriteCollectiveOffers = [offer]
    return offer


@pytest.fixture(name="template")
def collective_offer_template_fixture(redactor):
    offer = factories.CollectiveOfferTemplateFactory()
    redactor.favoriteCollectiveOfferTemplates = [offer]
    return offer


class GetRedactorAllFavoritesCountTest:
    def test_count(self, redactor, offer, template):
        assert get_redactor_all_favorites_count(redactor.id) == 1

    def test_only_collective_offers(self, redactor, offer):
        assert get_redactor_all_favorites_count(redactor.id) == 0

    def test_only_collective_offer_templates(self, redactor, template):
        assert get_redactor_all_favorites_count(redactor.id) == 1

    def test_no_favorites(self, redactor):
        assert not get_redactor_all_favorites_count(redactor.id)

    def test_ignore_not_eligible_for_search_offers(self, redactor, offer, template):
        factories.CollectiveOfferFactory(teacher=redactor)
        assert get_redactor_all_favorites_count(redactor.id) == 1

    def test_igore_favorites_from_another_user(self, redactor, template):
        factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[factories.CollectiveOfferTemplateFactory()]
        )

        assert get_redactor_all_favorites_count(redactor.id) == 1
