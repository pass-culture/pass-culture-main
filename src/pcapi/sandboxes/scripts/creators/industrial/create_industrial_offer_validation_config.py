import logging

from pcapi.core.offers.api import import_offer_validation_config
from pcapi.repository.user_queries import find_user_by_email


logger = logging.getLogger(__name__)


def create_industrial_offer_validation_config() -> None:
    logger.info("create_industrial_offer_validation_config")
    super_admin = find_user_by_email("pctest.admin93.0@example.com")
    previous_config_yaml = """
    minimum_score: 0.6
    parameters:
        name:
            model: "Offer"
            attribute: "name"
            condition:
                operator: "not in"
                comparated:
                    - "REJECTED"
                    - "PENDING"
                    - "DRAFT"
            factor: 0
        price_all_types:
            model: "Offer"
            attribute: "max_price"
            condition:
                operator: ">"
                comparated: 100
            factor: 0.7
    """
    config_yaml = """
    minimum_score: 0.6
    parameters:
        name:
            model: "Offer"
            attribute: "name"
            condition:
                operator: "contains"
                comparated:
                    - "REJECTED"
                    - "PENDING"
            factor: 0
    """
    import_offer_validation_config(previous_config_yaml, super_admin)
    import_offer_validation_config(config_yaml, super_admin)

    logger.info("created 2 offer validation config")
