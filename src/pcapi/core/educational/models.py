from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import String

from pcapi.models.db import Model


class EducationalInstitution(Model):
    __tablename__ = "educational_institution"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    institutionId = Column(String(30), nullable=False, unique=True, index=True)
