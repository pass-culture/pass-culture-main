from models.pc_object import PcObject

""" provider_event model """
import enum
from datetime import datetime
import sqlalchemy as db


class LocalProviderEventType(enum.Enum):
    SyncError = "SyncError"

    SyncPartStart = "SyncPartStart"
    SyncPartEnd = "SyncPartEnd"

    SyncStart = "SyncStart"
    SyncEnd = "SyncEnd"


class LocalProviderEvent(PcObject,
                         db.Model):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey("provider.id"),
                           nullable=False)
    provider = db.relationship('Provider',
                               foreign_keys=[providerId])

    date = db.Column(db.DateTime,
                     nullable=False,
                     default=datetime.utcnow)

    type = db.Column(db.Enum(LocalProviderEventType),
                     nullable=False)

    payload = db.Column(db.String(50),
                        nullable=True)

