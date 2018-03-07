import enum
from flask import current_app as app

db = app.db


class UserMediationOffer(app.model.PcObject, db.Model):
    userMediationId = db.Column(db.BigInteger,
                                db.ForeignKey('user_mediation.id'),
                                primary_key=True)

    userMediation = db.relationship(lambda: app.model.UserMediation,
                                    back_populates="userMediationOffers",
                                    foreign_keys=[userMediationId])

    offerId = db.Column(db.BigInteger,
                        db.ForeignKey('offer.id'),
                        primary_key=True)

    offer = db.relationship(lambda: app.model.Offer,
                            back_populates="userMediationOffers",
                            foreign_keys=[offerId])


app.model.UserMediationOffer = UserMediationOffer
