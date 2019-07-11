""" offerer """
from datetime import datetime

from sqlalchemy import BigInteger, \
    Column, \
    DateTime, \
    Index, \
    String, \
    TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import coalesce

from domain.keywords import create_ts_vector_and_table_args
from models.db import Model
from models.deactivable_mixin import DeactivableMixin
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.pc_object import PcObject
from models.providable_mixin import ProvidableMixin
from models.user_offerer import UserOfferer
from models.versioned_mixin import VersionedMixin


class Offerer(PcObject,
              Model,
              HasThumbMixin,
              HasAddressMixin,
              ProvidableMixin,
              NeedsValidationMixin,
              DeactivableMixin,
              VersionedMixin):
    id = Column(BigInteger, primary_key=True)

    dateCreated = Column(DateTime,
                         nullable=False,
                         default=datetime.utcnow)

    name = Column(String(140), nullable=False)

    users = relationship('User',
                         secondary='user_offerer')

    siren = Column(String(9), nullable=True,
                   unique=True)  # FIXME: should not be nullable, is until we have all SIRENs filled in the DB

    def give_rights(self, user, rights):
        if user:
            user_offerer = UserOfferer()
            user_offerer.offerer = self
            user_offerer.user = user
            user_offerer.rights = rights
            return user_offerer

    def errors(self):
        api_errors = super(Offerer, self).errors()
        api_errors.errors.update(HasAddressMixin.errors(self).errors)
        if self.siren is not None \
                and (not len(self.siren) == 9):
            # TODO: or not verify_luhn(self.siren)):
            api_errors.add_error('siren', 'Ce code SIREN est invalide')

        return api_errors

    @property
    def bic(self):
        return self.bankInformation.bic if self.bankInformation else None

    @property
    def iban(self):
        return self.bankInformation.iban if self.bankInformation else None

    @property
    def nOffers(self):
        n_offers = 0
        for venue in self.managedVenues:
            n_offers += venue.nOffers
        return n_offers


ts_indexes = [('idx_offerer_fts_name', Offerer.name),
              ('idx_offerer_fts_address', Offerer.address),
              ('idx_offerer_fts_siret', Offerer.siren)]


(Offerer.__ts_vectors__, Offerer.__table_args__) = create_ts_vector_and_table_args(ts_indexes)
