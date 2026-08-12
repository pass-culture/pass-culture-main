from flask import Flask


def install_routes(app: Flask) -> None:
    from . import authentication
    from . import offers
    from . import subscription
