from flask import current_app as app

db = app.db


class VenueProvider(app.model.PcObject,
                    app.model.ProvidableMixin,
                    app.model.DeactivableMixin,
                    db.Model):

    venueId = db.Column(db.BigInteger,
                        db.ForeignKey('venue.id'),
                        primary_key=True)
    venue = db.relationship(lambda: app.model.Venue,
                            back_populates="venueProviders",
                            foreign_keys=[venueId])

    providerId = db.Column(db.BigInteger,
                           db.ForeignKey('provider.id'),
                           primary_key=True)
    provider = db.relationship(lambda: app.model.Provider,
                               back_populates="venueProviders",
                               foreign_keys=[providerId])

    identifier = db.Column(db.String(70))

    venueIdAtOfferProvider = db.Column(db.String(70),
                                       primary_key=True)

    lastSyncDate = db.Column(db.DateTime,
                             nullable=True)


app.model.VenueProvider = VenueProvider
