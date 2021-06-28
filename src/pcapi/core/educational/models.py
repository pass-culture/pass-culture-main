from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pcapi.models.db import Model


class EducationalInstitution(Model):
    __tablename__ = "educational_institution"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    institutionId = Column(String(30), nullable=False, unique=True, index=True)


class EducationalYear(Model):
    __tablename__ = "educational_year"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    beginningDate = Column(DateTime, nullable=False)

    expirationDate = Column(DateTime, nullable=False)


class EducationalDeposit(Model):
    __tablename__ = "educational_deposit"
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = Column(BigInteger, ForeignKey("educational_institution.id"), index=True, nullable=True)

    educationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )

    educationalYearId = Column(BigInteger, ForeignKey("educational_year.id"), index=True, nullable=True)

    educationalYear = relationship(EducationalYear, foreign_keys=[educationalYearId], backref="deposits")
