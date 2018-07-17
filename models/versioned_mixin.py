""" versioned mixin """
from sqlalchemy import text
from postgresql_audit.flask import versioning_manager

from models.pc_object import PcObject

class VersionedMixin(object):
    __versioned__ = {}

    def activity(self):
        Activity = versioning_manager.activity_cls
        return Activity.query.filter(text("table_name='"+self.__tablename__
                                          + "' AND cast(changed_data->>'id' AS INT) = " + str(self.id)))\
                             .order_by(PcObject.db.desc(Activity.id))
