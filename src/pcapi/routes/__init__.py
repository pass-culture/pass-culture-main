from flask import Flask

from pcapi.routes.apis import private_api
from pcapi.routes.apis import public_api


def install_all_routes(app: Flask) -> None:
    from pcapi.admin.install import install_admin_template_filters
    from pcapi.admin.install import install_admin_views
    from pcapi.flask_app import admin
    from pcapi.models import db
    from pcapi.routes.adage.v1.blueprint import adage_v1
    from pcapi.routes.adage_iframe.blueprint import adage_iframe
    from pcapi.routes.native.v1.blueprint import native_v1
    from pcapi.routes.pro.blueprints import pro_api_v2
    from pcapi.routes.saml.blueprint import saml_blueprint
    import pcapi.tasks
    from pcapi.tasks.decorator import cloud_task_api

    install_admin_views(admin, db.session)
    install_routes(app)
    pcapi.tasks.install_handlers(app)
    install_admin_template_filters(app)

    app.register_blueprint(adage_v1, url_prefix="/adage/v1")
    app.register_blueprint(native_v1, url_prefix="/native/v1")
    app.register_blueprint(pro_api_v2, url_prefix="/v2")
    app.register_blueprint(adage_iframe, url_prefix="/adage-iframe")
    app.register_blueprint(saml_blueprint, url_prefix="/saml")
    app.register_blueprint(cloud_task_api)


def install_routes(app: Flask) -> None:

    from . import adage
    from . import adage_iframe
    from . import error_handlers  # pylint: disable=unused-import
    from . import external
    from . import internal
    from . import native
    from . import pro
    from . import saml
    from . import shared
    from . import webapp

    adage.install_routes(app)
    external.install_routes(app)
    internal.install_routes(app)
    native.install_routes(app)
    pro.install_routes(app)
    saml.install_routes(app)
    shared.install_routes(app)
    webapp.install_routes(app)
    adage_iframe.install_routes(app)

    app.register_blueprint(private_api)
    app.register_blueprint(public_api)
