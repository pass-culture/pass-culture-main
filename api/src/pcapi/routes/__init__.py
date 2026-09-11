import enum

from flask import Flask

from pcapi import settings


class UrlPrefix(enum.Enum):
    NATIVE = "/native"
    ADAGE_IFRAME = "/adage-iframe"
    SAML = "/saml"


def install_all_routes(app: Flask) -> None:
    from pcapi.routes.adage.blueprint import adage_blueprint
    from pcapi.routes.adage_iframe.blueprint import adage_iframe as adage_iframe_blueprint
    from pcapi.routes.apis import misc_blueprint
    from pcapi.routes.auth.blueprint import discord_blueprint
    from pcapi.routes.external.blueprint import external_blueprint
    from pcapi.routes.internal.blueprint import testing_blueprint
    from pcapi.routes.native.blueprint import native_blueprint
    from pcapi.routes.pro.blueprint import pro_blueprint
    from pcapi.routes.public.blueprints import provider_blueprint
    from pcapi.routes.saml.blueprint import saml_blueprint as saml_blueprint_blueprint

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

    adage.install_routes(app)
    external.install_routes(app)
    internal.install_routes(app)
    native.install_routes(app)
    auth.install_routes(app)
    pro.install_routes(app)
    public.install_routes(app)
    saml.install_routes(app)
    adage_iframe.install_routes(app)
    institutional.install_routes(app)

    app.register_blueprint(adage_blueprint)
    app.register_blueprint(native_blueprint, url_prefix=UrlPrefix.NATIVE.value)
    app.register_blueprint(provider_blueprint)
    app.register_blueprint(pro_blueprint)
    app.register_blueprint(adage_iframe_blueprint, url_prefix=UrlPrefix.ADAGE_IFRAME.value)
    app.register_blueprint(saml_blueprint_blueprint, url_prefix=UrlPrefix.SAML.value)
    app.register_blueprint(misc_blueprint)
    app.register_blueprint(external_blueprint)
    app.register_blueprint(discord_blueprint)

    if not settings.IS_PROD:
        # last protection if it is misconfigured in prod
        app.register_blueprint(testing_blueprint)
