from flask import current_app as app

db = app.db


class RecommendationOffer(app.model.PcObject, db.Model):
    recommendationId = db.Column(db.BigInteger,
                                 db.ForeignKey('recommendation.id'),
                                 primary_key=True)

    recommendation = db.relationship(lambda: app.model.Recommendation,
                                     back_populates="recommendationOffers",
                                     foreign_keys=[recommendationId])

    offerId = db.Column(db.BigInteger,
                        db.ForeignKey('offer.id'),
                        primary_key=True)

    offer = db.relationship(lambda: app.model.Offer,
                            back_populates="recommendationOffers",
                            foreign_keys=[offerId])


app.model.RecommendationOffer = RecommendationOffer
