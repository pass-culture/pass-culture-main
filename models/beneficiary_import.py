from datetime import datetime

from sqlalchemy import BigInteger, Column, ForeignKey, desc, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from models.beneficiary_import_status import BeneficiaryImportStatus, \
    ImportStatus
from models.db import Model, db
from models.pc_object import PcObject
from models.user import User


class BeneficiaryImport(PcObject, Model):
    demarcheSimplifieeApplicationId = Column(BigInteger,
                                             unique=True,
                                             nullable=False)

    beneficiaryId = Column(BigInteger,
                           ForeignKey("user.id"),
                           index=True,
                           nullable=True)

    demarcheSimplifieeProcedureId = Column(Integer, nullable=True)

    beneficiary = relationship('User',
                               foreign_keys=[beneficiaryId],
                               backref='beneficiaryImports')

    def setStatus(self, status: ImportStatus, detail: str = None, author: User = None):
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
