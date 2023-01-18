from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import bookings
    from .collective import install_routes as collective_install_routes

    collective_install_routes(app)
