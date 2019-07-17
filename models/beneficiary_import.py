import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, BigInteger, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from models import PcObject
from models.db import Model


class ImportStatus(enum.Enum):
    DUPLICATE = 'DUPLICATE'
    ERROR = 'ERROR'
    CREATED = 'CREATED'
    REJECTED = 'REJECTED'


class BeneficiaryImport(PcObject, Model):
    demarcheSimplifieeApplicationId = Column(BigInteger,
                                             unique=False,
                                             nullable=False)

    status = Column(Enum(ImportStatus), nullable=False)

    date = Column(DateTime,
                  nullable=False,
                  default=datetime.utcnow)

    detail = Column(String(255), nullable=True)

    beneficiaryId = Column(BigInteger,
                           ForeignKey("user.id"),
                           index=True,
                           nullable=True)

    beneficiary = relationship('User',
                               foreign_keys=[beneficiaryId],
                               backref='beneficiaryImports')
