from pcapi.core.categories import subcategories
from pcapi.core.offers.services import utils
from pcapi.core.offers.services import shared
from pcapi.core.offers.services import things_with_ean


class MapSubcategoriesToModelsTest():
    def test_map_subcategories_to_models(self):
        objs = utils.map_subcategories_to_models()
        assert objs.keys() <= subcategories.ALL_SUBCATEGORIES_DICT.keys()


class PartialValidationTest:
    def test_validate_thing(self):
        obj = utils.partial_validation(
            things_with_ean.CDModel,
            subcategoryId=subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            name="name",
            venue={"id": 1, "code": shared.VenueTypeCode.BOOKSTORE},
            product={"id": 1},
            audio_disability_compliant=True,
            mental_disability_compliant=True,
            motor_disability_compliant=True,
            visual_disability_compliant=True,
        )
