from models.soft_deletable_mixin import SoftDeletableMixin


def _soft_delete(obj: SoftDeletableMixin):
    obj.isSoftDeleted = True
    return obj
