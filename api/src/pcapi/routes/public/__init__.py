from flask import Flask


def install_routes(app: Flask) -> None:
    from . import individual_offers

    individual_offers.install_routes(app)
