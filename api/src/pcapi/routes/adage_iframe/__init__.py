from flask import Flask


def install_routes(app: Flask) -> None:
    from . import academies
    from . import authentication
    from . import bookings
    from . import educational_institution
    from . import favorites
    from . import features
    from . import logs
    from . import offers
    from . import playlists
    from . import redactor
    from . import venues
