import enum

from flask import Flask

from pcapi import settings


class UrlPrefix(enum.Enum):
    ADAGE_V1 = "/adage/v1"
    NATIVE = "/native"
    ADAGE_IFRAME = "/adage-iframe"
    SAML = "/saml"
    AUTH = "/auth"


def install_all_routes(app: Flask) -> None:
    import pcapi.tasks
    from pcapi.routes.adage.v1.blueprint import adage_v1 as adage_v1_blueprint
    from pcapi.routes.adage_iframe.blueprint import adage_iframe as adage_iframe_blueprint
    from pcapi.routes.apis import private_api
    from pcapi.routes.apis import public_api
    from pcapi.routes.auth.blueprint import auth_blueprint
    from pcapi.routes.native.blueprint import native_blueprint
    from pcapi.routes.pro.blueprint import pro_private_api as pro_private_api_blueprint
    from pcapi.routes.public import blueprints as public_blueprint
    from pcapi.routes.saml.blueprint import saml_blueprint as saml_blueprint_blueprint
    from pcapi.tasks.decorator import cloud_task_api

    from . import adage
    from . import adage_iframe
    from . import auth
    from . import error_handlers
    from . import external
    from . import institutional
    from . import internal
    from . import native
    from . import pro
    from . import public
    from . import saml
    from . import shared

    adage.install_routes(app)
    external.install_routes(app)
    internal.install_routes(app)
    native.install_routes(app)
    auth.install_routes(app)
    pro.install_routes(app)
    public.install_routes(app)
    saml.install_routes(app)
    shared.install_routes(app)
    adage_iframe.install_routes(app)
    pcapi.tasks.install_handlers(app)
    institutional.install_routes(app)

    app.register_blueprint(adage_v1_blueprint, url_prefix=UrlPrefix.ADAGE_V1.value)
    app.register_blueprint(native_blueprint, url_prefix=UrlPrefix.NATIVE.value)
    app.register_blueprint(public_blueprint.public_api)
    app.register_blueprint(public_blueprint.deprecated_v2_prefixed_public_api)
    app.register_blueprint(public_blueprint.deprecated_collective_public_api)
    app.register_blueprint(pro_private_api_blueprint)
    app.register_blueprint(adage_iframe_blueprint, url_prefix=UrlPrefix.ADAGE_IFRAME.value)
    app.register_blueprint(saml_blueprint_blueprint, url_prefix=UrlPrefix.SAML.value)
    app.register_blueprint(cloud_task_api)
    app.register_blueprint(private_api)
    app.register_blueprint(public_api)
    app.register_blueprint(auth_blueprint, url_prefix=UrlPrefix.AUTH.value)
