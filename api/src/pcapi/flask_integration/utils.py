import typing


if typing.TYPE_CHECKING:
    from flask import Flask

    from pcapi.flask_integration.app_builder.common import AppBuilder


def build_app(builder: "AppBuilder") -> "Flask":
    builder.before_app_creation()
    app = builder.create_app()
    builder.after_app_creation(app)
    builder.install_extensions(app)
    builder.install_middleware(app)
    with app.app_context():
        builder.install_routes(app)
        builder.install_handlers(app)
        builder.finalize_startup(app)
    return app
