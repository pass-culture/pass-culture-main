from flask import Flask


def install_routes(app: Flask) -> None:
    from . import collective
    from . import individual_offers

    collective.install_routes(app)
    individual_offers.install_routes(app)
