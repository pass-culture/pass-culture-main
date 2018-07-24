""" venue """
from sqlalchemy.event import listens_for
from sqlalchemy import BigInteger,\
                       Column,\
                       ForeignKey,\
                       Index,\
                       Numeric,\
                       String,\
                       TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from models.db import Model
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.occasion import Occasion
from models.offerer import Offerer
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from utils.search import create_tsvector


class Venue(PcObject,
            HasThumbMixin,
            HasAddressMixin,
            ProvidableMixin,
            Model):

    id = Column(BigInteger, primary_key=True)

    name = Column(String(140), nullable=False)

    siret = Column(String(14), nullable=True, unique=True)

    departementCode = Column(String(3), nullable=False, index=True)

    latitude = Column(Numeric(8, 5), nullable=True)

    longitude = Column(Numeric(8, 5), nullable=True)

    venueProviders = relationship('VenueProvider',
                                  back_populates="venue")

    managingOffererId = Column(BigInteger,
                               ForeignKey("offerer.id"),
                               nullable=False,
                               index=True)

    managingOfferer = relationship('Offerer',
                                   foreign_keys=[managingOffererId],
                                   backref='managedVenues')

    bookingEmail = Column(String(120), nullable=False)

    #openingHours = Column(ARRAY(TIME))
    # Ex: [['09:00', '18:00'], ['09:00', '19:00'], null,  ['09:00', '18:00']]
    # means open monday 9 to 18 and tuesday 9 to 19, closed wednesday,
    # open thursday 9 to 18, closed the rest of the week

    def store_department_code(self):
        self.departementCode = self.postalCode[:-3]

    def errors(self):
        errors = super(Venue, self).errors()
        if self.siret is not None\
           and not len(self.siret) == 14:
            errors.addError('siret', 'Ce code SIRET est invalide : '+self.siret)
        if self.managingOffererId is not None:
            if self.managingOfferer is None:
                managingOfferer = Offerer.query\
                                      .filter_by(id=self.managingOffererId).first()
            else:
                managingOfferer = self.managingOfferer
            if self.siret is not None\
               and managingOfferer is not None\
               and not self.siret.startswith(managingOfferer.siren):
                errors.addError('siret', 'Le code SIRET doit correspondre à un établissement de votre structure')
        return errors

    @property
    def nOccasions(self):
        return Occasion.query.filter_by(venue=self).count()

@listens_for(Venue, 'before_insert')
def before_insert(mapper, connect, self):
    self.store_department_code()


@listens_for(Venue, 'before_update')
def before_update(mapper, connect, self):
    self.store_department_code()

Venue.__ts_vector__ = create_tsvector(
    cast(coalesce(Venue.name, ''), TEXT),
    cast(coalesce(Venue.address, ''), TEXT),
    cast(coalesce(Venue.siret, ''), TEXT)
)


Venue.__table_args__ = (
    Index(
        'idx_venue_fts',
        Venue.__ts_vector__,
        postgresql_using='gin'
    ),
)
