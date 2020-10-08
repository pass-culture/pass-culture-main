from sqlalchemy import text

from pcapi.models.db import db, versioning_manager


class VersionedMixin(object):
    __versioned__ = {}

    def activity(self):
        Activity = versioning_manager.activity_cls
        return Activity.query.filter(
            text("table_name='" + self.__tablename__
                 + "' AND cast(old_data->>'id' AS INT) = "
                 + str(self.id))) \
            .order_by(db.desc(Activity.id))
