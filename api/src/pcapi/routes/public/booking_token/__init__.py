from flask import Flask


def install_routes(app: Flask) -> None:
    from . import v2

    v2.install_routes(app)
