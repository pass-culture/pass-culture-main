import datetime
import logging

from pcapi.connectors.titelive import TiteliveBase
import pcapi.core.providers.constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


def main() -> None:
    from pcapi.flask_app import app

    with app.app_context():
        titelive_provider = providers_repository.get_provider_by_name(
            providers_constants.TITELIVE_EPAGINE_PROVIDER_NAME
        )
        titelive_base = TiteliveBase.BOOK

        with transaction():
            sync_end_event = providers_models.LocalProviderEvent(
                date=datetime.datetime(2024, 6, 10),
                payload=titelive_base.value,
                provider=titelive_provider,
                type=providers_models.LocalProviderEventType.SyncEnd,
            )
            db.session.add(sync_end_event)
            db.session.flush()


if __name__ == "__main__":
    main()
