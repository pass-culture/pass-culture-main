from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin

""" occasion model """
from datetime import datetime
import sqlalchemy as db


class Occasion(PcObject,
               db.Model,
               ProvidableMixin):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    dateCreated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    thingId = db.Column(db.BigInteger,
                        db.ForeignKey("thing.id"),
                        nullable=True)

    thing = db.relationship('Thing',
                            foreign_keys=[thingId],
                            backref='occasions')

    eventId = db.Column(db.BigInteger,
                        db.ForeignKey("event.id"),
                        db.CheckConstraint('("eventId" IS NOT NULL AND "thingId" IS NULL)'
                                           + 'OR ("eventId" IS NULL AND "thingId" IS NOT NULL)',
                                           name='check_occasion_has_thing_xor_event'),
                        nullable=True)

    event = db.relationship('Event',
                            foreign_keys=[eventId],
                            backref='occasions')

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        nullable=True,
                        index=True)

    venue = db.relationship('Venue',
                            foreign_keys=[venueId],
                            backref='occasions')
