from flask import Flask


def install_routes(app: Flask) -> None:
    from . import v1

    v1.install_routes(app)
