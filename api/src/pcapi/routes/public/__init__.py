from flask import Flask


def install_routes(app: Flask) -> None:
    from . import books_stocks
    from . import individual_offers

    individual_offers.install_routes(app)
    books_stocks.install_routes(app)
