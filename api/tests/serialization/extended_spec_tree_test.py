from flask import Blueprint
from spectree import SecurityScheme
from spectree import Tag

from pcapi.serialization.decorator import spectree_serialize
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.spec_tree import _AUTHENTICATION_ATTRIBUTE
from pcapi.serialization.spec_tree import add_security_scheme


AUTH_KEY = "API_KEY"

SECURITY_SCHEME = SecurityScheme(
    name=AUTH_KEY,
    data={"type": "http", "scheme": "bearer", "description": "Api key issued by passculture"},  # type: ignore[arg-type]
)

api_schema = ExtendedSpecTree(
    "flask",
    description="SpecTree schema using added by ExtendedSpecTree params",
    tags=[
        Tag(name="TAG_1", description="coucou toi"),
        Tag(name="TAG_2", description="hey you!"),
    ],
    humanize_operation_id=True,
    security_schemes=[SECURITY_SCHEME],
)


# Fake decorator
def api_key_auth(func):
    add_security_scheme(func, AUTH_KEY)
    return func


# Registered by flask_app in `conftest.py`
test_extended_spec_tree_blueprint = Blueprint(
    "test_extended_spec_tree_blueprint", "coucou", url_prefix="/test-extended-spec-tree"
)


# Fake endpoint with no auth
@test_extended_spec_tree_blueprint.route("/", methods=["GET"])
@spectree_serialize(
    on_success_status=204,
    api=api_schema,
)
def spectree_get_test_endpoint():
    pass


# Fake endpoint with auth
@test_extended_spec_tree_blueprint.route("/require_auth", methods=["POST"])
@api_key_auth
@spectree_serialize(
    on_success_status=204,
    api=api_schema,
)
def spectree_post_test_endpoint():
    pass


# Register fake endpoints
api_schema.register(test_extended_spec_tree_blueprint)


class ExtendedSpecTreeTest:
    def test_should_document_endpoint_security_properly(self):
        spec = api_schema._generate_spec()
        assert "security" not in spec["paths"]["/test-extended-spec-tree/"]["get"]
        assert spec["paths"]["/test-extended-spec-tree/require_auth"]["post"]["security"] == [{AUTH_KEY: []}]

    def test_should_order_tags(self):
        spec = api_schema._generate_spec()
        assert spec["tags"] == [
            {"description": "coucou toi", "name": "TAG_1", "externalDocs": None},
            {"description": "hey you!", "name": "TAG_2", "externalDocs": None},
        ]

    def test_should_humanize_operationId(self):
        spec = api_schema._generate_spec()
        assert spec["paths"]["/test-extended-spec-tree/"]["get"]["operationId"] == "SpectreeGetTestEndpoint"
        assert (
            spec["paths"]["/test-extended-spec-tree/require_auth"]["post"]["operationId"] == "SpectreePostTestEndpoint"
        )


class AddSecuritySchemeTest:
    def test_should_add_security_scheme(self):
        def controller():
            pass

        add_security_scheme(controller, "fingerprint")
        add_security_scheme(controller, "faceid", ["pour les trucs vachement importants"])

        assert getattr(controller, _AUTHENTICATION_ATTRIBUTE) == [
            {"fingerprint": []},
            {"faceid": ["pour les trucs vachement importants"]},
        ]
