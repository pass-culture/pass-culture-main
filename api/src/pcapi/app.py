#!/usr/bin/env python
import typing

from pcapi import settings
from pcapi.flask_integration.app_builder.backend import BackendAppBuilder
from pcapi.flask_integration.utils import build_app


if typing.TYPE_CHECKING:
    from flask import Flask


def create_app() -> "Flask":
    return build_app(builder=BackendAppBuilder())


# This is only called when running pcapi locally
# Deployments use ENTRYPOINT exec ./entrypoint.sh
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
                f"⏳ Code debugger can now be attached on port {debug_port}, press F5 in VS Code for example ⏳.",
                flush=True,
            )
            debugpy.wait_for_client()
            print("🎉 Code debugger attached, enjoy debugging 🎉", flush=True)

    create_app().run(host=ip, port=port, debug=True, use_reloader=use_reloader)
