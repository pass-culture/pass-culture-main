from datetime import datetime
from enum import Enum
import typing

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from pcapi.core.users.models import EligibilityType
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    from pcapi.core.users.models import User


class BeneficiaryImportSources(Enum):
    demarches_simplifiees = "demarches_simplifiees"
    jouve = "jouve"
    educonnect = "educonnect"
    ubble = "ubble"


class BeneficiaryImport(PcObject, Base, Model):  # type: ignore [valid-type, misc]
    """
    THIS MODEL IS DEPRECATED - DO NOT USE

    We keep it defined here to keep historical data in the database.
    When this data is either transferred to the new model or deleted, we can remove this model.
    """

    applicationId = sa.Column(sa.BigInteger, nullable=True)

    beneficiaryId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)

    sourceId = sa.Column(sa.Integer, nullable=True)

    source = sa.Column(sa.String(255), nullable=False)

    thirdPartyId = sa.Column(sa.TEXT, nullable=True, index=True)

    eligibilityType = sa.Column(
        sa.Enum(EligibilityType, create_constraint=False),
        nullable=False,
        default=EligibilityType.AGE18,  # TODO (viconnex) remove default values
        server_default=sa.text(EligibilityType.AGE18.name),  # TODO (viconnex) remove default values
    )
    beneficiary = relationship("User", foreign_keys=[beneficiaryId], backref="beneficiaryImports")  # type: ignore [misc]

    def setStatus(self, status: ImportStatus, detail: str = None, author: "User" = None):  # type: ignore [no-untyped-def]
        new_status = BeneficiaryImportStatus()
        new_status.status = status
        new_status.detail = detail
        new_status.date = datetime.utcnow()
        new_status.author = author  # type: ignore [assignment]

        self.statuses.append(new_status)

    @hybrid_property
    def currentStatus(self):
        return self._last_status().status

    @currentStatus.expression  # type: ignore [no-redef]
    def currentStatus(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.status)

    @hybrid_property
    def updatedAt(self):
        return self._last_status().date

    @updatedAt.expression  # type: ignore [no-redef]
    def updatedAt(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.date)

    @hybrid_property
    def detail(self):
        return self._last_status().detail

    @detail.expression  # type: ignore [no-redef]
    def detail(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.detail)

    @hybrid_property
    def authorEmail(self):
        author = self._last_status().author
        return author.email or None

    @authorEmail.expression  # type: ignore [no-redef]
    def authorEmail(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.author)

    @property
    def history(self):  # type: ignore [no-untyped-def]
        return "\n".join([repr(s) for s in self.statuses])

    def get_detailed_source(self) -> str:
        if self.source == BeneficiaryImportSources.demarches_simplifiees.value:
            return f"démarches simplifiées dossier [{self.applicationId}]"
        # TODO(viconnex): implement source for educonnect
        return f"dossier {self.source} [{self.applicationId}]"

    @classmethod
    def _query_last_status(cls, column: sa.Column):  # type: ignore [no-untyped-def]
        return (
            db.session.query(column)
            .filter(BeneficiaryImportStatus.beneficiaryImportId == cls.id)
            .order_by(sa.desc(BeneficiaryImportStatus.date))
            .limit(1)
            .as_scalar()
        )

    def _last_status(self):  # type: ignore [no-untyped-def]
        return sorted(self.statuses, key=lambda x: x.date, reverse=True)[0]
