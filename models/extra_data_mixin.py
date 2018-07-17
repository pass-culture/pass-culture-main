import sqlalchemy as db
from sqlalchemy.dialects.postgresql import JSON


class ExtraDataMixin(object):
    extraData = db.Column(JSON)
