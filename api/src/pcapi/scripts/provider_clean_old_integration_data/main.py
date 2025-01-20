import logging

import sqlalchemy as sa

from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.flask_app import app
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


def _clean_id_a_provider_for_provider(provider_id: int, batch_size: int = _BATCH_SIZE) -> None:
    while True:
        with transaction():
            offers = (
                offers_models.Offer.query.filter(
                    offers_models.Offer.lastProviderId == provider_id,
                    sa.not_(offers_models.Offer.idAtProvider.is_(None)),
                )
                .limit(batch_size)
                .all()
            )

            if not offers:
                break

            offers_models.Offer.query.filter(offers_models.Offer.id.in_([offer.id for offer in offers])).update(
                {"idAtProvider": None},
                synchronize_session=False,
            )


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
        logger.info("Cleaning offers data for provider %s (id: %s)", provider.name, provider.id)
        _clean_id_a_provider_for_provider(provider_id=provider_id)


if __name__ == "__main__":
    app.app_context().push()
    clean_old_provider_data(_LEGACY_API_PROVIDERS_IDS)
