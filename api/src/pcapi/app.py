#!/usr/bin/env python
from flask_jwt_extended import JWTManager
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.flask_app import app
from pcapi.local_providers.install import install_local_providers


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = not settings.IS_DEV
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
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

    if settings.IS_DEV and not settings.IS_RUNNING_TESTS:
        install_local_providers()

    install_all_routes(app)


if __name__ == "__main__":
    port = settings.FLASK_PORT
    if settings.IS_DEV and settings.DEBUG_ACTIVATED:
        import debugpy

        if not debugpy.is_client_connected():
            debugpy.listen(("0.0.0.0", 10002))
            print("⏳ Code debugger can now be attached, press F5 in VS Code for example ⏳", flush=True)
            debugpy.wait_for_client()
            print("🎉 Code debugger attached, enjoy debugging 🎉", flush=True)

    set_tag("pcapi.app_type", "app")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
