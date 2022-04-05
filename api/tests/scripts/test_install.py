import flask

from pcapi.scripts.install import install_commands


def test_install():
    app = flask.Flask(__name__)
    install_commands(app)
    # Do not test all blueprints. We just want to make sure that the
    # function does not fail and that at least one blueprint is
    # registered.
    assert "pcapi_utils_human_ids" in app.blueprints
