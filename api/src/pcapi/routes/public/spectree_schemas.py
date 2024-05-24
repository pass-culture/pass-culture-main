from spectree import SecurityScheme
from spectree.models import Server

from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.validation.routes import users_authentifications

from .documentation_constants import descriptions
from .documentation_constants import tags


_INTEGRATION_SERVER = Server(
    url="https://backend.integration.passculture.pro", description="Integration test server", variables=None
)
_PRODUCTION_SERVER = Server(url="https://backend.passculture.app", description="Production server", variables=None)

_servers = [_INTEGRATION_SERVER, _PRODUCTION_SERVER]

# Schema of current public API
public_api_schema = ExtendedSpecTree(
    "flask",
    title="Pass Culture REST API",
    description=descriptions.PUBLIC_API_DESCRIPTION,
    PATH="/",
    MODE="strict",
    version="1.0",
    tags=tags.OPEN_API_TAGS,
    before=serialization_utils.public_api_before_handler,
    security_schemes=[
        SecurityScheme(
            name=users_authentifications.API_KEY_AUTH_NAME,
            data={"type": "http", "scheme": "bearer", "description": "Api key issued by passculture"},  # type: ignore [arg-type]
        ),
    ],
    servers=_servers,
    humanize_operation_id=True,
)

# Schema of deprecated APIs
deprecated_public_api_schema = ExtendedSpecTree(
    "flask",
    title="DEPRECATED",
    MODE="strict",
    before=serialization_utils.before_handler,
    PATH="/deprecated",
    tags=tags.DEPRACTED_TAGS,
    security_schemes=[
        SecurityScheme(
            name=users_authentifications.API_KEY_AUTH_NAME,
            data={"type": "http", "scheme": "bearer", "description": "Api key issued by passculture"},  # type: ignore [arg-type]
        ),
        SecurityScheme(
            name=users_authentifications.COOKIE_AUTH_NAME, data={"type": "apiKey", "in": "cookie", "name": "session"}  # type: ignore [arg-type]
        ),
    ],
    servers=_servers,
    humanize_operation_id=True,
    version="0.1",
)
