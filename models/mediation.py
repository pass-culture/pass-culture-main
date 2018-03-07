""" mediation model """
from datetime import datetime
from flask import current_app as app

db = app.db


class Mediation(app.model.PcObject,
                db.Model,
                app.model.HasThumbMixin,
                app.model.ProvidableMixin
                ):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    frontText = db.Column(db.Text, nullable=True)

    backText = db.Column(db.Text, nullable=True)

    dateCreated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.now)

    authorId = db.Column(db.BigInteger,
                         db.ForeignKey("user.id"),
                         nullable=True)

    author = db.relationship(lambda: app.model.User,
                             foreign_keys=[authorId],
                             backref='mediations')

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey("offerer.id"),
                          nullable=True)

    offerer = db.relationship(lambda: app.model.Offerer,
                              foreign_keys=[offererId],
                              backref='mediations')

    eventId = db.Column(db.BigInteger,
                        db.ForeignKey("event.id"),
                        nullable=True)

    event = db.relationship(lambda: app.model.Event,
                            foreign_keys=[eventId],
                            backref='mediations')

    thingId = db.Column(db.BigInteger,
                        db.ForeignKey("thing.id"),
                        nullable=True)

    thing = db.relationship(lambda: app.model.Thing,
                            foreign_keys=[thingId],
                            backref='mediations')


Mediation.__table_args__ = (
    db.CheckConstraint('"thumbCount" <= 1',
                       name='check_mediation_has_max_1_thumb'),
    db.CheckConstraint('"thumbCount" = 1 OR frontText IS NOT NULL',
                       name='check_mediation_has_thumb_or_text'),
)

app.model.Mediation = Mediation
