from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import account
    from . import authentication
    from . import bookings
    from . import cookies_consent
    from . import cultural_survey
    from . import favorites
    from . import offerers
    from . import offers
    from . import settings
    from . import subscription
    from . import universal_links
