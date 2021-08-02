from flask import Flask

from pcapi.flask_app import private_api
from pcapi.flask_app import public_api


def install_routes(app: Flask) -> None:

    from . import adage
    from . import adage_iframe
    from . import error_handlers  # pylint: disable=unused-import
    from . import external
    from . import internal
    from . import native
    from . import pro
    from . import shared
    from . import webapp

    adage.install_routes(app)
    external.install_routes(app)
    internal.install_routes(app)
    native.install_routes(app)
    pro.install_routes(app)
    shared.install_routes(app)
    webapp.install_routes(app)
    adage_iframe.install_routes(app)

    app.register_blueprint(private_api)
    app.register_blueprint(public_api)
