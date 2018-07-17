""" occasion model """
from datetime import datetime, timedelta
from flask import current_app as app
from sqlalchemy import event, DDL
from sqlalchemy.ext.hybrid import hybrid_property

db = app.db


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

    thing = db.relationship(lambda: Thing,
                            foreign_keys=[thingId],
                            backref='occasions')

    eventId = db.Column(db.BigInteger,
                        db.ForeignKey("event.id"),
                        db.CheckConstraint('("eventId" IS NOT NULL AND "thingId" IS NULL)'
                                           + 'OR ("eventId" IS NULL AND "thingId" IS NOT NULL)',
                                           name='check_occasion_has_thing_xor_event'),
                        nullable=True)

    event = db.relationship(lambda: Event,
                            foreign_keys=[eventId],
                            backref='occasions')

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        nullable=True,
                        index=True)

    venue = db.relationship(lambda: Venue,
                            foreign_keys=[venueId],
                            backref='occasions')

Occasion = Occasion
