"""Recreate column special_event.eventDate as DATE NOT NULL"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "bfd459b4a913"
down_revision = "138018be9e5a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("special_event", "eventDate")
    op.add_column(
        "special_event",
        sa.Column(
            "eventDate",
            sa.Date(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_special_event_eventDate"),
            "special_event",
            ["eventDate"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.drop_column("special_event", "eventDate")
    op.add_column(
        "special_event",
        sa.Column(
            "eventDate",
            sa.DateTime(),
            nullable=True,
        ),
    )
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_special_event_eventDate"),
            "special_event",
            ["eventDate"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
