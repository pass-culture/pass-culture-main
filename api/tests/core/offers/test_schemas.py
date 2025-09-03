import pytest

import pcapi.core.offers.exceptions as offers_exceptions
from pcapi.core.offers import schemas


pytestmark = pytest.mark.usefixtures("db_session")


class PatchDraftOfferBodyModelTest:
    def test_patch_draft_offer_body_model(self):
        _ = schemas.PatchDraftOfferBodyModel(
            name="Name", description="description", extraData={"artist": "An-2"}, durationMinutes=12
        )

    def test_patch_offer_with_invalid_subcategory(self):
        with pytest.raises(offers_exceptions.OfferException) as error:
            _ = schemas.PatchDraftOfferBodyModel(
                name="I solemnly swear that my intentions are evil",
                subcategoryId="Misconduct fullfield",
            )

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]
