from flask import Blueprint
from spectree import SpecTree

from pcapi.serialization.utils import before_handler


# FIXME: once we have the homemade authentication decorator we should
# be able to flag the routes and automatically list them here
PROTECTED_PATHS = {
    "/me",
    "/id_check_token",
    "/offer/{offer_id}",
}

native_v1 = Blueprint("native_v1", __name__)


class NativeSpecTree(SpecTree):
    def _generate_spec(self) -> dict:
        schema = super()._generate_spec()
        schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
        protected_paths = ["/native/v1" + path for path in PROTECTED_PATHS]
        for path in schema["paths"]:
            if path not in protected_paths:
                continue
            for operation in schema["paths"][path].values():
                operation["security"] = [{"bearerAuth": []}]
        return schema


api = NativeSpecTree("flask", MODE="strict", before=before_handler, PATH="/")
api.register(native_v1)
