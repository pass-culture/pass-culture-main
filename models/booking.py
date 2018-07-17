""" booking model """
from datetime import datetime
from flask_sqlalchemy import Model
from sqlalchemy import BigInteger,\
                      Column,\
                      DateTime,\
                      DDL,\
                      event,\
                      ForeignKey,\
                      Integer,\
                      String
from sqlalchemy.orm import relationship

from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.versioned_mixin import VersionedMixin

class Booking(PcObject,
              Model,
              DeactivableMixin,
              VersionedMixin):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    dateModified = Column(DateTime,
                          nullable=False,
                          default=datetime.utcnow)

    recommendationId = Column(BigInteger,
                              ForeignKey("recommendation.id"))

    recommendation = relationship('Recommendation',
                                  foreign_keys=[recommendationId],
                                  backref='bookings')

    offerId = Column(BigInteger,
                     ForeignKey("offer.id"),
                     index=True,
                     nullable=True)

    offer = relationship('Offer',
                         foreign_keys=[offerId],
                         backref='bookings')

    quantity = Column(Integer,
                      nullable=False,
                      default=1)

    @property
    def eventOccurenceBeginningDatetime(self):
        offer = self.offer
        if offer.thingId:
            return None
        return offer.eventOccurence.beginningDatetime

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    index=True,
                    nullable=False)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='userBookings')
