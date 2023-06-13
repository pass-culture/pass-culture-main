from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    # pylint: disable=unused-import
    from . import accounts
    from . import auth
    from . import autocomplete
    from . import collective_bookings
    from . import collective_offer_templates
    from . import custom_reimbursement_rules
    from . import filters
    from . import fraud
    from . import health_check
    from . import home
    from . import i18n
    from . import individual_bookings
    from . import move_siret
    from . import offers
    from . import pro
    from . import pro_users
    from . import tags
    from . import users
    from . import venues
    from .admin import blueprint as admin_blueprint
    from .admin import bo_users_blueprint
    from .collective_offers import blueprint as collective_offers_blueprint
    from .multiple_offers import blueprint as multiple_offers_blueprint
    from .offer_validation_rules import blueprint as offer_validation_rule_blueprint
    from .offerers import offerer_blueprint
    from .offerers import offerer_tag_blueprint
    from .offerers import validation_blueprint
    from .pivots import blueprint as pivots_blueprint
    from .providers import blueprint as providers_blueprint
    from .titelive import blueprint as titelive_blueprint

    if settings.ENABLE_TEST_USER_GENERATION:
        from .user_generation import blueprint as user_generation_blueprint

    filters.install_template_filters(app)
    i18n.install_template_filters(app)
