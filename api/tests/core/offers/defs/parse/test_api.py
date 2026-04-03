import pytest

from pcapi.core.offers.defs.models import things as things_models
from pcapi.core.offers.defs.parse import api
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
