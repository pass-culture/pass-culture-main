""" offer model """
from datetime import datetime
from flask import current_app as app
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from utils.search import create_tsvector

db = app.db


class Offer(app.model.PcObject,
            db.Model,
            app.model.DeactivableMixin,
            app.model.ProvidableMixin
            ):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    # an offer is either linked to a thing or to an eventOccurence

    dateModified = db.Column(db.DateTime,
                             nullable=False,
                             default=datetime.now)

    userMediationOffers = db.relationship(lambda: app.model.UserMediationOffer,
                                          back_populates="offer")

    eventOccurenceId = db.Column(db.BigInteger,
                                 db.ForeignKey("event_occurence.id"),
                                 db.CheckConstraint('"eventOccurenceId" IS NOT NULL OR "thingId" IS NOT NULL',
                                                    name='check_offer_has_event_occurence_or_thing'),
                                 nullable=True)

    eventOccurence = db.relationship(lambda: app.model.EventOccurence,
                                     foreign_keys=[eventOccurenceId])

    thingId = db.Column(db.BigInteger,
                        db.ForeignKey("thing.id"),
                        nullable=True)

    thing = db.relationship(lambda: app.model.Thing,
                            foreign_keys=[thingId])

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        db.CheckConstraint('("venueId" IS NOT NULL AND "eventOccurenceId" IS NULL)'
                                           + 'OR ("venueId" IS NULL AND "eventOccurenceId" IS NOT NULL)',
                                           name='check_offer_has_venue_xor_event_occurence'),
                        nullable=True)

    venue = db.relationship(lambda: app.model.Venue,
                            foreign_keys=[venueId],
                            backref='offers')

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey("offerer.id"),
                          nullable=True)

    offerer = db.relationship(lambda: app.model.Offerer,
                              foreign_keys=[offererId],
                              backref='offers')

    price = db.Column(db.Numeric(10, 2),
                      nullable=False)

    available = db.Column(db.Integer,
                          nullable=True)

    groupSize = db.Column(db.Integer,
                          nullable=False,
                          default=1)

    @hybrid_property
    def object(self):
        return self.thing or self.eventOccurence




app.model.Offer = Offer
