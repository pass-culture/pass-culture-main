from datetime import datetime

from sqlalchemy import TEXT, BigInteger, Boolean, CheckConstraint, Column, \
    DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.event import listens_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from domain.keywords import create_ts_vector_and_table_args
from domain.postal_code.postal_code import PostalCode
from models.venue_type import VenueType
from models.bank_information import BankInformationStatus
from models.db import Model
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.offer_sql_entity import OfferSQLEntity
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.versioned_mixin import VersionedMixin

CONSTRAINT_CHECK_IS_VIRTUAL_XOR_HAS_ADDRESS = """
(
    "isVirtual" IS TRUE
    AND (address IS NULL AND "postalCode" IS NULL AND city IS NULL AND "departementCode" IS NULL)
)
OR
(
    "isVirtual" IS FALSE
    AND siret is NOT NULL
    AND ("postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
)
OR
(
    "isVirtual" IS FALSE
    AND (siret is NULL and comment is NOT NULL)
    AND (address IS NOT NULL AND "postalCode" IS NOT NULL AND city IS NOT NULL AND "departementCode" IS NOT NULL)
)

"""

CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL = """
    (siret IS NULL AND comment IS NULL AND "isVirtual" IS TRUE)
    OR (siret IS NULL AND comment IS NOT NULL AND "isVirtual" IS FALSE)
    OR (siret IS NOT NULL AND "isVirtual" IS FALSE)
"""


class VenueSQLEntity(PcObject,
                     Model,
                     HasThumbMixin,
                     HasAddressMixin,
                     ProvidableMixin,
                     VersionedMixin,
                     NeedsValidationMixin):
    __tablename__ = 'venue'

    id = Column(BigInteger, primary_key=True)

    name = Column(String(140), nullable=False)

    siret = Column(String(14), nullable=True, unique=True)

    departementCode = Column(String(3), nullable=True)

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

    bookingEmail = Column(String(120), nullable=True)

    postalCode = Column(String(6), nullable=True)

    city = Column(String(50), nullable=True)

    publicName = Column(String(255), nullable=True)

    isVirtual = Column(
        Boolean,
        CheckConstraint(CONSTRAINT_CHECK_IS_VIRTUAL_XOR_HAS_ADDRESS, name='check_is_virtual_xor_has_address'),
        nullable=False,
        default=False
    )

    comment = Column(
        TEXT,
        CheckConstraint(
            CONSTRAINT_CHECK_HAS_SIRET_XOR_HAS_COMMENT_XOR_IS_VIRTUAL,
            name='check_has_siret_xor_comment_xor_isVirtual'
        ),
        nullable=True
    )

    venueTypeId = Column(Integer,
                         ForeignKey('venue_type.id'),
                         nullable=True)

    venueLabelId = Column(Integer,
                          ForeignKey('venue_label.id'),
                          nullable=True)

    dateCreated = Column(DateTime,
                         nullable=True,
                         default=datetime.utcnow)

    def store_departement_code(self):
        self.departementCode = PostalCode(self.postalCode).get_departement_code()

    @property
    def bic(self):
        return self.bankInformation.bic if self.bankInformation else None

    @property
    def iban(self):
        return self.bankInformation.iban if self.bankInformation else None

    @property
    def demarchesSimplifieesApplicationId(self):
        if not self.bankInformation:
            return None

        can_show_application_id = self.bankInformation.status == BankInformationStatus.DRAFT or self.bankInformation.status == BankInformationStatus.ACCEPTED
        if not can_show_application_id:
            return None

        return self.bankInformation.applicationId

    @property
    def nOffers(self):
        return OfferSQLEntity.query.filter(OfferSQLEntity.venueId == self.id).with_entities(OfferSQLEntity.id).count()


@listens_for(VenueSQLEntity, 'before_insert')
def before_insert(mapper, connect, self):
    _fill_departement_code_from_postal_code(self)


@listens_for(VenueSQLEntity, 'before_update')
def before_update(mapper, connect, self):
    _fill_departement_code_from_postal_code(self)


def _fill_departement_code_from_postal_code(self):
    if not self.isVirtual:
        if not self.postalCode:
            raise IntegrityError(None, None, None)
        self.store_departement_code()


def create_digital_venue(offerer):
    digital_venue = VenueSQLEntity()
    digital_venue.isVirtual = True
    digital_venue.name = "Offre numérique"
    digital_venue.venueTypeId = _get_digital_venue_type_id()
    digital_venue.managingOfferer = offerer
    return digital_venue

def _get_digital_venue_type_id() -> int:
    return VenueType.query.filter_by(label="Offre numérique").first().id

ts_indexes = [('idx_venue_fts_name', VenueSQLEntity.name),
              ('idx_venue_fts_publicName', VenueSQLEntity.publicName,),
              ('idx_venue_fts_address', VenueSQLEntity.address),
              ('idx_venue_fts_siret', VenueSQLEntity.siret),
              ('idx_venue_fts_city', VenueSQLEntity.city)]

(VenueSQLEntity.__ts_vectors__, VenueSQLEntity.__table_args__) = create_ts_vector_and_table_args(ts_indexes)
