from datetime import datetime
import enum
import typing

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import relationship

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    import pcapi.core.users.models as users_models
    from pcapi.models.beneficiary_import import BeneficiaryImport


class ImportStatus(enum.Enum):
    DRAFT = "DRAFT"
    ONGOING = "ONGOING"
    DUPLICATE = "DUPLICATE"
    ERROR = "ERROR"
    CREATED = "CREATED"
    REJECTED = "REJECTED"
    RETRY = "RETRY"
    WITHOUT_CONTINUATION = "WITHOUT_CONTINUATION"


class BeneficiaryImportStatus(PcObject, Base, Model):
    """
    THIS MODEL IS DEPRECATED - DO NOT USE

    We keep it defined here to keep historical data in the database.
    When this data is either transferred to the new model or deleted, we can remove this model.
    """

    def __repr__(self) -> str:
        author = self.author.full_name if self.author else "import automatisé"
        updated_at = datetime.strftime(self.date, "%d/%m/%Y")
        return f"{self.status.value}, le {updated_at} par {author}"

    status: ImportStatus = Column(Enum(ImportStatus, create_constraint=False), nullable=False)

    date: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, server_default=func.now())

    detail = Column(String(255), nullable=True)

    beneficiaryImportId: int = Column(BigInteger, ForeignKey("beneficiary_import.id"), index=True, nullable=False)

    beneficiaryImport: sa_orm.Mapped["BeneficiaryImport"] = relationship(
        "BeneficiaryImport", foreign_keys=[beneficiaryImportId], back_populates="statuses"
    )

    authorId = Column(BigInteger, ForeignKey("user.id"), nullable=True)

    author: sa_orm.Mapped["users_models.User | None"] = relationship("User", foreign_keys=[authorId])
