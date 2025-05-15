from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    from .endpoints import (
        bookings,
        domains,
        educational_institutions,
        national_programs,
        offers,
        students_levels,
        venues,
    )

    if not settings.IS_PROD:
        # do not import this route when inside production environment.
        # it should not be exposed by automatic documentation tools.
        from .endpoints.adage_mock import bookings as adage_mock
