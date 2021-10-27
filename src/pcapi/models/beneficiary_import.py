from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.pc_object import PcObject


class BeneficiaryImportSources(Enum):
    demarches_simplifiees = "demarches_simplifiees"
    jouve = "jouve"


class BeneficiaryImport(PcObject, Model):
    applicationId = sa.Column(sa.BigInteger, nullable=False)

    beneficiaryId = sa.Column(sa.BigInteger, sa.ForeignKey("user.id"), index=True, nullable=True)

    sourceId = sa.Column(sa.Integer, nullable=True)

    source = sa.Column(sa.String(255), nullable=False)

    beneficiary = relationship("User", foreign_keys=[beneficiaryId], backref="beneficiaryImports")

    eligibilityType = sa.Column(
        sa.Enum(EligibilityType, create_constraint=False),
        nullable=False,
        default=EligibilityType.AGE18,
        server_default=sa.text(EligibilityType.AGE18.value),
    )

    sa.Index(
        "idx_beneficiary_import_application",
        applicationId,
        sourceId,
        source,
        unique=True,
    )

    def setStatus(self, status: ImportStatus, detail: str = None, author: User = None):
        new_status = BeneficiaryImportStatus()
        new_status.status = status
        new_status.detail = detail
        new_status.date = datetime.utcnow()
        new_status.author = author

        self.statuses.append(new_status)

    @hybrid_property
    def currentStatus(self):
        return self._last_status().status

    @currentStatus.expression
    def currentStatus(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.status)

    @hybrid_property
    def updatedAt(self):
        return self._last_status().date

    @updatedAt.expression
    def updatedAt(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.date)

    @hybrid_property
    def detail(self):
        return self._last_status().detail

    @detail.expression
    def detail(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.detail)

    @hybrid_property
    def authorEmail(self):
        author = self._last_status().author
        return author.email or None

    @authorEmail.expression
    def authorEmail(cls):  # pylint: disable=no-self-argument
        return cls._query_last_status(BeneficiaryImportStatus.author)

    @property
    def history(self):
        return "\n".join([repr(s) for s in self.statuses])

    def get_detailed_source(self) -> str:
        if self.source == BeneficiaryImportSources.demarches_simplifiees.value:
            return f"démarches simplifiées dossier [{self.applicationId}]"
        # TODO(viconnex): implement source for educonnect
        return f"dossier {self.source} [{self.applicationId}]"

    @classmethod
    def _query_last_status(cls, column: sa.Column):
        return (
            db.session.query(column)
            .filter(BeneficiaryImportStatus.beneficiaryImportId == cls.id)
            .order_by(sa.desc(BeneficiaryImportStatus.date))
            .limit(1)
            .as_scalar()
        )

    def _last_status(self):
        return sorted(self.statuses, key=lambda x: x.date, reverse=True)[0]
