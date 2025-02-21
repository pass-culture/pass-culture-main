import logging

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


if __name__ == "__main__":
    app.app_context().push()
    clean_old_provider_data(_LEGACY_API_PROVIDERS_IDS)
