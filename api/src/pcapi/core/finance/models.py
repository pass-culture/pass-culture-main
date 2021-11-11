"""Finance-related models.

In all models, the amount is in euro cents. It is signed:
- a negative amount will be outgoing (payable by us to someone);
- a positive amount will be incoming (payable to us by someone).
"""

import enum

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from pcapi.models.db import Model
import pcapi.utils.db as db_utils


class Frequency(enum.Enum):
    EVERY_TWO_WEEKS = "every two weeks"


class BusinessUnit(Model):
    id = sqla.Column(sqla.BigInteger, primary_key=True, autoincrement=True)
    name = sqla.Column(sqla.Text)
    siret = sqla.Column(sqla.String(14), unique=True)

    bankAccountId = sqla.Column(sqla.BigInteger, sqla.ForeignKey("bank_information.id"), index=True, nullable=True)
    bankAccount = sqla_orm.relationship("BankInformation", foreign_keys=[bankAccountId])

    cashflowFrequency = sqla.Column(db_utils.MagicEnum(Frequency), nullable=False, default=Frequency.EVERY_TWO_WEEKS)
    invoiceFrequency = sqla.Column(db_utils.MagicEnum(Frequency), nullable=False, default=Frequency.EVERY_TWO_WEEKS)
