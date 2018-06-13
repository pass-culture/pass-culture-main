from flask import current_app as app

db = app.db


class VenueProvider(app.model.PcObject,
                    app.model.ProvidableMixin,
                    app.model.DeactivableMixin,
                    db.Model):

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey('venue.id'),
                        nullable=False)
    venue = db.relationship(lambda: app.model.Venue,
                            back_populates="venueProviders",
                            foreign_keys=[venueId])

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey('provider.id'),
                           nullable=False)
    provider = db.relationship(lambda: app.model.Provider,
                               back_populates="venueProviders",
                               foreign_keys=[providerId])

    venueIdAtOfferProvider = db.Column(db.String(70))

    lastSyncDate = db.Column(db.DateTime,
                             nullable=True)


app.model.VenueProvider = VenueProvider
