#!/usr/bin/env python
from sentry_sdk import set_tag
from werkzeug.middleware.profiler import ProfilerMiddleware

from pcapi import settings
from pcapi.flask_app import app
from pcapi.local_providers.install import install_local_providers
from pcapi.routes import install_all_routes


if settings.PROFILE_REQUESTS:
    profiling_restrictions = [settings.PROFILE_REQUESTS_LINES_LIMIT]
    app.config["PROFILE"] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=profiling_restrictions)  # type: ignore [assignment]


def install_login_manager() -> None:
    # pylint: disable=unused-import
    import pcapi.utils.login_manager


with app.app_context():
    if settings.IS_DEV:
        install_local_providers()
    install_login_manager()
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
