import logging

from pcapi import settings


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    logger.info(
        "DEMARCHE_NUMERIQUE_CREATE_UBBLE_MIN_DATETIME = %s", settings.DEMARCHE_NUMERIQUE_CREATE_UBBLE_MIN_DATETIME
    )
