from postgresql_audit.flask import versioning_manager
from sqlalchemy import text

from models.db import db


class VersionedMixin(object):
    __versioned__ = {}

    def activity(self):
        Activity = versioning_manager.activity_cls
        return Activity.query.filter(
            text("table_name='" + self.__tablename__ + "' AND cast(old_data->>'id' AS INT) = " + str(self.id))) \
            .order_by(db.desc(Activity.id))
