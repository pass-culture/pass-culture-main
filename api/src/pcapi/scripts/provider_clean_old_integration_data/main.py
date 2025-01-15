import logging

from sqlalchemy import text

from pcapi import settings
from pcapi.core.providers import models as providers_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)

_LEGACY_API_PROVIDERS_IDS = [
    15,  # TiteLive Stocks (Epagine / Place des libraires.com)
    59,  # Praxiel/Inférence
    58,  # FNAC
    23,  # www.leslibraires.fr
    66,  # Decitre
    63,  # Librisoft
    68,  # TMIC-Ellipses
    65,  # Mollat
    67,  # CDI-Bookshop
]

_BATCH_SIZE = 1000


def _clean_id_at_providers(provider_ids: list[int], batch_size: int = _BATCH_SIZE) -> None:
    # Disabling statement_timeout as we can't know in advance how long it would take
    db.session.execute(text("SET statement_timeout = '300s';"))

    # create procedure
    db.session.execute(
        text(
            """
            CREATE OR REPLACE PROCEDURE update_deprecated_provider_offer_batch(provider_id_list INT[], batch_size INT)
            LANGUAGE plpgsql
            AS $$
            BEGIN
                LOOP
                    -- Begin a new transaction
                    BEGIN
                        WITH batch AS (
                            SELECT "id"
                            FROM offer
                            WHERE "lastProviderId" = ANY (provider_id_list)
                            AND "idAtProvider" IS NOT NULL
                            LIMIT batch_size
                        )

                        UPDATE offer SET "idAtProvider" = NULL WHERE "id" IN (SELECT "id" FROM batch);

                        -- Exit the loop if no rows were updated
                        EXIT WHEN NOT FOUND;
                    EXCEPTION
                        -- Rollback the transaction in case of any error
                        WHEN OTHERS THEN
                            ROLLBACK;
                            -- Optionally, you can raise an exception to stop the procedure
                            RAISE;
                    END;
                END LOOP;
            END $$;
            """
        )
    )

    db.session.execute(
        text("""CALL update_deprecated_provider_offer_batch(:provider_id_list, :batch_size);"""),
        params={"provider_id_list": provider_ids, "batch_size": batch_size},
    )

    # delete procedure
    db.session.execute(text("""DROP PROCEDURE IF EXISTS update_deprecated_provider_offer_batch;"""))

    # According to PostgreSQL, setting such values this way is affecting only the current session
    # but let's be defensive by setting back to the original values
    db.session.execute(text(f"SET statement_timeout = {settings.DATABASE_STATEMENT_TIMEOUT}"))


def clean_old_provider_data(provider_ids: list[int]) -> None:
    # Update providers
    for provider_id in provider_ids:
        with transaction():
            provider = providers_models.Provider.query.get(provider_id)

            logger.info("Cleaning data for provider %s (id: %s)", provider.name, provider.id)

            if "[DÉPRÉCIÉ]" not in provider.name:
                provider.name = f"[DÉPRÉCIÉ] {provider.name}"
            provider.enabledForPro = False
            provider.isActive = False

    # Update providers offers
    _clean_id_at_providers(provider_ids)


if __name__ == "__main__":
    app.app_context().push()
    clean_old_provider_data(_LEGACY_API_PROVIDERS_IDS)
