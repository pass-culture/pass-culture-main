from flask import Flask


def install_routes(app: Flask) -> None:
    from . import (
        academies,
        authentication,
        bookings,
        educational_institution,
        favorites,
        features,
        logs,
        offers,
        playlists,
        redactor,
        venues,
    )
