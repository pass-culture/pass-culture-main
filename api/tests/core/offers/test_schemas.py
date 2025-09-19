import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.exceptions as offers_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.offers import schemas
from pcapi.models.api_errors import ApiErrors


pytestmark = pytest.mark.usefixtures("db_session")


class PostDraftOfferBodyModelTest:
    def test_post_draft_offer_body_model(self):
        venue = offerers_factories.VirtualVenueFactory()
        _ = schemas.PostDraftOfferBodyModel(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venueId=venue.id,
            description="description",
            durationMinutes=12,
            extraData={"ean": "12345678910111"},
        )


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


class CheckOfferNameIsValidTest:
    def test_raises_api_error_when_offer_name_is_too_long(self):
        # Given
        offer_title_too_long = (
            "Nom vraiment très long excédant la taille maximale (nom de plus de quatre-vingt-dix caractères)"
        )

        # When
        with pytest.raises(ApiErrors) as error:
            schemas.check_offer_name_length_is_valid(offer_title_too_long)

        # Then
        assert error.value.errors["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]

    def test_does_not_raise_exception_when_offer_name_length_is_valid(self):
        # Given
        offer_title_less_than_90_characters = "Nom de moins de quatre-vingt-dix caractères"

        # The the following should not raise
        schemas.check_offer_name_length_is_valid(offer_title_less_than_90_characters)


@pytest.mark.parametrize(
    "url,video_id",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("http://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s", "dQw4w9WgXcQ"),
        ("m.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/e/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLUMRshJ8e2c4oQ60D4Ew15A1LgN5C7Y3X", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.other.com", None),
        ("dQw4w9WgXcQ", None),
    ],
)
def test_extract_youtube_video_id_from_url(url, video_id):
    assert schemas.extract_youtube_video_id(url) == video_id
