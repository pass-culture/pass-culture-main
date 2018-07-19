""" recommendation model """
from datetime import datetime
from sqlalchemy.sql import expression
from sqlalchemy import BigInteger,\
                       Boolean,\
                       CheckConstraint,\
                       Column,\
                       DateTime,\
                       ForeignKey,\
                       String
from sqlalchemy.orm import relationship

from models import Offer, EventOccurence
from models.db import Model
from models.pc_object import PcObject


class Recommendation(PcObject, Model):

    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    nullable=False,
                    index=True)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref='recommendations')

    mediationId = Column(BigInteger,
                         ForeignKey('mediation.id'),
                         index=True,
                         nullable=True) # NULL for recommendation created directly from a thing or an event

    mediation = relationship('Mediation',
                                foreign_keys=[mediationId],
                                backref='recommendations')

    thingId = Column(BigInteger,
                        ForeignKey('thing.id'),
                        index=True,
                        nullable=True) # NULL for recommendation created from a mediation or an event

    thing = relationship('Thing',
                            foreign_keys=[thingId],
                            backref='recommendations')

    eventId = Column(BigInteger,
                        ForeignKey('event.id'),
                        CheckConstraint('("thingId" IS NOT NULL AND "eventId" IS NULL)'
                                           + 'OR ("thingId" IS NULL AND "eventId" IS NOT NULL)'
                                           + 'OR ("thingId" IS NULL AND "eventId" IS NULL)',
                                           name='check_reco_has_thingid_xor_eventid_xor_nothing'),
                        index=True,
                        nullable=True) # NULL for recommendation created a mediation or an offer

    event = relationship('Event',
                            foreign_keys=[eventId],
                            backref='recommendations')

    shareMedium = Column(String(20),
                            nullable=True)

    inviteforEventOccurenceId = Column(BigInteger,
                                          ForeignKey('event_occurence.id'),
                                          nullable=True)

    inviteforEventOccurence = relationship('EventOccurence',
                                              foreign_keys=[inviteforEventOccurenceId],
                                              backref='inviteRecommendations')

    dateCreated = Column(DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    dateUpdated = Column(DateTime,
                            nullable=False,
                            default=datetime.utcnow)

    dateRead = Column(DateTime,
                         nullable=True,
                         index=True)

    validUntilDate = Column(DateTime,
                               nullable=True,
                               index=True)

    isClicked = Column(Boolean,
                          nullable=False,
                          server_default=expression.false(),
                          default=False)

    isFavorite = Column(Boolean,
                           nullable=False,
                           server_default=expression.false(),
                           default=False)

    isFirst = Column(Boolean,
                        nullable=False,
                        server_default=expression.false(),
                        default=False)

    @property
    def mediatedOffers(self, as_query=False):
        "Returns the offers that correspond to this recommendation\
         if there is a mediation, only offers from the author of the\
         mediation are considered (offerers don't want to advertise\
         for each other)."
        return self.mediatedOffersQuery.all()

    @property
    def mediatedOffersQuery(self):
        query = Offer.query
        reco_or_mediation = self
        if self.mediation is not None:
            reco_or_mediation = self.mediation
            query = query.filter_by(offererId=self.mediation.offererId)
        if self.thingId is not None:
            query = query.filter_by(thingId=reco_or_mediation.thingId)
        elif self.eventId is not None:
            query = query.join(EventOccurence)\
                         .filter(EventOccurence.eventId == reco_or_mediation.eventId)
        return query
        
    # FIXME: This is to support legacy code in the webapp
    # it should be removed once all requests from the webapp
    # have an app version header, which will mean that all
    # clients (or at least those who do use the app) have
    # a recent version of the app

    @property
    def mediatedOccurences(self):
        occurences = []
        if self.mediationId is None:
            if self.event is None:
                return None
            else:
                occurences = self.event.occurences
        else:
            if self.mediation.event is None:
                return None
            else:
                occurences = self.mediation.event.occurences
        return sorted(occurences,
                      key=lambda o: o.beginningDatetime,
                      reverse=True)
