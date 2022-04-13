import sqlalchemy as sqla

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class Criterion(PcObject, Model):  # type: ignore [valid-type, misc]
    name = sqla.Column(sqla.String(140), nullable=False, unique=True)
    description = sqla.Column(sqla.Text, nullable=True)
    startDateTime = sqla.Column(sqla.DateTime, nullable=True)
    endDateTime = sqla.Column(sqla.DateTime, nullable=True)

    def __str__(self) -> str:
        return self.name
