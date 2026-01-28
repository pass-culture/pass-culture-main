from flask import Flask


def install_routes(app: Flask) -> None:
    from . import v1
    from . import v2
    from . import v3

    v1.install_routes(app)
    v2.install_routes(app)
    v3.install_routes(app)
