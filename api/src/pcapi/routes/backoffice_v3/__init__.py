from flask import Flask


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import accounts
    from . import admin
    from . import auth
    from . import autocomplete
    from . import collective_bookings
    from . import collective_offer_templates
    from . import collective_offers
    from . import custom_reimbursement_rules
    from . import filters
    from . import health_check
    from . import home
    from . import i18n
    from . import individual_bookings
    from . import move_siret
    from . import offerers
    from . import offers
    from . import pro
    from . import pro_users
    from . import tags
    from . import users
    from . import venues
    from .providers import blueprint

    filters.install_template_filters(app)
    i18n.install_template_filters(app)
