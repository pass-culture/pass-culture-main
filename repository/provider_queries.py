from models.provider import Provider


def get_provider_by_local_class(local_class: str) -> Provider:
    return Provider.query \
        .filter_by(localClass=local_class) \
        .first()


def get_enabled_providers_for_pro():
    return Provider \
        .query\
        .filter_by(isActive=True) \
        .filter_by(enabledForPro=True) \
        .order_by(Provider.name) \
        .all()
