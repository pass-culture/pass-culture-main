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


LocalProviderEventType = LocalProviderEventType


class LocalProviderEvent(PcObject,
                         db.Model):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey("provider.id"),
                           nullable=False)
    provider = db.relationship(lambda: Provider,
                               foreign_keys=[providerId])

    date = db.Column(db.DateTime,
                     nullable=False,
                     default=datetime.utcnow)

    type = db.Column(db.Enum(LocalProviderEventType),
                     nullable=False)

    payload = db.Column(db.String(50),
                        nullable=True)


LocalProviderEvent = LocalProviderEvent
