""" provider_event model """
import enum
from datetime import datetime
from flask import current_app as app

db = app.db


class LocalProviderEventType(enum.Enum):
    SyncError = "SyncError"

    SyncPartStart = "SyncPartStart"
    SyncPartEnd = "SyncPartEnd"

    SyncStart = "SyncStart"
    SyncEnd = "SyncEnd"


app.model.LocalProviderEventType = LocalProviderEventType


class LocalProviderEvent(app.model.PcObject,
                         db.Model):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey("provider.id"),
                           nullable=False)
    provider = db.relationship(lambda: app.model.Provider,
                               foreign_keys=[providerId])

    date = db.Column(db.DateTime,
                     nullable=False,
                     default=datetime.now)

    type = db.Column(db.Enum(app.model.LocalProviderEventType),
                     nullable=False)

    payload = db.Column(db.String(50),
                        nullable=True)


app.model.LocalProviderEvent = LocalProviderEvent
