import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers.defs import models
from pcapi.core.offers.defs import utils
from pcapi.core.offers.defs.diff import api
from pcapi.core.offers.defs.diff import types as diff_types
from pcapi.core.offers.defs.parse import types


class BuildFieldsDiffTest:
    def test_same_fields(self):
        src = {types.Field.build(name="f1")}
        compared = {types.Field.build(name="f1")}

        diff = api.build_fields_diff(src, compared)
        assert set(diff) == {diff_types.Same("f1")}

    def test_should_be_missing(self):
        src = {types.Field.build(name="f1")}
        compared = {types.Field.build(name="f1"), types.Field.build(name="f3")}

        diff = api.build_fields_diff(src, compared)
        assert set(diff) == {diff_types.Same("f1"), diff_types.ShouldBeMissing("f3")}

    def test_should_be_present(self):
        src = {types.Field.build(name="f1"), types.Field.build(name="f2")}
        compared = {types.Field.build(name="f1")}

        diff = api.build_fields_diff(src, compared)
        assert set(diff) == {diff_types.Same("f1"), diff_types.ShouldBePresent("f2")}

    def test_should_be_optional(self):
        src = {types.Field.build(name="f1", optional=True)}
        compared = {types.Field.build(name="f1")}

        diff = api.build_fields_diff(src, compared)
        assert set(diff) == {diff_types.ShouldBeOptional("f1")}

    def test_should_be_mandatory(self):
        src = {types.Field.build(name="f1")}
        compared = {types.Field.build(name="f1", optional=True)}

        diff = api.build_fields_diff(src, compared)
        assert set(diff) == {diff_types.ShouldBeMandatory("f1")}


def build_random_subcategory(**kwargs):
    return subcategories.Subcategory(
        **{
            "id": "ID",
            "category": "nope",
            "pro_label": "Label",
            "app_label": "Label",
            "homepage_label_name": "NONE",
            "is_event": False,
            "conditional_fields": {},
            "can_expire": True,
            "can_be_duo": False,
            "online_offline_platform": "ONLINE",
            "is_digital_deposit": False,
            "is_physical_deposit": False,
            "reimbursement_rule": "STANDARD",
            **kwargs,
        }
    )


RANDOM = build_random_subcategory(id="RANDOM")
DIGITAL = build_random_subcategory(id="DIGITAL", is_digital_deposit=True)
EVENT = build_random_subcategory(id="EVENT", is_event=True)
DIGITAL_EVENT = build_random_subcategory(id="DIGITAL_EVENT", is_event=True, is_digital_deposit=True)
UNSELECTABLE = build_random_subcategory(id="UNSELECTABLE", is_selectable=False)


RandomModel = models.LivrePapierModel
DigitalModel = models.PodcastModel
EventModel = models.ConcertModel
DigitalEventModel = models.LivestreamMusiqueModel
UnselectableModel = models.OeuvreArtModel


class BuildPropertiesDiffTest:
    @pytest.mark.parametrize("subcategory", [pytest.param(sc, id=sc.id) for sc in subcategories.ALL_SUBCATEGORIES])
    def test_new_models_and_subcategories_have_the_same_properties(self, subcategory):
        diff = api.build_typology_diff(subcategory, utils.MODELS[subcategory.id])
        assert diff == "same"

    def test_digital_subcategory_expects_digital_model(self):
        diff = api.build_typology_diff(DIGITAL, EventModel)
        assert diff == "should_be_digital"

        diff = api.build_typology_diff(DIGITAL, DigitalModel)
        assert diff == "same"

    def test_event_subcategory_expects_event_model(self):
        diff = api.build_typology_diff(EVENT, RandomModel)
        assert diff == "should_be_activity"

        diff = api.build_typology_diff(RANDOM, EventModel)
        assert diff == "should_not_be_activity"

        diff = api.build_typology_diff(EVENT, EventModel)
        assert diff == "same"

    def test_digital_event_expects_digital_event_model(self):
        diff = api.build_typology_diff(DIGITAL_EVENT, DigitalModel)
        assert diff == "should_be_activity"

        diff = api.build_typology_diff(DIGITAL_EVENT, EventModel)
        assert diff == "should_be_digital"

        diff = api.build_typology_diff(DIGITAL_EVENT, DigitalEventModel)
        assert diff == "same"

    def test_unselectable_subcategory_expects_unselectable_model(self):
        diff = api.build_typology_diff(EVENT, UnselectableModel)
        assert diff == "should_be_selectable"

        diff = api.build_typology_diff(UNSELECTABLE, EventModel)
        assert diff == "should_not_be_selectable"

        diff = api.build_typology_diff(UNSELECTABLE, UnselectableModel)
        assert diff == "same"


class BuildModelAndSubcategoryFieldsDiffStatusTest:
    @pytest.mark.parametrize("subcategory", [pytest.param(sc, id=sc.id) for sc in subcategories.ALL_SUBCATEGORIES])
    def test_model_should_have_no_fields_diff_with_its_subcategory(self, subcategory):
        model = utils.MODELS[subcategory.id]
        status = api.build_model_and_subcategory_fields_diff_status(model, subcategory)
        assert status.kind == "no_diff"
