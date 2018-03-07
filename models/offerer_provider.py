from flask import current_app as app

db = app.db


class OffererProvider(app.model.PcObject,
                      app.model.ProvidableMixin,
                      db.Model):

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey('offerer.id'),
                          primary_key=True)
    offerer = db.relationship(lambda: app.model.Offerer,
                              back_populates="offererProviders",
                              foreign_keys=[offererId])

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey('provider.id'),
                           primary_key=True)
    provider = db.relationship(lambda: app.model.Provider,
                               back_populates="offererProviders",
                               foreign_keys=[providerId])

    offererIdAtOfferProvider = db.Column(db.String(70),
                                         primary_key=True)


app.model.OffererProvider = OffererProvider
