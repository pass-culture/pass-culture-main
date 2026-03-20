from flask import url_for

from pcapi.routes.native.blueprint import native_blueprint
from pcapi.routes.pro.blueprint import pro_private_api


@native_blueprint.route("/test_write_session")
def write_native_session():
    from flask import session

    session["random_key"] = 123
    return ""


@pro_private_api.route("/test_write_session")
def write_pro_session():
    from flask import session

    session["random_key"] = 123
    return ""


def test_write_session_native(client):
    result = client.get(url_for("native.write_native_session"))
    # we want a hard crash here to forbid usage in dev.
    assert result.status_code == 500


def test_write_session_pro(client):
    result = client.get(url_for("pro_private_api.write_pro_session"))
    assert result.status_code == 200
