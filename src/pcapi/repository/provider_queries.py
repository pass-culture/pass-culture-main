from operator import or_
from typing import Optional

from pcapi.core.providers.provider import Provider


def get_provider_enabled_for_pro_by_id(provider_id: int) -> Optional[Provider]:
    return Provider.query.filter_by(id=provider_id).filter_by(isActive=True).filter_by(enabledForPro=True).first()


def get_provider_by_local_class(local_class: str) -> Provider:
    return Provider.query.filter_by(localClass=local_class).first()


def get_enabled_providers_for_pro() -> list[Provider]:
    return Provider.query.filter_by(isActive=True).filter_by(enabledForPro=True).order_by(Provider.name).all()


def get_providers_enabled_for_pro_excluding_specific_provider(allocine_local_class: str) -> list[Provider]:
    return (
        Provider.query.filter_by(isActive=True)
        .filter_by(enabledForPro=True)
        .filter(or_(Provider.localClass != allocine_local_class, Provider.localClass.is_(None)))
        .order_by(Provider.name)
        .all()
    )
