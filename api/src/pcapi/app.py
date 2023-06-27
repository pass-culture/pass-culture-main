#!/usr/bin/env python
import os

from flask_jwt_extended import JWTManager
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.flask_app import app
from pcapi.flask_app import setup_metrics


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = not settings.IS_DEV
app.config["SESSION_COOKIE_SAMESITE"] = settings.SESSION_COOKIE_SAMESITE
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SECURE"] = not settings.IS_DEV
app.config["REMEMBER_COOKIE_DURATION"] = 90 * 24 * 3600
app.config["PERMANENT_SESSION_LIFETIME"] = 90 * 24 * 3600
app.config["FLASK_ADMIN_SWATCH"] = "flatly"
app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
app.config["WTF_CSRF_ENABLED"] = False

jwt = JWTManager(app)


with app.app_context():
    # pylint: disable=unused-import
    from pcapi.routes import install_all_routes
    import pcapi.utils.login_manager

    install_all_routes(app)

    setup_metrics(app)


if __name__ == "__main__":
    port = settings.FLASK_PORT
    if settings.IS_DEV and settings.DEBUG_ACTIVATED:
        import debugpy

        if not debugpy.is_client_connected():
            debug_port = 10002
            debugpy.listen(("0.0.0.0", debug_port))
            print(
                f"⏳ Code debugger can now be attached on port {debug_port}, press F5 in VS Code for example ⏳",
                flush=True,
            )
            debugpy.wait_for_client()
            print("🎉 Code debugger attached, enjoy debugging 🎉", flush=True)

    set_tag("pcapi.app_type", "app")
    debug = use_reloader = True
    if "DEBUG_METRICS" in os.environ:
        # 'prometheus_flask_exporter' does not play well when debug mode is on.
        debug = use_reloader = False
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=use_reloader)
