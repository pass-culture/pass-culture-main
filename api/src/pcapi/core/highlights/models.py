import typing

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql

from pcapi import settings
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    pass


class Highlight(PcObject, Base, Model):
    __tablename__ = "highlight"

    name: sa_orm.Mapped[str] = sa.Column(sa.Text, nullable=False)
    description: sa_orm.Mapped[str] = sa.Column("description", sa.Text, nullable=False)
    availability_timespan: sa_orm.Mapped[psycopg2.extras.DateTimeRange] = sa.Column(postgresql.TSRANGE, nullable=False)
    highlight_timespan: sa_orm.Mapped[psycopg2.extras.DateTimeRange] = sa.Column(postgresql.TSRANGE, nullable=False)
    mediation_uuid: sa_orm.Mapped[str] = sa.Column(sa.Text, nullable=False, unique=True)

    @property
    def mediation_url(self) -> str:
        return f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{self.uuid}"

    __table_args__ = (
        sa.CheckConstraint('length("name") <= 200'),
        sa.CheckConstraint('length("mediation_uuid") <= 100'),
        sa.CheckConstraint('length("description") <= 2000'),
    )
