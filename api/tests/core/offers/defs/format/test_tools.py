import typing

from pcapi.core.offers.defs.format import tools
from pcapi.core.offers.defs.format import types
from pcapi.core.offers.defs.models import things as things_models
from pcapi.core.offers.defs.parse import types as base_types


class BuildSchemasTest:
    def test_schemas_are_sorted_by_subcategory_id(self):
        models = [things_models.LivrePapierModel, things_models.SupportPhysiqueFilmModel]
        schemas = tools.build_schemas(models)
        assert len(schemas) == len(models)
        assert schemas[0].subcategory.id < schemas[1].subcategory.id

    def test_empty_models_input_returns_empty_collection(self):
        assert len(tools.build_schemas([])) == 0


class FormatModelToSchemaTest:
    def test_format_model_as_expected(self):
        model = things_models.LivrePapierModel
        schema, _ = tools.format_model_to_schema({}, model)

        type_annotation = model.model_fields["subcategory_id"].annotation
        subcategory_id = typing.get_args(type_annotation)[0]
        assert schema.subcategory.id == subcategory_id

        found_required = {f.name for f in schema.properties.required}
        expected_required = {k for k, v in model.model_fields.items() if v.is_required()}
        assert found_required == expected_required

    def test_cache_is_filled_with_parent_classes(self):
        model = things_models.LivrePapierModel
        _, cache = tools.format_model_to_schema({}, model)
        assert {"Base"} == set(cache.keys())


class BuildModelHierarchyTest:
    def test_builds_hierarchy_from_empty_cache(self):
        model = things_models.LivrePapierModel
        hierarchy, cache = tools.build_model_hierarchy({}, model)

        assert cache
        assert {f.name for f in hierarchy} == {
            "name",
            "venue",
            "audio_disability_compliant",
            "mental_disability_compliant",
            "motor_disability_compliant",
            "visual_disability_compliant",
            "typology",
            "description",
            "booking_email",
        }

    def test_builds_hierarchy_from_filled_cache(self):
        model = things_models.LivrePapierModel
        _, cache = tools.build_model_hierarchy({}, model)
        hierarchy, updated_cache = tools.build_model_hierarchy(cache, model)

        assert cache == updated_cache
        assert {f.name for f in hierarchy} == {
            "name",
            "venue",
            "audio_disability_compliant",
            "mental_disability_compliant",
            "motor_disability_compliant",
            "visual_disability_compliant",
            "typology",
            "description",
            "booking_email",
        }


class BuildFieldWithOriginTest:
    def test_build_base(self):
        field = base_types.Field.build(name="my_field")
        hierarchy = types.Hierarchy({field})

        field_with_origin = tools.build_field_with_origin(hierarchy, field)
        assert field_with_origin.origin == types.FieldOrigin.BASE

    def test_build_own(self):
        field = base_types.Field.build(name="my_field")
        hierarchy = types.Hierarchy()

        field_with_origin = tools.build_field_with_origin(hierarchy, field)
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
