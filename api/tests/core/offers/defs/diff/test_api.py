from typing import Literal

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers.defs import models
from pcapi.core.offers.defs import utils
from pcapi.core.offers.defs.diff import api
from pcapi.core.offers.defs.diff import types as diff_types
from pcapi.core.offers.defs.parse import types


class BuildFieldsDiffTest:
    class SameFields:
        src = {types.Field.build(name="f1")}
        compared = {types.Field.build(name="f1")}
        expected_diff = {diff_types.Same("f1")}

    class ShouldBeMissing:
        src = {types.Field.build(name="f1")}
        compared = {types.Field.build(name="f1"), types.Field.build(name="f3")}
        expected_diff = {diff_types.Same("f1"), diff_types.ShouldBeMissing("f3")}

    class ShouldBePresent:
        src = {types.Field.build(name="f1"), types.Field.build(name="f2")}
        compared = {types.Field.build(name="f1")}
        expected_diff = {diff_types.Same("f1"), diff_types.ShouldBePresent("f2")}

    class ShouldBeOptional:
        src = {types.Field.build(name="f1", optional=True)}
        compared = {types.Field.build(name="f1")}
        expected_diff = {diff_types.ShouldBeOptional("f1")}

    class ShouldBeMandatory:
        src = {types.Field.build(name="f1")}
        compared = {types.Field.build(name="f1", optional=True)}
        expected_diff = {diff_types.ShouldBeMandatory("f1")}

    @pytest.mark.parametrize("ctx", [SameFields, ShouldBeMissing, ShouldBePresent, ShouldBeOptional, ShouldBeMandatory])
    def test_build_fields_diff(self, ctx):
        diff = api.build_fields_diff(ctx.src, ctx.compared)
        assert set(diff) == ctx.expected_diff


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


DIGITAL = build_random_subcategory(id="DIGITAL", is_digital_deposit=True)
EVENT = build_random_subcategory(id="EVENT", is_event=True)
DIGITAL_EVENT = build_random_subcategory(id="DIGITAL_EVENT", is_event=True, is_digital_deposit=True)


class DigitalModel(models.Base):
    typology: Literal[models.Typology.DIGITAL] = models.Typology.DIGITAL


class EventModel(models.Base):
    typology: Literal[models.Typology.ACTIVITY_EVENT] = models.Typology.ACTIVITY_EVENT


class DigitalEventModel(models.Base):
    typology: Literal[models.Typology.ACTIVITY_ONLINE_EVENT] = models.Typology.ACTIVITY_ONLINE_EVENT


class RandomModel(models.Base):
    typology: Literal[models.Typology.THINGS] = models.Typology.THINGS


class BuildPropertiesDiffTest:
    @pytest.mark.parametrize("subcategory", [pytest.param(sc, id=sc.id) for sc in subcategories.ALL_SUBCATEGORIES])
    def test_new_models_and_subcategories_have_the_same_properties(self, subcategory):
        diff = api.build_properties_diff(subcategory, utils.MODELS[subcategory.id])
        assert diff.kind == "same"

    def test_digital_subcategory_expects_digital_model(self):
        diff = api.build_properties_diff(DIGITAL, EventModel)
        assert diff.kind == "should_be_digital"

        diff = api.build_properties_diff(DIGITAL, DigitalModel)
        assert diff.kind == "same"

    def test_event_subcategory_expects_event_model(self):
        diff = api.build_properties_diff(EVENT, DigitalModel)
        assert diff.kind == "should_not_be_digital"

        diff = api.build_properties_diff(EVENT, EventModel)
        assert diff.kind == "same"

    def test_digital_event_expects_digital_event_model(self):
        diff = api.build_properties_diff(DIGITAL_EVENT, DigitalModel)
        assert diff.kind == "could_be_an_event"

        diff = api.build_properties_diff(DIGITAL_EVENT, EventModel)
        assert diff.kind == "should_be_digital"

        diff = api.build_properties_diff(DIGITAL_EVENT, DigitalEventModel)
        assert diff.kind == "same"
