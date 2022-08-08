from flask import Flask


def install_all_routes(app: Flask) -> None:
    from pcapi.admin.install import install_admin
    from pcapi.admin.install import install_admin_autocomplete_views
    from pcapi.admin.install import install_admin_template_filters
    from pcapi.models import db
    from pcapi.routes.adage.v1.blueprint import adage_v1 as adage_v1_blueprint
    from pcapi.routes.adage_iframe.blueprint import adage_iframe as adage_iframe_blueprint
    from pcapi.routes.apis import private_api
    from pcapi.routes.apis import public_api
    from pcapi.routes.backoffice.blueprint import backoffice_blueprint
    from pcapi.routes.native.v1.blueprint import native_v1 as native_v1_blueprint
    from pcapi.routes.pro.blueprint import pro_private_api as pro_private_api_blueprint
    from pcapi.routes.pro.blueprint import pro_public_api_v1 as pro_public_api_v1_blueprint
    from pcapi.routes.pro.blueprint import pro_public_api_v2 as pro_public_api_v2_blueprint
    from pcapi.routes.saml.blueprint import saml_blueprint as saml_blueprint_blueprint
    import pcapi.tasks
    from pcapi.tasks.decorator import cloud_task_api

    from . import adage
    from . import adage_iframe
    from . import backoffice
    from . import error_handlers  # pylint: disable=unused-import
    from . import external
    from . import internal
    from . import native
    from . import pro
    from . import saml
    from . import shared
    from .pro import public_api as pro_public_api

    install_admin(app, db.session)
    install_admin_autocomplete_views()
    adage.install_routes(app)
    external.install_routes(app)
    internal.install_routes(app)
    native.install_routes(app)
    pro.install_routes(app)
    pro_public_api.install_routes(app)
    saml.install_routes(app)
    shared.install_routes(app)
    adage_iframe.install_routes(app)
    pcapi.tasks.install_handlers(app)
    install_admin_template_filters(app)
    backoffice.install_routes(app)

    app.register_blueprint(adage_v1_blueprint, url_prefix="/adage/v1")
    app.register_blueprint(native_v1_blueprint, url_prefix="/native/v1")
    app.register_blueprint(pro_public_api_v1_blueprint)
    app.register_blueprint(pro_public_api_v2_blueprint, url_prefix="/v2")
    app.register_blueprint(pro_private_api_blueprint)
    app.register_blueprint(adage_iframe_blueprint, url_prefix="/adage-iframe")
    app.register_blueprint(saml_blueprint_blueprint, url_prefix="/saml")
    app.register_blueprint(cloud_task_api)
    app.register_blueprint(private_api)
    app.register_blueprint(public_api)
    app.register_blueprint(backoffice_blueprint, url_prefix="/backoffice")
