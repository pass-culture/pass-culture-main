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

    # FIXME: This is to support legacy code in the webapp
    # it should be removed once all requests from the webapp
    # have an app version header, which will mean that all
    # clients (or at least those who do use the apps) have
    # a recent version of the app
    @hybrid_property
    def offer(self):
        return self.offers

app.model.EventOccurence = EventOccurence
