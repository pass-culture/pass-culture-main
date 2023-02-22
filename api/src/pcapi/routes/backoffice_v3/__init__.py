from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import accounts
    from . import admin
    from . import auth
    from . import autocomplete
    from . import collective_bookings
    from . import filters
    from . import health_check
    from . import home
    from . import i18n
    from . import individual_bookings
    from . import offerers
    from . import offers
    from . import pro
    from . import pro_support
    from . import pro_users
    from . import users
    from . import venues

    filters.install_template_filters(app)
    i18n.install_template_filters(app)
