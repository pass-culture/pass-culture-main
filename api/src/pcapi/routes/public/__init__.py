from flask import Flask


def install_routes(app: Flask) -> None:
    from . import booking_token
    from . import collective
    from . import individual_offers

    booking_token.install_routes(app)
    collective.install_routes(app)
    individual_offers.install_routes(app)
