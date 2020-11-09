from typing import List
from typing import Optional

from pcapi.models.provider import Provider


def get_provider_enabled_for_pro_by_id(provider_id: int) -> Optional[Provider]:
    return Provider.query \
        .filter_by(id=provider_id) \
        .filter_by(isActive=True) \
        .filter_by(enabledForPro=True) \
        .first()


def get_provider_by_local_class(local_class: str) -> Provider:
    return Provider.query \
        .filter_by(localClass=local_class) \
        .first()


def get_enabled_providers_for_pro() -> List[Provider]:
    return Provider \
        .query \
        .filter_by(isActive=True) \
        .filter_by(enabledForPro=True) \
        .order_by(Provider.name) \
        .all()


def get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class: str) -> List[Provider]:
    return Provider.query \
        .filter_by(isActive=True) \
        .filter_by(enabledForPro=True) \
        .filter(Provider.localClass != allocine_local_class) \
        .order_by(Provider.name) \
        .all()
