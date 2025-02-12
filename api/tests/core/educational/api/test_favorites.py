import pytest

from pcapi.core.educational import factories
from pcapi.core.educational.api.favorites import get_redactor_favorites_count


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="redactor")
def redactor_fixture():
    return factories.EducationalRedactorFactory()


class GetRedactorAllFavoritesCountTest:
    def test_count(self, redactor):
        redactor.favoriteCollectiveOffers = [factories.CollectiveStockFactory().collectiveOffer]
        redactor.favoriteCollectiveOfferTemplates = [factories.CollectiveOfferTemplateFactory()]
        assert get_redactor_favorites_count(redactor.id) == 1

    def test_only_collective_offers(self, redactor):
        redactor.favoriteCollectiveOffers = [factories.CollectiveStockFactory().collectiveOffer]
        assert get_redactor_favorites_count(redactor.id) == 0

    def test_only_collective_offer_templates(self, redactor):
        redactor.favoriteCollectiveOfferTemplates = [factories.CollectiveOfferTemplateFactory()]
        assert get_redactor_favorites_count(redactor.id) == 1

    def test_no_favorites(self, redactor):
        assert get_redactor_favorites_count(redactor.id) == 0

    def test_ignore_not_eligible_for_search_offers(self, redactor):
        redactor.favoriteCollectiveOffers = [factories.CollectiveStockFactory().collectiveOffer]
        redactor.favoriteCollectiveOfferTemplates = [factories.CollectiveOfferTemplateFactory()]
        factories.CollectiveOfferFactory(teacher=redactor)
        assert get_redactor_favorites_count(redactor.id) == 1

    def test_igore_favorites_from_another_user(self, redactor):
        redactor.favoriteCollectiveOfferTemplates = [factories.CollectiveOfferTemplateFactory()]
        factories.EducationalRedactorFactory(
            favoriteCollectiveOfferTemplates=[factories.CollectiveOfferTemplateFactory()]
        )
        assert get_redactor_favorites_count(redactor.id) == 1
