from flask import current_app as app
from sqlalchemy.dialects.postgresql import JSON

db = app.db


class ExtraDataMixin(object):
    extraData = db.Column(JSON)


app.model.ExtraDataMixin = ExtraDataMixin
