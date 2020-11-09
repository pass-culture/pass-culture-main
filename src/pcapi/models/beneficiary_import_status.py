from datetime import datetime
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class ImportStatus(enum.Enum):
    DUPLICATE = 'DUPLICATE'
    ERROR = 'ERROR'
    CREATED = 'CREATED'
    REJECTED = 'REJECTED'
    RETRY = 'RETRY'


class BeneficiaryImportStatus(PcObject, Model):
    def __repr__(self):
        author = self.author.publicName if self.author else 'import automatisé'
        updated_at = datetime.strftime(self.date, '%d/%m/%Y')
        return f"{self.status.value}, le {updated_at} par {author}"

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

    authorId = Column(BigInteger,
                      ForeignKey("user.id"),
                      nullable=True)

    author = relationship('UserSQLEntity',
                          foreign_keys=[authorId])
