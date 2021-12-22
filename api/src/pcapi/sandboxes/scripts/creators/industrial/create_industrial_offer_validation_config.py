import logging

from pcapi.core.offers.api import import_offer_validation_config
from pcapi.core.users.repository import find_user_by_email


logger = logging.getLogger(__name__)


def create_industrial_offer_validation_config() -> None:
    logger.info("create_industrial_offer_validation_config")
    super_admin = find_user_by_email("pctest.admin93.0@example.com")
    previous_config_yaml = """
    minimum_score: 0.6
    rules:
        - name: "Check offer name"
          factor: 0
          conditions:
              - model: "Offer"
                attribute: "name"
                condition:
                    operator: "not in"
                    comparated:
                        - "REJECTED"
                        - "PENDING"
                        - "DRAFT"
        - name: "Check max price"
          factor: 0.7
          conditions:
              - model: "Offer"
                attribute: "max_price"
                condition:
                    operator: ">"
                    comparated: 100
    """
    config_yaml = """
    minimum_score: 0.6
    rules:
        - name: "Check offer name"
          factor: 0
          conditions:
              - model: "Offer"
                attribute: "name"
                condition:
                    operator: "contains"
                    comparated:
                        - "REJECTED"
                        - "PENDING"
    """
    import_offer_validation_config(previous_config_yaml, super_admin)
    import_offer_validation_config(config_yaml, super_admin)

    logger.info("created 2 offer validation config")
