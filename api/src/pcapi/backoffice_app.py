#!/usr/bin/env python
import typing

from flask import render_template
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
from livereload import Server
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.flask_app import app
from pcapi.routes.backoffice_v3.scss import preprocess_scss


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = not settings.IS_DEV
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "bo_session"
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SECURE"] = not settings.IS_DEV
app.config["REMEMBER_COOKIE_DURATION"] = 120 * 60
app.config["REMEMBER_COOKIE_NAME"] = "bo_remember_me"
app.config["PERMANENT_SESSION_LIFETIME"] = 120 * 60

csrf = CSRFProtect()
csrf.init_app(app)


@app.errorhandler(CSRFError)
def handle_csrf_error(error: typing.Any) -> tuple[str, int]:
    return render_template("errors/csrf.html"), 400


with app.app_context():
    # pylint: disable=unused-import
    from pcapi.routes import error_handlers  # pylint: disable=unused-import
    from pcapi.routes.backoffice_v3 import install_routes
    from pcapi.routes.backoffice_v3.blueprint import backoffice_v3_web
    import pcapi.routes.backoffice_v3.error_handlers  # pylint: disable=unused-import
    import pcapi.utils.login_manager

    preprocess_scss(settings.IS_DEV)
    install_routes(app)
    app.register_blueprint(backoffice_v3_web, url_prefix="/backofficev3")


if __name__ == "__main__":
    port = settings.FLASK_PORT
    if settings.IS_DEV and settings.DEBUG_ACTIVATED:
        import debugpy

        if not debugpy.is_client_connected():
            debugpy.listen(("0.0.0.0", 10003))
            print("⏳ Code debugger can now be attached, press F5 in VS Code for example ⏳", flush=True)
            debugpy.wait_for_client()
            print("🎉 Code debugger attached, enjoy debugging 🎉", flush=True)

    set_tag("pcapi.app_type", "app")
    if settings.BACKOFFICE_LIVE_RELOAD_SERVER:
        # remember to use DEBUG mode for templates auto reload
        # https://github.com/lepture/python-livereload/issues/144
        app.debug = True
        live_server = Server(app.wsgi_app)
        live_server.serve(host="0.0.0.0", port=port, debug=True)
    else:
        app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
