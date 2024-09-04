import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.schemas import PatchDraftOfferBodyModel
from pcapi.core.offers.schemas import PostDraftOfferBodyModel


pytestmark = pytest.mark.usefixtures("db_session")


class PostDraftOfferBodyModelTest:
    def test_post_draft_offer_body_model(self):
        venue = offerers_factories.VirtualVenueFactory()
        _ = PostDraftOfferBodyModel(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venueId=venue.id,
            description="description",
            durationMinutes=12,
            extraData={"ean": "12345678910111"},
        )


class PatchDraftOfferBodyModelTest:
    def test_patch_draft_offer_body_model(self):
        _ = PatchDraftOfferBodyModel(
            name="Name", description="description", extraData={"artist": "An-2"}, durationMinutes=12
        )
