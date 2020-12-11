from flask import Blueprint
import pydantic.schema
from spectree import SpecTree

from pcapi.serialization.utils import before_handler


native_v1 = Blueprint("native_v1", __name__)


# TODO: Remove PassSpecTree and pydantic patch whenever
# https://github.com/0b01001001/spectree/pull/91 is released
class PassSpecTree(SpecTree):
    def _generate_spec(self) -> dict:
        spec = super()._generate_spec()
        spec["components"]["schemas"].update(spec.pop("definitions", {}))
        return spec


pydantic.schema.default_prefix = "#/components/schemas/"


api = PassSpecTree("flask", MODE="strict", before=before_handler, PATH="/")
api.register(native_v1)
