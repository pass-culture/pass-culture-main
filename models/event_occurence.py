""" event occurence """
from flask import current_app as app
from sqlalchemy.ext.hybrid import hybrid_property

db = app.db


class EventOccurence(app.model.PcObject,
                     db.Model,
                     app.model.DeactivableMixin,
                     app.model.ProvidableMixin
                    ):
    id = db.Column(db.BigInteger,
                   primary_key=True)

    type = db.Column(db.Enum(app.model.EventType),
                     nullable=True)

    eventId = db.Column(db.BigInteger,
                        db.ForeignKey("event.id"),
                        nullable=False)

    event = db.relationship(lambda: app.model.Event,
                            foreign_keys=[eventId],
                            backref='occurences')

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey("venue.id"),
                        nullable=True)

    venue = db.relationship(lambda: app.model.Venue,
                            foreign_keys=[venueId],
                            backref='eventOccurences')

    beginningDatetime = db.Column(db.DateTime,
                                  nullable=False)

    accessibility = db.Column(db.Binary(1),
                              nullable=False,
                              default=bytes([0]))


app.model.EventOccurence = EventOccurence
