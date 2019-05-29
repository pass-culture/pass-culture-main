from datetime import datetime

from models.soft_deletable_mixin import SoftDeletableMixin


def soft_delete_objects(*objects):
    return list(map(_soft_delete, objects))


def invalidate_recommendations_if_deactivating_object(data, recommendations):
    if 'isActive' in data and not data['isActive']:
        for recommendation in recommendations:
            recommendation.validUntilDate = datetime.utcnow()


def _soft_delete(obj: SoftDeletableMixin):
    obj.isSoftDeleted = True
    return obj
