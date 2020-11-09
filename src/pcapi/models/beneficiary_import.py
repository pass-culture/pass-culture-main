from datetime import datetime
from enum import Enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import desc
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from pcapi.models.beneficiary_import_status import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.models.db import Model
from pcapi.models.db import db
from pcapi.models.pc_object import PcObject
from pcapi.models.user_sql_entity import UserSQLEntity


class BeneficiaryImportSources(Enum):
    demarches_simplifiees = 'demarches_simplifiees'
    jouve = 'jouve'


class BeneficiaryImport(PcObject, Model):
    applicationId = Column(BigInteger,
                           nullable=False)

    beneficiaryId = Column(BigInteger,
                           ForeignKey('user.id'),
                           index=True,
                           nullable=True)

    sourceId = Column(Integer, nullable=True)

    source = Column(String(255), nullable=False)

    beneficiary = relationship('UserSQLEntity',
                               foreign_keys=[beneficiaryId],
                               backref='beneficiaryImports')

    def setStatus(self, status: ImportStatus, detail: str = None, author: UserSQLEntity = None):
        new_status = BeneficiaryImportStatus()
        new_status.status = status
        new_status.detail = detail
        new_status.date = datetime.utcnow()
        new_status.author = author

        if self.statuses:
            self.statuses.append(new_status)
        else:
            self.statuses = [new_status]

    @hybrid_property
    def currentStatus(self):
        return self._last_status().status

    @currentStatus.expression
    def currentStatus(cls):
        return cls._query_last_status(BeneficiaryImportStatus.status)

    @hybrid_property
    def updatedAt(self):
        return self._last_status().date

    @updatedAt.expression
    def updatedAt(cls):
        return cls._query_last_status(BeneficiaryImportStatus.date)

    @hybrid_property
    def detail(self):
        return self._last_status().detail

    @detail.expression
    def detail(cls):
        return cls._query_last_status(BeneficiaryImportStatus.detail)

    @hybrid_property
    def authorEmail(self):
        author = self._last_status().author
        return author.email or None

    @authorEmail.expression
    def authorEmail(cls):
        return cls._query_last_status(BeneficiaryImportStatus.author)

    @property
    def history(self):
        return '\n'.join([repr(s) for s in self.statuses])

    @classmethod
    def _query_last_status(cls, column: Column):
        return db.session \
            .query(column) \
            .filter(BeneficiaryImportStatus.beneficiaryImportId == cls.id) \
            .order_by(desc(BeneficiaryImportStatus.date)) \
            .limit(1) \
            .as_scalar()

    def _last_status(self):
        return sorted(self.statuses, key=lambda x: x.date, reverse=True)[0]
