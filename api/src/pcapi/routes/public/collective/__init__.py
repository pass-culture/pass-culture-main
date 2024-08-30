from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import

    from .endpoints import bookings
    from .endpoints import categories
    from .endpoints import domains
    from .endpoints import educational_institutions
    from .endpoints import national_programs
    from .endpoints import offers
    from .endpoints import students_levels
    from .endpoints import venues

    if not settings.IS_PROD:
        # do not import this route when inside production environment.
        # it should not be exposed by automatic documentation tools.
        from .endpoints.simulate_adage_steps import bookings as simulate_adage_bookings
