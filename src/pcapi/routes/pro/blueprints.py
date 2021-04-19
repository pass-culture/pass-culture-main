from flask import Blueprint
from spectree import SpecTree

from pcapi.serialization.utils import before_handler
from pcapi.validation.routes import users_authentifications


pro_api_v1 = Blueprint("pro_api_v1", __name__)


API_KEY_AUTH = "ApiKeyAuth"


class ProApiV1BluePrints(SpecTree):
    def _generate_spec(self) -> dict:
        schema = super()._generate_spec()
        schema["components"]["securitySchemes"] = {
            API_KEY_AUTH: {
                "type": "http",
                "scheme": "bearer",
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
                    if users_authentifications.API_KEY in func.requires_authentication:
                        schema["paths"][path][method.lower()]["security"] = [{API_KEY_AUTH: []}]

        return schema


api = ProApiV1BluePrints("flask", MODE="strict", before=before_handler, PATH="/")
api.register(pro_api_v1)
