"""SQLAlchemy model for the PokeTodo experimental entity."""

import datetime
import enum

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class PokeTodoPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PokeTodo(PcObject, Model):
    __tablename__ = "poke_todo"

    title: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(255), nullable=False)
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    priority: sa_orm.Mapped[PokeTodoPriority] = sa_orm.mapped_column(
        sa.Enum(PokeTodoPriority, native_enum=False, create_constraint=False),
        nullable=False,
        default=PokeTodoPriority.LOW,
        server_default=PokeTodoPriority.LOW.value,
    )
    due_date: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    is_completed: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=sa.sql.expression.false()
    )
    date_created: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    date_updated: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
