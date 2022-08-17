from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import authentication
    from . import bookings
    from . import features
    from . import logs
    from . import offers
    from . import venues
