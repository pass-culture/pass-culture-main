import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers.defs import utils
from pcapi.core.offers.defs.format import tools
from pcapi.core.offers.defs.format import types
from pcapi.core.offers.defs.models import typology
from pcapi.core.offers.defs.parse import types as base_types


class BuildSchemasTest:
    def test_schemas_are_sorted_by_subcategory_id(self):
        schemas = tools.build_schemas(utils.MODELS.values())
        assert len(schemas) == len(utils.MODELS)

        extracted_subcategory_ids = [schema.subcategory.id for schema in schemas]
        assert sorted(extracted_subcategory_ids) == extracted_subcategory_ids

    def test_empty_models_input_returns_empty_collection(self):
        assert len(tools.build_schemas([])) == 0


class FormatModelToSchemaTest:
    @pytest.mark.parametrize("subcategory", [pytest.param(sc, id=sc.id) for sc in subcategories.ALL_SUBCATEGORIES])
    def test_format_model_as_expected(self, subcategory):
        model = utils.MODELS[subcategory.id]
        schema = tools.format_model_to_schema(set(), model)

        assert schema.subcategory.id == subcategory.id

        found_required = {f.name for f in schema.properties.required}
        expected_required = {k for k, v in model.model_fields.items() if v.is_required()}
        assert found_required == expected_required

        found_optional = {f.name for f in schema.properties.optional}
        expected_optional = {k for k, v in model.model_fields.items() if not v.is_required()}
        assert found_optional == expected_optional

    @pytest.mark.parametrize("model", [pytest.param(model, id=model.__name__) for model in typology.DIGITAL])
    def test_format_model_computes_digital_typology_as_expected(self, model):
        schema = tools.format_model_to_schema(set(), model)
        assert {"digital"} <= set(schema.properties.typology)

    @pytest.mark.parametrize("model", [pytest.param(model, id=model.__name__) for model in typology.ACTIVITY])
    def test_format_model_computes_event_typology_as_expected(self, model):
        schema = tools.format_model_to_schema(set(), model)
        assert {"activity"} <= set(schema.properties.typology)

    @pytest.mark.parametrize("model", [pytest.param(model, id=model.__name__) for model in typology.CANNOT_BE_CREATED])
    def test_format_model_computes_unselectable_typology_as_expected(self, model):
        schema = tools.format_model_to_schema(set(), model)
        assert {"unselectable"} <= set(schema.properties.typology)


class BuildFieldWithOriginTest:
    def test_build_base(self):
        field = base_types.Field.build(name="my_field")

        field_with_origin = tools.build_field_with_origin({field}, field)
        assert field_with_origin.origin == types.FieldOrigin.BASE

    def test_build_own(self):
        field = base_types.Field.build(name="my_field")

        field_with_origin = tools.build_field_with_origin(set(), field)
        assert field_with_origin.origin == types.FieldOrigin.OWN


class SortFieldsWithOriginTest:
    def test_sorts_by_origin_and_name(self):
        o1 = types.FieldWithOrigin.from_field(base_types.Field.build(name="o1"), origin=types.FieldOrigin.OWN)
        b1 = types.FieldWithOrigin.from_field(base_types.Field.build(name="b1"), origin=types.FieldOrigin.BASE)
        o2 = types.FieldWithOrigin.from_field(base_types.Field.build(name="o2"), origin=types.FieldOrigin.OWN)
        b2 = types.FieldWithOrigin.from_field(base_types.Field.build(name="b2"), origin=types.FieldOrigin.BASE)

        fields = [o1, b2, b1, o2]
        sorted_fields = tools.sort_fields_with_origin(fields)

        assert sorted_fields == [b1, b2, o1, o2]

    def test_accept_empty_list_and_returns_empty_list(self):
        assert len(tools.sort_fields_with_origin([])) == 0
