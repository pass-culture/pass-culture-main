import typing

from flask import Blueprint
from flask_cors.extension import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.routes.native import utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


native_blueprint = Blueprint("native", __name__)
native_blueprint.before_request(utils.check_client_version)
CORS(
    native_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_NATIVE,
    supports_credentials=True,
)

JWT_AUTH = "JWTAuth"
SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),  # type: ignore[arg-type]
]

api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)
api.register(native_blueprint)

blueprints: dict[str, Blueprint] = {}


def get_native_blueprint(version: str = "v1") -> Blueprint:
    if version not in blueprints:
        blueprint = Blueprint(f"native_{version}", __name__)
        native_blueprint.register_blueprint(blueprint, url_prefix=f"/{version}")
        blueprints[version] = blueprint

    return blueprints[version]


def native_route(rule: str, version: str = "v1", **kwargs: typing.Any) -> typing.Callable:
    blueprint = get_native_blueprint(version)
    return blueprint.route(rule, **kwargs)
