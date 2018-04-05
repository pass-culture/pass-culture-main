""" mediation model """
from datetime import datetime
from flask import current_app as app
import os
from pathlib import Path
from sqlalchemy import event
from sqlalchemy.orm import mapper
import time


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

    tutoIndex = db.Column(db.Integer,
                          nullable=True)


Mediation.__table_args__ = (
    db.CheckConstraint('"thumbCount" <= 1',
                       name='check_mediation_has_max_1_thumb'),
    db.CheckConstraint('"thumbCount" = 1 OR frontText IS NOT NULL',
                       name='check_mediation_has_thumb_or_text'),
    db.CheckConstraint('"eventId" IS NOT NULL OR thingId IS NOT NULL'
                       + ' OR tutoIndex IS NOT NULL',
                       name='check_mediation_has_event_or_thing_or_tutoIndex'),
)


TUTOS_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / '..'\
                 / 'static' / 'tuto_mediations'


def upsertTutoMediation(index, dominant_color, backText=None):
    existing_mediation = Mediation.query.filter_by(tutoIndex=index)\
                                        .first()
    mediation = existing_mediation or Mediation()
    mediation.tutoIndex = index
    mediation.backText = backText
    app.model.PcObject.check_and_save(mediation)

    with open(TUTOS_PATH / (str(index) + '.svg'), "rb") as f:
        mediation.save_thumb(f.read(),
                             0,
                             image_type='svg',
                             dominant_color=dominant_color)
    app.model.PcObject.check_and_save(mediation)


def upsertTutoMediations():
    upsertTutoMediation(0, b'\xFF\x00\x00')
    upsertTutoMediation(1,
                        b'\xFF\x00\x00',
                        backText="Bien joué ! Pour revenir à l'écran"
                                 + " principal, faites glisser cette"
                                 + " fenềtre vers le bas ou appuyez"
                                 + " sur la croix en haut à droite.")


Mediation.upsertTutoMediations = upsertTutoMediations

app.model.Mediation = Mediation
