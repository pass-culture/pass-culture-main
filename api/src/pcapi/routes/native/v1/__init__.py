from flask import Flask


def install_routes(app: Flask) -> None:
    from . import (
        account,
        achievements,
        artists,
        authentication,
        banner,
        bookings,
        cookies_consent,
        cultural_survey,
        favorites,
        feedbacks,
        offerers,
        offers,
        reaction,
        recommendation,
        reminder,
        settings,
        subscription,
        universal_links,
    )
