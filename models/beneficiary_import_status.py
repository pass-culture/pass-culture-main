import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, BigInteger, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from models.pc_object import PcObject
from models.db import Model


class ImportStatus(enum.Enum):
    DUPLICATE = 'DUPLICATE'
    ERROR = 'ERROR'
    CREATED = 'CREATED'
    REJECTED = 'REJECTED'


class BeneficiaryImportStatus(PcObject, Model):
    status = Column(Enum(ImportStatus), nullable=False)

    date = Column(DateTime,
                  nullable=False,
                  default=datetime.utcnow)

    detail = Column(String(255), nullable=True)

    beneficiaryImportId = Column(BigInteger,
                                 ForeignKey("beneficiary_import.id"),
                                 index=True,
                                 nullable=False)

    beneficiaryImport = relationship('BeneficiaryImport',
                                     foreign_keys=[beneficiaryImportId],
                                     backref='statuses')
