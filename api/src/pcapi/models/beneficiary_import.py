from enum import Enum
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import relationship

from pcapi.core.users.models import EligibilityType
from pcapi.models import Base
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


class BeneficiaryImport(PcObject, Base, Model):
    """
    THIS MODEL IS DEPRECATED - DO NOT USE

    We keep it defined here to keep historical data in the database.
    When this data is either transferred to the new model or deleted, we can remove this model.
    """

    applicationId = sa.Column(sa.BigInteger, nullable=True)

    beneficiaryId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)

    sourceId = sa.Column(sa.Integer, nullable=True)

    source: str = sa.Column(sa.String(255), nullable=False)

    thirdPartyId = sa.Column(sa.TEXT, nullable=True, index=True)

    eligibilityType: EligibilityType = sa.Column(
        sa.Enum(EligibilityType, create_constraint=False),
        nullable=False,
        default=EligibilityType.AGE18,  # TODO (viconnex) remove default values
        server_default=sa.text(EligibilityType.AGE18.name),  # TODO (viconnex) remove default values
    )
    beneficiary: sa_orm.Mapped["User"] = relationship(
        "User", foreign_keys=[beneficiaryId], backref="beneficiaryImports"
    )

    @property
    def currentStatus(self):
        return self._last_status().status

    @property
    def updatedAt(self):
        return self._last_status().date

    @property
    def detail(self):
        return self._last_status().detail

    @property
    def authorEmail(self):
        author = self._last_status().author
        return author.email or None

    @property
    def history(self) -> str:
        return "\n".join([repr(s) for s in self.statuses])

    def get_detailed_source(self) -> str:
        if self.source == BeneficiaryImportSources.demarches_simplifiees.value:
            return f"démarches simplifiées dossier [{self.applicationId}]"
        # TODO(viconnex): implement source for educonnect
        return f"dossier {self.source} [{self.applicationId}]"

    def _last_status(self) -> BeneficiaryImportStatus:
        return sorted(self.statuses, key=lambda x: x.date, reverse=True)[0]
