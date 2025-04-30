from flask import Flask


def install_routes(app: Flask) -> None:
    from . import account
    from . import achievements
    from . import artists
    from . import authentication
    from . import banner
    from . import bookings
    from . import cookies_consent
    from . import cultural_survey
    from . import favorites
    from . import feedbacks
    from . import offerers
    from . import offers
    from . import reaction
    from . import recommendation
    from . import reminder
    from . import settings
    from . import subscription
    from . import universal_links
