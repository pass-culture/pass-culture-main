from flask import Blueprint
from spectree import SpecTree

from pcapi.routes.native import security
from pcapi.serialization.utils import before_handler


native_v1 = Blueprint("native_v1", __name__)


class NativeSpecTree(SpecTree):
    def _generate_spec(self) -> dict:
        schema = super()._generate_spec()
        schema["components"]["securitySchemes"] = {
            "JWTAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }

        # Find routes that are protected by authentication
        # We may drop this whenever Spectree supports authentication
        for route in self.backend.find_routes():
            path, _parameters = self.backend.parse_path(route)
            if path not in schema["paths"]:
                continue
            for method, func in self.backend.parse_func(route):
                if method.lower() not in schema["paths"][path]:
                    continue
                if self.backend.bypass(func, method) or self.bypass(func):
                    continue

                if getattr(func, "requires_authentication", None):
                    if security.JWT_AUTH in func.requires_authentication:
                        schema["paths"][path][method.lower()]["security"] = [{"JWTAuth": []}]

        return schema


api = NativeSpecTree("flask", MODE="strict", before=before_handler, PATH="/")
api.register(native_v1)
