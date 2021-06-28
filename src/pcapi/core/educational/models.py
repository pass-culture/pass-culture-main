from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pcapi.models.db import Model


class EducationalInstitution(Model):

    __tablename__ = "educational_institution"
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    institutionId = Column(String(30), nullable=False, unique=True, index=True)


class EducationalDeposit(Model):
    __tablename__ = "educational_deposit"
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    educationalInstitutionId = Column(BigInteger, ForeignKey("educational_institution.id"), index=True, nullable=True)

    educationalInstitution = relationship(
        EducationalInstitution, foreign_keys=[educationalInstitutionId], backref="deposits"
    )
