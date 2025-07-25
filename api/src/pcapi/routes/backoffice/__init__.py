from flask import Flask

from pcapi import settings


def install_routes(app: Flask) -> None:
    from . import auth
    from . import autocomplete
    from . import filters
    from . import health_check
    from . import home
    from . import move_siret
    from . import pro
    from . import redirect
    from . import types_
    from .accounts import account_tag_blueprint
    from .accounts import blueprint as accounts_blueprint
    from .accounts import update_request_blueprint
    from .admin import blueprint as admin_blueprint
    from .admin import bo_users_blueprint
    from .bank_account import blueprint as bank_account_blueprint
    from .bookings import collective_bookings_blueprint
    from .bookings import individual_bookings_blueprint
    from .chronicles import blueprint as chronicles_blueprint
    from .collective_offers import collective_offer_templates_blueprint
    from .collective_offers import collective_offers_blueprint
    from .criteria import blueprint as criteria_blueprint
    from .custom_reimbursement_rule import blueprint as custom_reimbursement_rule_blueprint
    from .external.zendesk_sell import blueprint as zendesk_sell_blueprint
    from .finance import finance_incidents_blueprint
    from .fraud import blueprint as fraud_blueprint
    from .gdpr_user_extract import blueprint as gdpr_extract_blueprint
    from .multiple_offers import blueprint as multiple_offers_blueprint
    from .non_payment_notices import blueprint as non_payment_notices_blueprint
    from .offer_price_limitation_rules import blueprint as offer_price_limitation_rule_blueprint
    from .offer_validation_rules import blueprint as offer_validation_rule_blueprint
    from .offerers import offerer_blueprint
    from .offerers import offerer_tag_blueprint
    from .offerers import validation_blueprint
    from .offers import blueprint as offers_blueprint
    from .operations import blueprint as operations_blueprint
    from .pivots import blueprint as pivots_blueprint
    from .preferences import blueprint as preferences_blueprint
    from .pro import blueprint as pro_blueprint
    from .pro_users import blueprint as pro_users_blueprint
    from .products import blueprint as products_blueprint
    from .providers import blueprint as providers_blueprint
    from .titelive import blueprint as titelive_blueprint
    from .users import blueprint as users_blueprint
    from .venues import blueprint as venues_blueprint

    if settings.ENABLE_TEST_USER_GENERATION or settings.ENABLE_BO_COMPONENT_PAGE:
        from .dev import blueprint

    filters.install_template_filters(app)
