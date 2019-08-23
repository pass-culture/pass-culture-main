from typing import List

from models.provider import Provider


def find_provider_by_id(provider_id: int) -> Provider:
    return Provider.query.filter_by(id=provider_id).first()


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
