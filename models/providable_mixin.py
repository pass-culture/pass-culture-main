from datetime import datetime
from flask import current_app as app
from sqlalchemy.ext.declarative import declared_attr

db = app.db


class ProvidableMixin(app.model.VersionedMixin):

    @declared_attr
    def lastProviderId(cls):
        return db.Column(db.BigInteger,
                         db.ForeignKey("provider.id"),
                         nullable=True)

    @declared_attr
    def lastProvider(cls):
        return db.relationship(lambda: app.model.Provider,
                               foreign_keys=[cls.lastProviderId])

    idAtProviders = db.Column(db.String(70),
                              db.CheckConstraint('"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
                                                 name='check_providable_with_provider_has_idatproviders'),
                              nullable=True,
                              unique=True)

    dateModifiedAtLastProvider = db.Column(db.DateTime,
                                           nullable=True,
                                           default=datetime.now)


app.model.ProvidableMixin = ProvidableMixin
