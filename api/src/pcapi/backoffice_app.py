#!/usr/bin/env python
import typing

from flask import Response
from flask import make_response
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.flask_app import app
from pcapi.flask_app import setup_metrics
from pcapi.repository import mark_transaction_as_invalid
from pcapi.routes.backoffice.scss import preprocess_scss


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "bo_session"
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
app.config["REMEMBER_COOKIE_DURATION"] = 120 * 60
app.config["REMEMBER_COOKIE_NAME"] = "bo_remember_me"
app.config["PERMANENT_SESSION_LIFETIME"] = 120 * 60

csrf = CSRFProtect()
csrf.init_app(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(error: typing.Any) -> tuple[str, int]:
    mark_transaction_as_invalid()
    return render_template("errors/csrf.html"), 400


def generate_error_response(errors: dict, backoffice_template_name: str = "errors/generic.html") -> Response:
    # If the error happens inside a turbo-frame, it's id is reused to insert the error in the correct place
    turbo_frame_id = request.headers.get("Turbo-Frame")
    content = render_template(backoffice_template_name, errors=errors, turbo_frame_id=turbo_frame_id)
    return make_response(content)


with app.app_context():
    # pylint: disable=unused-import
    from pcapi.routes import error_handlers  # pylint: disable=unused-import
    from pcapi.routes.backoffice import install_routes
    from pcapi.routes.backoffice.blueprint import backoffice_web
    import pcapi.routes.backoffice.error_handlers  # pylint: disable=unused-import
    import pcapi.utils.login_manager

    preprocess_scss(settings.BACKOFFICE_WATCH_SCSS_CHANGE)
    install_routes(app)
    app.register_blueprint(backoffice_web, url_prefix="/")

    app.generate_error_response = generate_error_response

    setup_metrics(app)


if __name__ == "__main__":
    port = settings.FLASK_BACKOFFICE_PORT
    if settings.IS_DEV and settings.DEBUG_ACTIVATED:
        import debugpy

        if not debugpy.is_client_connected():
            debugpy.listen(("0.0.0.0", 10003))
            print("⏳ Code debugger can now be attached, press F5 in VS Code for example ⏳", flush=True)
            debugpy.wait_for_client()
            print("🎉 Code debugger attached, enjoy debugging 🎉", flush=True)

    set_tag("pcapi.app_type", "app")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
