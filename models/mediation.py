""" mediation model """
from datetime import datetime
import os
from pathlib import Path
from flask_sqlalchemy import Model
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from models.has_thumb_mixin import HasThumbMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin


class Mediation(PcObject,
                Model,
                HasThumbMixin,
                ProvidableMixin):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    frontText = Column(Text, nullable=True)

    backText = Column(Text, nullable=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    authorId = Column(BigInteger,
                      ForeignKey("user.id"),
                      nullable=True)

    author = relationship('User',
                          foreign_keys=[authorId],
                          backref='mediations')

    offererId = Column(BigInteger,
                       ForeignKey("offerer.id"),
                       nullable=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref='mediations')

    eventId = Column(BigInteger,
                     ForeignKey("event.id"),
                     index=True,
                     nullable=True)

    event = relationship('Event',
                         foreign_keys=[eventId],
                         backref='mediations')

    thingId = Column(BigInteger,
                     ForeignKey("thing.id"),
                     index=True,
                     nullable=True)

    thing = relationship('Thing',
                         foreign_keys=[thingId],
                         backref='mediations')

    tutoIndex = Column(Integer,
                       nullable=True,
                       index=True)


Mediation.__table_args__ = (
    db.CheckConstraint('"thumbCount" <= 2',
                       name='check_mediation_has_max_2_thumbs'),
    db.CheckConstraint('"thumbCount" > 0 OR frontText IS NOT NULL',
                       name='check_mediation_has_thumb_or_text'),
    db.CheckConstraint('"eventId" IS NOT NULL OR thingId IS NOT NULL'
                       + ' OR tutoIndex IS NOT NULL',
                       name='check_mediation_has_event_or_thing_or_tutoIndex'),
)


TUTOS_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / '..'\
                 / 'static' / 'tuto_mediations'


def upsertTutoMediation(index, has_back=False):
    existing_mediation = Mediation.query.filter_by(tutoIndex=index)\
                                        .first()
    mediation = existing_mediation or Mediation()
    mediation.tutoIndex = index
    PcObject.check_and_save(mediation)

    with open(TUTOS_PATH / (str(index) + '.png'), "rb") as f:
        mediation.save_thumb(f.read(),
                             0,
                             no_convert=True,
                             image_type='png')

    if has_back:
        with open(TUTOS_PATH / (str(index) + '_verso.png'), "rb") as f:
            mediation.save_thumb(f.read(),
                                 1,
                                 no_convert=True,
                                 image_type='png')

    PcObject.check_and_save(mediation)


def upsertTutoMediations():
    upsertTutoMediation(0)
    upsertTutoMediation(1, True)
