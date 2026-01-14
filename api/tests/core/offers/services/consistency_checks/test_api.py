import typing

import pydantic
import pytest

from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.core.categories.models import ExtraDataFieldEnum
from pcapi.core.categories.models import FieldCondition
from pcapi.core.categories.models import OnlineOfflinePlatformChoices
from pcapi.core.categories.models import ReimbursementRuleChoices
from pcapi.core.offers.services import models
from pcapi.core.offers.services.consistency_checks import api
from pcapi.core.offers.services.diff import types as diff_types
from pcapi.core.offers.services.parse import types


def build_subcategory_fields_base(**kwargs):
    return {
        "id": "WITH_CONDITIONAL_FIELDS",
        "category": pro_categories.TECHNIQUE,
        "pro_label": "pro label",
        "app_label": "app label",
        "homepage_label_name": "COURS",
        "is_event": False,
        "conditional_fields": {},
        "can_expire": True,
        "can_be_duo": False,
        "online_offline_platform": OnlineOfflinePlatformChoices.OFFLINE.value,
        "is_digital_deposit": False,
        "is_physical_deposit": False,
        "reimbursement_rule": ReimbursementRuleChoices.STANDARD.value,
        **kwargs,
    }


class BuildSubcategoryFieldsTest:
    def test_subcategory_with_conditional_fields(self):
        kwargs = build_subcategory_fields_base()
        kwargs["conditional_fields"] = {
            ExtraDataFieldEnum.EAN.value: FieldCondition(
                is_required_in_external_form=True, is_required_in_internal_form=False
            ),
            ExtraDataFieldEnum.AUTHOR.value: FieldCondition(
                is_required_in_external_form=False, is_required_in_internal_form=False
            ),
        }

        subcategory = subcategories.Subcategory(**kwargs)
        fields = api.build_subcategory_fields(subcategory)

        expected = {
            types.Field.build(name=ExtraDataFieldEnum.EAN.value, optional=True),
            types.Field.build(name=ExtraDataFieldEnum.AUTHOR.value, optional=True),
        }
        assert fields == expected

    def test_subcategory_without_conditional_fields(self):
        subcategory = subcategories.Subcategory(**build_subcategory_fields_base())
        assert api.build_subcategory_fields(subcategory) == set()


class DummyExtraData(pydantic.BaseModel):
    info: str | None = None
    version: int


class DummyWithExtraDataModel(models.Base):
    subcategory_id: typing.Literal["DUMMY_WITH_EXTRA_DATA"]
    extra_data: DummyExtraData


class BuildDiffStatusTest:
    class NoDiffToFind:
        conditional_fields = {
            "info": FieldCondition(),
            "version": FieldCondition(is_required_in_internal_form=True),
        }
        expected_diff = {diff_types.Same("info"), diff_types.Same("version")}

    class SubcategoryFieldShouldBeOptional:
        conditional_fields = {"info": FieldCondition(), "version": FieldCondition()}
        expected_diff = {diff_types.Same("info"), diff_types.ShouldBeOptional("version")}

    class SubcategoryFieldShouldBeMandatory:
        conditional_fields = {
            "info": FieldCondition(is_required_in_internal_form=True),
            "version": FieldCondition(is_required_in_internal_form=True),
        }
        expected_diff = {diff_types.ShouldBeMandatory("info"), diff_types.Same("version")}

    class SubcategoryFieldShouldBePresent:
        conditional_fields = {
            "info": FieldCondition(),
            "version": FieldCondition(is_required_in_internal_form=True),
            "new": FieldCondition(),
        }
        expected_diff = {diff_types.Same("info"), diff_types.Same("version"), diff_types.ShouldBePresent("new")}

    class SubcategoryFieldShouldBeMissing:
        conditional_fields = {"info": FieldCondition()}
        expected_diff = {diff_types.Same("info"), diff_types.ShouldBeMissing("version")}

    @pytest.mark.parametrize(
        "ctx",
        [
            NoDiffToFind,
            SubcategoryFieldShouldBeOptional,
            SubcategoryFieldShouldBeMandatory,
            SubcategoryFieldShouldBePresent,
            SubcategoryFieldShouldBeMissing,
        ],
    )
    def test_buil_diff_status(self, ctx):
        model = DummyWithExtraDataModel

        kwargs = build_subcategory_fields_base(id="DUMMY_WITH_EXTRA_DATA")
        kwargs["conditional_fields"] = ctx.conditional_fields
        subcategory = subcategories.Subcategory(**kwargs)

        status = api.build_diff_status(model, subcategory)
        assert status.subcategory_id == "DUMMY_WITH_EXTRA_DATA"
        assert set(status.diff) == ctx.expected_diff


class BuildSubcategoriesDiffStatusTest:
    def test_all_subcategories_are_valid(self):
        status = api.build_subcategories_diff_status()

        found_subcategory_ids = {s.subcategory_id for s in status}
        known_subcategory_ids = set(subcategories.ALL_SUBCATEGORIES_DICT.keys())
        assert found_subcategory_ids == known_subcategory_ids

        for s in status:
            for diff_field in s.diff:
                assert diff_field == diff_types.Same(diff_field.field)
