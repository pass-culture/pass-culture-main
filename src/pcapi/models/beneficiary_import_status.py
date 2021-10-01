from datetime import datetime
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class ImportStatus(enum.Enum):
    DRAFT = "DRAFT"
    ONGOING = "ONGOING"
    DUPLICATE = "DUPLICATE"
    ERROR = "ERROR"
    CREATED = "CREATED"
    REJECTED = "REJECTED"
    RETRY = "RETRY"
    WITHOUT_CONTINUATION = "WITHOUT_CONTINUATION"


class BeneficiaryImportStatus(PcObject, Model):
    def __repr__(self):
        author = self.author.publicName if self.author else "import automatisé"
        updated_at = datetime.strftime(self.date, "%d/%m/%Y")
        return f"{self.status.value}, le {updated_at} par {author}"

    status = Column(Enum(ImportStatus, create_constraint=False), nullable=False)

    date = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    detail = Column(String(255), nullable=True)

    beneficiaryImportId = Column(BigInteger, ForeignKey("beneficiary_import.id"), index=True, nullable=False)

    beneficiaryImport = relationship("BeneficiaryImport", foreign_keys=[beneficiaryImportId], backref="statuses")

    authorId = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    author = relationship("User", foreign_keys=[authorId])
