#!/usr/bin/env python
import typing

from flask import Response
from flask import flash
from flask import make_response
from flask import render_template
from flask import request
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect

from pcapi import settings
from pcapi.core.users.sessions import install_backoffice_login
from pcapi.flask_app import app
from pcapi.flask_app import setup_metrics
from pcapi.routes.backoffice import static_utils
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "bo_session"
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
app.config["REMEMBER_COOKIE_DURATION"] = 120 * 60
app.config["REMEMBER_COOKIE_NAME"] = "bo_remember_me"
app.config["PERMANENT_SESSION_LIFETIME"] = 120 * 60
app.config["USE_GLOBAL_ATOMIC"] = True

csrf = CSRFProtect()
csrf.init_app(app)


@app.after_request
def add_headers(response: Response) -> Response:
    # Cache static files in the browser to avoid many requests when every page is loaded, which would cause many
    # database queries for users in before_request() and many logs printed (on 2024-10-09, 36 files, 72 db queries).
    if request.path.startswith("/static/") or request.path.startswith("/favicon"):
        response.headers["Cache-Control"] = "public,max-age=3600"

    return response


@app.errorhandler(CSRFError)
def handle_csrf_error(error: typing.Any) -> tuple[str, int]:
    mark_transaction_as_invalid()
    return render_template("errors/csrf.html"), 400


def generate_error_response(errors: dict, backoffice_template_name: str = "errors/generic.html") -> Response:
    from pcapi.routes.backoffice import utils

    content = ""
    # In case of a request coming from htmx, display errors as flash messages
    if utils.is_request_from_htmx():
        for error_line in utils.format_response_error_messages(errors):
            flash(error_line, "danger")
    else:
        content = render_template(
            backoffice_template_name,
            errors=errors,
            static_hashes=static_utils.get_hashes(),
        )
    return make_response(content)


with app.app_context():
    from pcapi.routes import error_handlers  # noqa F401
    from pcapi.routes.backoffice import install_routes
    from pcapi.routes.backoffice.blueprint import backoffice_web
    import pcapi.routes.backoffice.error_handlers  # noqa F401

    static_utils.generate_bundles()
    install_backoffice_login()
    install_routes(app)
    app.register_blueprint(backoffice_web, url_prefix="/")

    app.generate_error_response = generate_error_response

    setup_metrics(app)

# This is only called when running pcapi locally
# Deployments use ENTRYPOINT exec ./entrypoint.sh
if __name__ == "__main__":
    port = settings.FLASK_BACKOFFICE_PORT
    is_debugger_enabled = settings.IS_DEV and settings.DEBUG_ACTIVATED
    if is_debugger_enabled:
        import debugpy

        if not debugpy.is_client_connected():
            debug_port = 10003
            debugpy.listen(("0.0.0.0", debug_port))
            print(
                f"⏳ Code debugger can now be attached on port {debug_port}, press F5 in VS Code for example ⏳",
                flush=True,
            )
            debugpy.wait_for_client()
            print("🎉 Code debugger attached, enjoy debugging 🎉", flush=True)

    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=not is_debugger_enabled)
