from models import Provider


def get_enabled_providers_for_pro():
    return Provider \
        .query\
        .filter_by(isActive=True) \
        .filter_by(enabledForPro=True) \
        .all()
