import pytest

from pcapi.core.offers.services.diff import api
from pcapi.core.offers.services.diff import types as diff_types
from pcapi.core.offers.services.parse import types


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
