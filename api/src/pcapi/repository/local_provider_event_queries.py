from datetime import datetime
from datetime import timedelta

import pcapi.core.providers.models as providers_models


def find_latest_sync_part_end_event(provider: providers_models.Provider) -> providers_models.LocalProviderEvent:
    return (
        providers_models.LocalProviderEvent.query.filter(
            (providers_models.LocalProviderEvent.provider == provider)  # type: ignore [operator]
            & (providers_models.LocalProviderEvent.type == providers_models.LocalProviderEventType.SyncPartEnd)
            & (providers_models.LocalProviderEvent.date > datetime.utcnow() - timedelta(days=25))
        )
        .order_by(providers_models.LocalProviderEvent.date.desc())
        .first()
    )
