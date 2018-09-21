""" offerer """
from datetime import datetime
from sqlalchemy import BigInteger, \
    Column, \
    DateTime, \
    Index, \
    String, \
    TEXT, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.offer import Offer
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.user_offerer import UserOfferer
from utils.search import create_tsvector


class Offerer(PcObject,
              HasThumbMixin,
              HasAddressMixin,
              ProvidableMixin,
              NeedsValidationMixin,
              DeactivableMixin,
              Model):
    id = Column(BigInteger, primary_key=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    name = Column(String(140), nullable=False)

    users = relationship('User',
                         secondary='user_offerer')

    siren = Column(String(9), nullable=True,
                   unique=True)  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    iban = Column(
        String(27), 
        nullable=True)

    bic = Column(String(11),
                 CheckConstraint('(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)',
                                 name='check_iban_and_bic_xor_not_iban_and_not_bic'),
                 nullable=True)

    def give_rights(self, user, rights):
        if user:
            user_offerer = UserOfferer()
            user_offerer.offerer = self
            user_offerer.user = user
            user_offerer.rights = rights
            return user_offerer

    def errors(self):
        errors = super(Offerer, self).errors()
        errors.errors.update(HasAddressMixin.errors(self).errors)
        if self.siren is not None \
                and (not len(self.siren) == 9):
            # TODO: or not verify_luhn(self.siren)):
            errors.addError('siren', 'Ce code SIREN est invalide')
        return errors

    @property
    def nOffers(self):
        return Offer.query \
            .filter(Offer.venueId.in_(list(map(lambda v: v.id,
                                               self.managedVenues)))).count()


Offerer.__ts_vector__ = create_tsvector(
    cast(coalesce(Offerer.name, ''), TEXT),
    cast(coalesce(Offerer.address, ''), TEXT),
    cast(coalesce(Offerer.siren, ''), TEXT)
)

Offerer.__table_args__ = (
    Index(
        'idx_offerer_fts',
        Offerer.__ts_vector__,
        postgresql_using='gin'
    ),
)
