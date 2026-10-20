from flask import Flask


def install_routes(app: Flask) -> None:
    from . import account
    from . import authentication
    from . import bookings
    from . import favorites
    from . import offerers
    from . import reaction
    from . import subscription
