""" recommendation model """
from datetime import datetime
from flask import current_app as app

db = app.db


class Recommendation(app.model.PcObject, db.Model):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       nullable=False)

    user = db.relationship(lambda: app.model.User,
                           foreign_keys=[userId],
                           backref='recommendations')

    recommendationBookings = db.relationship(lambda: app.model.RecommendationBooking,
                                             back_populates="recommendation")

    # FIXME: Replace this with offerId (single offer)
    # + constraint ? (offerId XOR mediationId ?)
    recommendationOffers = db.relationship(lambda: app.model.RecommendationOffer,
                                           back_populates="recommendation")

    mediationId = db.Column(db.BigInteger,
                            db.ForeignKey('mediation.id'),
                            nullable=True) # NULL for recommendation created directly from an offer

    mediation = db.relationship(lambda: app.model.Mediation,
                                foreign_keys=[mediationId],
                                backref='recommendations')

    sharedByUserId = db.Column(db.BigInteger,
                               db.ForeignKey('user.id'),
                               nullable=True)

    sharedByUser = db.relationship(lambda: app.model.User,
                                   foreign_keys=[sharedByUserId],
                                   backref='sharedRecommendations')

    shareMedium = db.Column(db.String(20),
                            nullable=True)

    inviteforEventOccurenceId = db.Column(db.BigInteger,
                                          db.ForeignKey('event_occurence.id'),
                                          nullable=True)

    inviteforEventOccurence = db.relationship(lambda: app.model.EventOccurence,
                                              foreign_keys=[inviteforEventOccurenceId],
                                              backref='inviteRecommendations')

    dateCreated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.now)

    dateUpdated = db.Column(db.DateTime,
                            nullable=False,
                            default=datetime.now)

    dateRead = db.Column(db.DateTime,
                         nullable=True)

    validUntilDate = db.Column(db.DateTime,
                               nullable=False)

    isClicked = db.Column(db.Boolean,
                          nullable=False,
                          default=False)

    isFavorite = db.Column(db.Boolean,
                           nullable=False,
                           default=False)

    isFirst = db.Column(db.Boolean,
                        nullable=False,
                        default=False)


    @property
    def mediatedOccurences(self):
        #FIXME: try to turn this into a join
        if self.mediationId is None:
            if self.recommendationOffers[0].eventOccurenceId is None:
                return None
            else:
                return self.recommendationOffers[0].eventOccurence.event.occurences
        else:
            if self.mediation.event is None:
                return None
            else:
                return self.mediation.event.occurences


app.model.Recommendation = Recommendation
