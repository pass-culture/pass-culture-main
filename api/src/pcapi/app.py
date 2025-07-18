#!/usr/bin/env python
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from sentry_sdk import set_tag

from pcapi import settings
from pcapi.flask_app import app
from pcapi.flask_app import setup_metrics


app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
app.config["SESSION_COOKIE_SAMESITE"] = settings.SESSION_COOKIE_SAMESITE
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_SECURE"] = settings.SESSION_COOKIE_SECURE
app.config["REMEMBER_COOKIE_DURATION"] = 90 * 24 * 3600
app.config["PERMANENT_SESSION_LIFETIME"] = 90 * 24 * 3600
app.config["FLASK_ADMIN_SWATCH"] = "flatly"
app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
app.config["WTF_CSRF_ENABLED"] = False
app.config["USE_GLOBAL_ATOMIC"] = False

jwt = JWTManager(app)
csrf = CSRFProtect()
csrf.init_app(app)


with app.app_context():
    import pcapi.utils.login_manager  # noqa F401
    from pcapi.routes import install_all_routes

    install_all_routes(app)

    setup_metrics(app)


if __name__ == "__main__":
    ip = settings.FLASK_IP
    port = settings.FLASK_PORT
    is_debugger_enabled = settings.IS_DEV and settings.DEBUG_ACTIVATED
    use_reloader = settings.FLASK_USE_RELOADER and not is_debugger_enabled

    if is_debugger_enabled:
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
    app.run(host=ip, port=port, debug=True, use_reloader=use_reloader)
