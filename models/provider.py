from models.deactivable_mixin import DeactivableMixin
from models.pc_object import PcObject
from models.provider import Provider
from models.venue_provider import VenueProvider

""" provider """
from sqlalchemy.dialects.postgresql import CHAR
import sqlalchemy as db



class Provider(PcObject,
               DeactivableMixin,
               db.Model):
    id = db.Column(db.BigInteger,
                   primary_key=True)

    name = db.Column(db.String(60),
                     nullable=False)

    localClass = db.Column(db.String(30),
                           db.CheckConstraint('("localClass" IS NOT NULL AND "apiKey" IS NULL)'
                                              + 'OR ("localClass" IS NULL AND "apiKey" IS NOT NULL)',
                                              name='check_provider_has_localclass_or_apikey'),
                           nullable=True,
                           unique=True)

    venueProviders = db.relationship(VenueProvider,
                                     back_populates="provider",
                                     foreign_keys=[VenueProvider.providerId])

    apiKey = db.Column(CHAR(32),
                       nullable=True)

    apiKeyGenerationDate = db.Column(db.DateTime,
                                     nullable=True)

    def getByClassName(name):
        return Provider.query\
                       .filter_by(localClass=name)\
                       .first()
