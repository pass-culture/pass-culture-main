""" user_mediation model """
from datetime import datetime
from flask import current_app as app

db = app.db


class UserMediation(app.model.PcObject, db.Model):

    id = db.Column(db.BigInteger,
                   primary_key=True,
                   autoincrement=True)

    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       nullable=False)

    user = db.relationship(lambda: app.model.User,
                           foreign_keys=[userId],
                           backref='userMediations')

    userMediationOffers = db.relationship(lambda: app.model.UserMediationOffer,
                                          back_populates="userMediation")

    mediationId = db.Column(db.BigInteger,
                            db.ForeignKey('mediation.id'),
                            nullable=True)

    mediation = db.relationship(lambda: app.model.Mediation,
                                foreign_keys=[mediationId],
                                backref='userMediations')

    sharedByUserId = db.Column(db.BigInteger,
                               db.ForeignKey('user.id'),
                               nullable=True)

    sharedByUser = db.relationship(lambda: app.model.User,
                                   foreign_keys=[sharedByUserId],
                                   backref='sharedUserMediations')

    shareMedium = db.Column(db.String(20),
                            nullable=True)

    inviteforEventOccurenceId = db.Column(db.BigInteger,
                                          db.ForeignKey('event_occurence.id'),
                                          nullable=True)

    inviteforEventOccurence = db.relationship(lambda: app.model.EventOccurence,
                                              foreign_keys=[inviteforEventOccurenceId],
                                              backref='inviteUserMediations')

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



app.model.UserMediation = UserMediation
