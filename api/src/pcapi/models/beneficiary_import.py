import typing
from enum import Enum

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import relationship

from pcapi.core.users.models import EligibilityType
from pcapi.models import Model
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    from pcapi.core.users.models import User


class BeneficiaryImportSources(Enum):
    demarches_simplifiees = "demarches_simplifiees"
    jouve = "jouve"
    educonnect = "educonnect"
    ubble = "ubble"


class BeneficiaryImport(PcObject, Model):
    """
    THIS MODEL IS DEPRECATED - DO NOT USE

    We keep it defined here to keep historical data in the database.
    When this data is either transferred to the new model or deleted, we can remove this model.
    """

    __tablename__ = "beneficiary_import"
    applicationId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.BigInteger, nullable=True)

    sourceId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(sa.Integer, nullable=True)

    source: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)

    thirdPartyId: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.TEXT, nullable=True, index=True)

    eligibilityType: sa_orm.Mapped[EligibilityType] = sa_orm.mapped_column(
        sa.Enum(EligibilityType, create_constraint=False),
        nullable=False,
        default=EligibilityType.AGE18,
        server_default=sa.text(EligibilityType.AGE18.name),
    )

    beneficiaryId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True
    )
    beneficiary: sa_orm.Mapped["User | None"] = relationship(
        "User", foreign_keys=[beneficiaryId], back_populates="beneficiaryImports"
    )

    statuses: sa_orm.Mapped[list["BeneficiaryImportStatus"]] = relationship(
        "BeneficiaryImportStatus",
        foreign_keys="BeneficiaryImportStatus.beneficiaryImportId",
        back_populates="beneficiaryImport",
    )

    def get_detailed_source(self) -> str:
        if self.source == BeneficiaryImportSources.demarches_simplifiees.value:
            return f"démarches simplifiées dossier [{self.applicationId}]"
        return f"dossier {self.source} [{self.applicationId}]"
