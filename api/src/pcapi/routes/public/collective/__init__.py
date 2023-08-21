from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import

    from .endpoints import bookings
    from .endpoints import categories
    from .endpoints import domains
    from .endpoints import educational_institutions
    from .endpoints import offers
    from .endpoints import students_levels
    from .endpoints import venues
