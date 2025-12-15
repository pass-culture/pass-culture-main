import pytest

from pcapi.core.categories import pro_categories
from pcapi.core.categories import subcategories
from pcapi.core.categories.models import ExtraDataFieldEnum
from pcapi.core.categories.models import FieldCondition
from pcapi.core.categories.models import OnlineOfflinePlatformChoices
from pcapi.core.categories.models import ReimbursementRuleChoices
from pcapi.core.offers.defs.models import things as things_models
from pcapi.core.offers.defs.parse import api
from pcapi.core.offers.defs.parse import types
from pcapi.core.offers.defs.utils import MODELS


def assert_same_fields(model, fields):
    assert set(model.model_fields.keys()) == {f.name for f in fields}

    required_found = {f.name for f in fields if not f.optional}
    required_expected = {name for name, info in model.model_fields.items() if info.is_required()}
    assert required_found == required_expected

    optional_found = {f.name for f in fields if f.optional}
    optional_expected = {name for name, info in model.model_fields.items() if not info.is_required()}
    assert optional_found == optional_expected


class BuildModelFieldsTest:
    @pytest.mark.parametrize("model", [pytest.param(model, id=subcategory) for subcategory, model in MODELS.items()])
    def test_can_build_any_known_model(self, model):
        fields = api.build_model_fields(model)
        assert_same_fields(model, fields)


class BuildModelExtraDataTest:
    @pytest.mark.parametrize("model", [pytest.param(model, id=subcategory) for subcategory, model in MODELS.items()])
    def test_can_build_from_any_known_model(self, model):
        model = things_models.LivrePapierModel
        extra_data = model.model_fields["extra_data"].annotation
        fields = api.build_model_extra_data_fields(model)
        assert_same_fields(extra_data, fields)


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

        assert fields == {
            types.Field.build(name=ExtraDataFieldEnum.EAN.value, optional=True),
            types.Field.build(name=ExtraDataFieldEnum.AUTHOR.value, optional=True),
        }

    def test_subcategory_without_conditional_fields(self):
        subcategory = subcategories.Subcategory(**build_subcategory_fields_base())
        assert api.build_subcategory_fields(subcategory) == set()
